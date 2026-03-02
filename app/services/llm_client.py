"""
功能说明（中文）：
1. 对接 DashScope OpenAI 兼容接口（/chat/completions）。
2. 将系统提示词和用户输入发送给模型，拿回结构化 JSON 结果。
3. 自动处理部分模型对 response_format 参数不兼容的问题（400 时自动降级重试）。

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

    def _extract_content(self, response_json: dict[str, Any]) -> str:
        choices = response_json.get("choices", [])
        if not choices:
            raise ValueError(f"模型返回缺少 choices: {response_json}")

        message = choices[0].get("message", {})
        content = message.get("content", "")

        # 兼容部分兼容层把 content 返回为 list 的情况
        if isinstance(content, list):
            text_chunks: list[str] = []
            for part in content:
                if isinstance(part, dict) and part.get("type") == "text":
                    text_chunks.append(str(part.get("text", "")))
                else:
                    text_chunks.append(str(part))
            return "".join(text_chunks)
        return str(content)

    @staticmethod
    def _loads_json_maybe_markdown(text: str) -> dict[str, Any]:
        raw = text.strip()
        # 兼容 ```json ... ``` 输出
        if raw.startswith("```"):
            raw = raw.strip("`")
            raw = raw.replace("json\n", "", 1).strip()
        return json.loads(raw)

    def _request(self, headers: dict[str, str], payload: dict[str, Any]) -> dict[str, Any]:
        resp = requests.post(
            self.endpoint,
            headers=headers,
            json=payload,
            timeout=self.settings.timeout,
        )

        # 为排障提供更明确错误
        if not resp.ok:
            raise requests.HTTPError(
                f"{resp.status_code} {resp.reason} for url: {resp.url}; body={resp.text}",
                response=resp,
            )

        data = resp.json()
        content = self._extract_content(data)
        return self._loads_json_maybe_markdown(content)

    def chat_json(self, system_prompt: str, user_prompt: str) -> dict[str, Any]:
        headers = {
            "Authorization": f"Bearer {self.settings.api_key}",
            "Content-Type": "application/json",
        }

        base_payload = {
            "model": self.settings.model_name,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "max_tokens": self.settings.max_tokens,
            "temperature": 0.1,
        }

        # 第一轮：优先 JSON 模式
        first_payload = {**base_payload, "response_format": {"type": "json_object"}}
        try:
            return self._request(headers, first_payload)
        except requests.HTTPError as exc:
            # DashScope 某些模型可能不支持 response_format，400 时降级重试
            if exc.response is None or exc.response.status_code != 400:
                raise

        # 第二轮：不带 response_format，再靠 prompt 约束 + 本地 JSON 解析
        return self._request(headers, base_payload)
