"""
功能说明（中文）：
1. 从 laws 目录加载所有 json 法律文件。
2. 将法律数据标准化成统一结构，提供给大模型做检索分析。
3. 需要替换法律数据来源时，只改本文件。

命令示例（Windows PowerShell）：
1. 设置法律目录：
   $env:ACTION_LAW_DIR="D:\\Work_ICT\\action_law\\laws"
2. 启动服务：
   uvicorn app.main:app --host 0.0.0.0 --port 8000
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class LawRepository:
    def __init__(self, law_dir: str | Path):
        self.law_dir = Path(law_dir)

    def load_laws(self) -> list[dict[str, Any]]:
        if not self.law_dir.exists():
            raise FileNotFoundError(f"法律目录不存在: {self.law_dir}")

        results: list[dict[str, Any]] = []
        for file in sorted(self.law_dir.glob("*.json")):
            with file.open("r", encoding="utf-8") as f:
                data = json.load(f)
            results.append(self._normalize_law(data, file.name))
        return results

    @staticmethod
    def _normalize_law(data: dict[str, Any], filename: str) -> dict[str, Any]:
        """
        兼容常见法律 json 结构。
        目标结构:
        {
          "law_id": "xxx",
          "law_name": "xxx",
          "articles": [{"article_id": "...", "article_text": "..."}]
        }
        """
        law_id = str(data.get("law_id") or data.get("id") or filename)
        law_name = str(data.get("law_name") or data.get("name") or filename)

        raw_articles = data.get("articles") or data.get("clauses") or []
        articles: list[dict[str, str]] = []
        for idx, article in enumerate(raw_articles, start=1):
            if isinstance(article, dict):
                article_id = str(
                    article.get("article_id")
                    or article.get("id")
                    or article.get("clause_id")
                    or idx
                )
                article_text = str(
                    article.get("article_text")
                    or article.get("text")
                    or article.get("content")
                    or ""
                )
            else:
                article_id = str(idx)
                article_text = str(article)

            if article_text.strip():
                articles.append({"article_id": article_id, "article_text": article_text})

        return {
            "law_id": law_id,
            "law_name": law_name,
            "articles": articles,
        }
