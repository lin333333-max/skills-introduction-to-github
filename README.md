# action_law（FastAPI + 大模型法律分析）

## 1. 项目结构（可直接复制到 `D:\Work_ICT\action_law`）

```text
action_law/
├─ app/
│  ├─ __init__.py
│  ├─ main.py                   # FastAPI 入口
│  ├─ config.py                 # 解析 config_235b.txt
│  ├─ schemas.py                # 入参/出参模型
│  └─ services/
│     ├─ __init__.py
│     ├─ law_repository.py      # 读取 laws/*.json
│     ├─ llm_client.py          # 调用 DashScope 兼容接口
│     └─ analyzer.py            # 分析流程编排
├─ laws/                        # 你的法律 json 文件目录
├─ config_235b.txt              # 你的模型配置文件
└─ requirements.txt
```

## 2. 安装依赖

```bash
pip install -r requirements.txt
```

## 3. 运行（Windows PowerShell）

```powershell
cd D:\Work_ICT\action_law
$env:ACTION_LAW_CONFIG="D:\Work_ICT\action_law\config_235b.txt"
$env:ACTION_LAW_DIR="D:\Work_ICT\action_law\laws"
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 4. 调用示例

```powershell
curl -X POST "http://127.0.0.1:8000/analyze" `
  -H "Content-Type: application/json" `
  -d "{\"action\":\"入室盗窃他人财物\"}"
```

返回结构示例：

```json
{
  "action": "入室盗窃他人财物",
  "matches": [
    {
      "law_name": "中华人民共和国刑法",
      "law_id": "criminal_law",
      "article_id": "264",
      "analysis": "该行为以非法占有为目的，秘密窃取他人财物，符合盗窃罪构成要件。"
    }
  ]
}
```
