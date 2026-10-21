"""第一个大模型调用程序。

运行：uv run first_call.py
"""

import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()  # 从 .env 读环境变量

client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com",
)

response = client.chat.completions.create(
    model="deepseek-chat",
    messages=[
        {"role": "user", "content": "用一句话解释什么是编程"},
    ],
)

print(response.choices[0].message.content)