"""
MioConfig CLI — 对话 + 配置的最小原型
验证「配置 = 文本注入 + 验证钩子」这个模型
"""

import json, os, sys
from pathlib import Path

import httpx

CONFIG_FILE = Path(__file__).parent / "config.json"
LLM_API_KEY = os.environ.get("DEEPSEEK_API_KEY", "")
LLM_BASE = "https://api.deepseek.com/v1"


# ── 配置管理层 ────────────────────────────────────

def load_config() -> dict:
    if CONFIG_FILE.exists():
        return json.loads(CONFIG_FILE.read_text("utf-8"))
    return {
        "思维链": "",
        "拦截格式": "",
    }


def save_config(config: dict):
    CONFIG_FILE.write_text(json.dumps(config, ensure_ascii=False, indent=2), "utf-8")


def build_system_prompt(config: dict) -> str:
    """配置注入 system prompt —— 蓝图里 BUILD 阶段做的事"""
    parts = ["你是一个 AI 助手。\n"]

    if config.get("思维链"):
        parts.append("## 思考步骤\n")
        parts.append("请在每次回复前严格按以下步骤思考：\n")
        parts.append(config["思维链"])
        parts.append("\n")

    return "".join(parts)


async def self_check(first_reply: str, check_rules: str) -> str:
    """
    自检回环 —— 拦下来 → 发固定提示词 → PASS / 修正
    """
    if not check_rules.strip():
        return first_reply

    rules_block = check_rules.strip()

    check_prompt = (
        f"以下是你刚刚给用户的回复：\n"
        f"---\n{first_reply}\n---\n\n"
        f"请按以下规则逐条自查：\n{rules_block}\n\n"
        f"规则：\n"
        f"1. 全部符合 → 只输出 PASS（一个字都不许多）\n"
        f"2. 有一条不符合 → 直接输出修正后的完整回复，不许加任何解释、不许说'修正版如下'、不许分析哪里错了"
    )

    # 单次流式调用
    print("\n── [自检] ──")
    result = await stream_llm(
        [{"role": "user", "content": check_prompt}],
        temperature=0.2,
        label="",
    )

    if result.strip().upper() == "PASS":
        print("── [自检] 通过 ──")
        return first_reply
    else:
        print("── [结果] ──")
        return result


# ── LLM 调用层 ────────────────────────────────────

async def stream_llm(messages: list[dict], temperature: float = 0.7, label: str = ""):
    """
    流式调用 LLM，逐 chunk 打印，爸爸能看到整个过程。
    返回完整回复文本。
    """
    header = f"[{label}] " if label else ""

    async with httpx.AsyncClient(timeout=120) as c:
        async with c.stream(
            "POST",
            f"{LLM_BASE}/chat/completions",
            headers={
                "Authorization": f"Bearer {LLM_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": "deepseek-v4-flash",
                "messages": messages,
                "temperature": temperature,
                "stream": True,
            },
        ) as r:
            r.raise_for_status()
            full = []
            async for line in r.aiter_lines():
                if line.startswith("data: "):
                    chunk = line[6:]
                    if chunk == "[DONE]":
                        break
                    try:
                        delta = json.loads(chunk)["choices"][0].get("delta", {})
                        content = delta.get("content", "")
                        if content:
                            print(content, end="", flush=True)
                            full.append(content)
                    except (json.JSONDecodeError, KeyError, IndexError):
                        pass
            print()  # 换行
            return "".join(full)


# ── UI 层 ─────────────────────────────────────────

def print_banner(config: dict):
    print("\033[2J\033[H", end="")  # 清屏
    print("╔══════════════════════════════════════╗")
    print("║        MioConfig · 配置原型          ║")
    print("╠══════════════════════════════════════╣")
    chain_on = "[ON]" if config.get("思维链") else "[OFF]"
    check_on = "[ON]" if config.get("拦截格式") else "[OFF]"
    print(f"║  思维链: {chain_on}   拦截: {check_on}                   ║")
    print("╠══════════════════════════════════════╣")
    print("║  /config  配置    /clear  清上下文    ║")
    print("║  /quit    退出    /help   帮助       ║")
    print("╚══════════════════════════════════════╝")
    print()


def config_panel(config: dict):
    """配置面板 —— 爸爸说的「选项框」"""
    while True:
        print("\n┌── 配置面板 ──────────────────────┐")
        print("│  1. 思维链 (自定义思考步骤)       │")
        print("│  2. 拦截格式 (回复验证规则)       │")
        print("│  3. 返回                          │")
        print("└────────────────────────────────────┘")
        choice = input("选 > ").strip()

        if choice == "1":
            print(f"\n当前思维链:\n{config['思维链'] or '(空)'}")
            print("\n输入新内容 (空行结束，. 清空):")
            lines = []
            while True:
                line = input()
                if line == "":
                    break
                if line == ".":
                    lines = []
                    break
                lines.append(line)
            if lines:
                config["思维链"] = "\n".join(lines)
            elif not lines:
                config["思维链"] = ""
            save_config(config)

        elif choice == "2":
            print(f"\n当前拦截格式:\n{config['拦截格式'] or '(空)'}")
            print("\n输入新内容 (空行结束，. 清空):")
            lines = []
            while True:
                line = input()
                if line == "":
                    break
                if line == ".":
                    lines = []
                    break
                lines.append(line)
            if lines:
                config["拦截格式"] = "\n".join(lines)
            elif not lines:
                config["拦截格式"] = ""
            save_config(config)

        elif choice == "3":
            return
        else:
            print("无效选项")


async def main():
    config = load_config()
    messages = []  # 对话历史

    while True:
        print_banner(config)
        user_input = input("[你] > ").strip()

        if not user_input:
            continue

        if user_input.startswith("/quit"):
            print("再见~")
            break

        if user_input == "/config":
            config_panel(config)
            continue

        if user_input == "/clear":
            messages = []
            print("✓ 上下文已清空")
            input("按回车继续...")
            continue

        if user_input == "/help":
            print("""
/chat     跟 LLM 对话（默认模式，直接输入文字即可）
/config   打开配置面板 ┬ 思维链 (自定义 LLM 思考步骤)
           (选项框)     └ 拦截格式 (回复后验证规则)
/clear    清空对话上下文
/quit     退出

配置说明:
  思维链  → BUILD 阶段注入 system prompt，强制 LLM 按步骤思考
  拦截格式 → POST_THINK 阶段检查回复是否合规，违规则提醒用户
            """)
            input("按回车继续...")
            continue

        # ── 对话模式 ──
        system_prompt = build_system_prompt(config)

        api_messages = [{"role": "system", "content": system_prompt}]
        api_messages.extend(messages)
        api_messages.append({"role": "user", "content": user_input})

        try:
            # 第一轮：流式输出
            print("── [回复] ──")
            first_reply = await stream_llm(api_messages, label="")

            # ── 自检回环 ──
            check_rules = config.get("拦截格式", "")
            if check_rules.strip():
                final_reply = await self_check(first_reply, check_rules)
            else:
                final_reply = first_reply

            messages.append({"role": "user", "content": user_input})
            messages.append({"role": "assistant", "content": final_reply})

        except Exception as e:
            print(f"\n[错误] {e}")

        input("\n按回车继续...")


if __name__ == "__main__":
    import asyncio

    if not LLM_API_KEY:
        print("请设置环境变量 DEEPSEEK_API_KEY")
        sys.exit(1)

    asyncio.run(main())
