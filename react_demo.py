"""ReAct 循环：模型可以连续调用多个工具。

运行：uv run react_demo.py
"""

import json
import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com",
)


# ========== 工具 1：天气 ==========
def get_weather(city: str) -> str:
    """查询城市天气"""
    data = {"北京": "晴天，25度", "上海": "多云，28度", "深圳": "雷阵雨，30度"}
    return data.get(city, f"查不到 {city} 的天气")


# ========== 工具 2：计算器 ==========
def calculate(expression: str) -> str:
    """计算数学表达式，例如 '2 + 3 * 4'"""
    try:
        allowed = set("0123456789+-*/(). ")
        if not set(expression) <= allowed:
            return "表达式包含不允许的字符"
        return str(eval(expression))       # 仅用于学习演示
    except Exception as e:
        return f"计算失败：{e}"


# ========== 工具说明书 ==========
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "查询指定城市的实时天气情况",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {"type": "string", "description": "城市名称"}
                },
                "required": ["city"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "calculate",
            "description": "计算数学表达式，支持加减乘除和括号",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "数学表达式，如 '2 + 3 * 4'",
                    }
                },
                "required": ["expression"],
            },
        },
    },
]

# 工具名 → 真实函数的映射表
TOOL_MAP = {
    "get_weather": get_weather,
    "calculate": calculate,
}


def run_agent(user_input: str, max_turns: int = 5):
    """跑一个 ReAct 循环"""
    messages = [{"role": "user", "content": user_input}]

    for turn in range(max_turns):
        print(f"\n--- 第 {turn + 1} 轮 ---")

        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            tools=tools,
        )
        message = response.choices[0].message

        # 情况 A：模型不需要工具，直接回答 → 结束
        if not message.tool_calls:
            print(f"最终回答：{message.content}")
            return message.content

        # 情况 B：模型要调工具 → 执行，把结果塞回去，继续下一轮
        messages.append(message)

        for tool_call in message.tool_calls:
            name = tool_call.function.name
            args = json.loads(tool_call.function.arguments or "{}")
            print(f">>> 调用工具：{name}({args})")

            func = TOOL_MAP.get(name)
            result = func(**args) if func else f"未知工具：{name}"
            print(f">>> 结果：{result}")

            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": str(result),
            })

    print("达到最大轮数，强制结束")
    return None


if __name__ == "__main__":
    # 测试 1：单工具
    run_agent("北京今天天气怎么样？")

    # 测试 2：需要多步（先算数，再报天气）
    run_agent("帮我算一下 (25 + 30) * 2 等于多少，另外深圳天气如何？")