# llm-first

学习大模型 API 调用的第一个项目。

## 环境要求

- Python 3.12+
- uv（依赖管理）

## 运行方式

1. 复制 `.env.example` 为 `.env`，填入你的 API Key
2. `uv sync`
3. `uv run first_call.py`（或 `stream_demo.py`）

## 文件说明

- `first_call.py` —— 基础对话调用
- `stream_demo.py` —— 流式输出

## 学习笔记

- `messages` 数组是对话历史，模型本身**无状态**
- `temperature` 控制随机性（0 = 确定，1.5+ = 有创意）
- 流式输出基于 **SSE** 协议