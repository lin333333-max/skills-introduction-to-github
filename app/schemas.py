"""
功能说明（中文）：
1. 定义接口输入输出数据结构（Pydantic 模型）。
2. 约束返回字段：犯罪行为、法律名称、法律id、法条id、分析说明。
3. 便于后续扩展字段时仅改 schema，不影响业务主流程。

命令示例（Windows PowerShell）：
1. 启动后访问文档：
   http://127.0.0.1:8000/docs
2. 使用 curl 调用：
   curl -X POST "http://127.0.0.1:8000/analyze" -H "Content-Type: application/json" -d "{\"action\":\"入室盗窃他人财物\"}"
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class AnalyzeRequest(BaseModel):
    action: str = Field(..., description="待分析的犯罪行为描述", min_length=2)


class MatchedLawItem(BaseModel):
    law_name: str = Field(..., description="法律名称")
    law_id: str = Field(..., description="法律ID")
    article_id: str = Field(..., description="法条ID")
    analysis: str = Field(..., description="触犯原因分析")


class AnalyzeResponse(BaseModel):
    action: str = Field(..., description="输入的犯罪行为")
    matches: list[MatchedLawItem] = Field(default_factory=list, description="匹配到的法律法条")
