"""
功能说明（中文）：
1. 读取并解析大模型配置文件（key=value 格式），支持你提供的 config_235b.txt。
2. 将 provider/base_url/api_key/model_name/timeout 等参数转换为程序可用配置。
3. 提供统一的配置对象，方便后续替换模型或改配置时只改这一个文件。

命令示例（Windows PowerShell）：
1. 启动服务：
   uvicorn app.main:app --host 0.0.0.0 --port 8000
2. 指定配置文件和法律目录：
   $env:ACTION_LAW_CONFIG="D:\\Work_ICT\\action_law\\config_235b.txt"
   $env:ACTION_LAW_DIR="D:\\Work_ICT\\action_law\\laws"
   uvicorn app.main:app --host 0.0.0.0 --port 8000
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass
class LLMSettings:
    provider: str
    base_url: str
    api_key: str
    model_name: str
    model_type: str = "chat"
    timeout: int = 1000
    context_length: int = 4096
    max_tokens: int = 4096
    vision: bool = False
    function_call: bool = False
    enable_thinking: bool = False


def _parse_bool(value: str, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "y", "on"}


def load_llm_settings(config_path: str | Path) -> LLMSettings:
    """解析 key=value 文本配置文件。"""
    path = Path(config_path)
    if not path.exists():
        raise FileNotFoundError(f"未找到模型配置文件: {path}")

    raw: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        raw[key.strip()] = value.strip()

    required = ["provider", "base_url", "api_key", "model_name"]
    missing = [k for k in required if not raw.get(k)]
    if missing:
        raise ValueError(f"配置缺失字段: {missing}")

    return LLMSettings(
        provider=raw["provider"],
        base_url=raw["base_url"],
        api_key=raw["api_key"],
        model_name=raw["model_name"],
        model_type=raw.get("model_type", "chat"),
        timeout=int(raw.get("timeout", 1000)),
        context_length=int(raw.get("context_length", 4096)),
        max_tokens=int(raw.get("max_tokens", 4096)),
        vision=_parse_bool(raw.get("vision", "false")),
        function_call=_parse_bool(raw.get("function_call", "false")),
        enable_thinking=_parse_bool(raw.get("enable_thinking", "false")),
    )
