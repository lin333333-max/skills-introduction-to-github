"""
功能说明（中文）：
1. 对接 DashScope OpenAI 兼容接口（/chat/completions）。
2. 将系统提示词和用户输入发送给模型，拿回结构化 JSON 结果。
3. 如果后续更换模型供应商，可在本文件适配。

命令示例（Windows PowerShell）：
1. 安装依赖：
   pip install -r requirements.txt
2. 运行接口：
   uvicorn app.main:app --host 0.0.0.0 --port 8000
"""

from __future__ import annotations

import json
from typing import Any

import requests

from app.config import LLMSettings


class LLMClient:
    def __init__(self, settings: LLMSettings):
        self.settings = settings
        self.endpoint = settings.base_url.rstrip("/") + "/chat/completions"

    def chat_json(self, system_prompt: str, user_prompt: str) -> dict[str, Any]:
        headers = {
            "Authorization": f"Bearer {self.settings.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.settings.model_name,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "max_tokens": self.settings.max_tokens,
            "temperature": 0.1,
            "response_format": {"type": "json_object"},
        }

        resp = requests.post(
            self.endpoint,
            headers=headers,
            json=payload,
            timeout=self.settings.timeout,
        )
        resp.raise_for_status()
        data = resp.json()
        content = data["choices"][0]["message"]["content"]
        return json.loads(content)
