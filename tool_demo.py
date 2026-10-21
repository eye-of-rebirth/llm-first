"""第一个工具调用：模型自己决定要不要用工具。

运行：uv run tool_demo.py
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


# ========== 第一步：定义真实函数（在你的电脑上执行）==========
def get_weather(city: str) -> str:
    """查询城市天气（用假数据演示）"""
    fake = {
        "北京": "晴天，25度，微风",
        "上海": "多云，28度",
        "深圳": "雷阵雨，30度",
    }
    return fake.get(city, f"查不到 {city} 的天气")


# ========== 第二步：用"说明书"格式描述这个函数 ==========
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "查询指定城市的实时天气情况",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "城市名称，例如：北京、上海",
                    }
                },
                "required": ["city"],
            },
        },
    }
]

# ========== 第三步：把问题和工具一起发给模型 ==========
messages = [{"role": "user", "content": "北京今天天气怎么样？"}]

response = client.chat.completions.create(
    model="deepseek-chat",
    messages=messages,
    tools=tools,          # ← 关键：把工具清单告诉模型
)

message = response.choices[0].message

print("模型返回的内容：", message.content)
print("模型想调用的工具：", message.tool_calls)

if message.tool_calls:
    tool_call = message.tool_calls[0]
    func_name = tool_call.function.name
    func_args = json.loads(tool_call.function.arguments or "{}")

    print(f"\n>>> 模型请求调用：{func_name}")
    print(f">>> 参数：{func_args}")

    # ========== 第四步：你自己执行这个函数 ==========
    if func_name == "get_weather":
        result = get_weather(**func_args)
        print(f">>> 我们执行的结果：{result}")

        # ========== 第五步：把结果塞回对话，再问一次模型 ==========
        messages.append(message)          # 模型的调用请求
        messages.append({                 # 我们的执行结果
            "role": "tool",
            "tool_call_id": tool_call.id,
            "content": result,
        })

        final = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            tools=tools,
        )
        print(f"\n>>> 模型最终回答：{final.choices[0].message.content}")