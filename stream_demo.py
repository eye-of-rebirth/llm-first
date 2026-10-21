"""流式输出：文字逐字吐出来。

运行：uv run stream_demo.py
"""

import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com",
)

stream = client.chat.completions.create(
    model="deepseek-chat",
    messages=[{"role": "user", "content": "讲一个关于程序员的笑话"}],
    stream=True,          # ← 唯一的改动
)

for chunk in stream:
    content = chunk.choices[0].delta.content
    if content:            # 有些 chunk 是空的，要判断
        print(content, end="", flush=True)

print()