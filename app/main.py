"""
功能说明（中文）：
1. FastAPI 入口文件，提供 /health 和 /analyze 接口。
2. 通过环境变量读取配置文件路径、法律目录路径，实现可配置化。
3. 组织模块化服务：配置解析、法律加载、模型调用、分析聚合。

命令示例（Windows PowerShell）：
1. 安装依赖：
   pip install -r requirements.txt
2. 设置路径（按你提供的路径）：
   $env:ACTION_LAW_CONFIG="D:\\Work_ICT\\action_law\\config_235b.txt"
   $env:ACTION_LAW_DIR="D:\\Work_ICT\\action_law\\laws"
3. 启动服务：
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
4. 测试接口：
   curl -X POST "http://127.0.0.1:8000/analyze" -H "Content-Type: application/json" -d "{\"action\":\"入室盗窃他人财物\"}"
"""

from __future__ import annotations

import os

from fastapi import FastAPI, HTTPException

from app.config import load_llm_settings
from app.schemas import AnalyzeRequest, AnalyzeResponse
from app.services.analyzer import LawAnalyzer
from app.services.law_repository import LawRepository
from app.services.llm_client import LLMClient


app = FastAPI(title="Action Law Analyzer", version="1.0.0")


def _build_analyzer() -> LawAnalyzer:
    config_path = os.getenv("ACTION_LAW_CONFIG", "config_235b.txt")
    law_dir = os.getenv("ACTION_LAW_DIR", "laws")

    settings = load_llm_settings(config_path)
    repo = LawRepository(law_dir)
    llm = LLMClient(settings)
    return LawAnalyzer(repo, llm)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/analyze", response_model=AnalyzeResponse)
def analyze_action(req: AnalyzeRequest) -> AnalyzeResponse:
    try:
        analyzer = _build_analyzer()
        return analyzer.analyze(req.action)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"分析失败: {exc}") from exc
