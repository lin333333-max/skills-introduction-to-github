"""
功能说明（中文）：
1. 组合“法律库加载 + 大模型分析”流程。
2. 根据犯罪行为，从法律条文中筛选并输出结构化结果。
3. 统一在这里构造 prompt，方便后续优化分析策略。

命令示例（Windows PowerShell）：
1. 本地调试后端：
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
2. 请求测试：
   curl -X POST "http://127.0.0.1:8000/analyze" -H "Content-Type: application/json" -d "{\"action\":\"诈骗他人钱财\"}"
"""

from __future__ import annotations

import json
from typing import Any

from app.schemas import AnalyzeResponse, MatchedLawItem
from app.services.law_repository import LawRepository
from app.services.llm_client import LLMClient


class LawAnalyzer:
    def __init__(self, law_repo: LawRepository, llm_client: LLMClient):
        self.law_repo = law_repo
        self.llm_client = llm_client

    def analyze(self, action: str) -> AnalyzeResponse:
        laws = self.law_repo.load_laws()
        system_prompt = self._build_system_prompt()
        user_prompt = self._build_user_prompt(action, laws)
        raw = self.llm_client.chat_json(system_prompt, user_prompt)
        return self._parse_response(action, raw)

    @staticmethod
    def _build_system_prompt() -> str:
        return (
            "你是一名严谨的中国法律分析助手。"
            "你只能根据用户给出的法律库进行分析，不要编造法律。"
            "输出必须是 JSON 对象，格式如下："
            "{\"matches\":[{\"law_name\":\"\",\"law_id\":\"\",\"article_id\":\"\",\"analysis\":\"\"}]}。"
            "analysis 要清楚说明该行为为什么触犯该法条。"
        )

    @staticmethod
    def _build_user_prompt(action: str, laws: list[dict[str, Any]]) -> str:
        return (
            f"犯罪行为：{action}\n\n"
            "以下是法律库（JSON）：\n"
            f"{json.dumps(laws, ensure_ascii=False)}\n\n"
            "请从中找出可能涉及的法律和法条，并给出分析。"
        )

    @staticmethod
    def _parse_response(action: str, raw: dict[str, Any]) -> AnalyzeResponse:
        matches_raw = raw.get("matches", []) if isinstance(raw, dict) else []
        matches: list[MatchedLawItem] = []

        for item in matches_raw:
            if not isinstance(item, dict):
                continue
            law_name = str(item.get("law_name", "")).strip()
            law_id = str(item.get("law_id", "")).strip()
            article_id = str(item.get("article_id", "")).strip()
            analysis = str(item.get("analysis", "")).strip()
            if law_name and law_id and article_id and analysis:
                matches.append(
                    MatchedLawItem(
                        law_name=law_name,
                        law_id=law_id,
                        article_id=article_id,
                        analysis=analysis,
                    )
                )

        return AnalyzeResponse(action=action, matches=matches)
