from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from app.services.suggest_service import generate_suggestions
from app.services.rewrite_service import rewrite_sentence
from fastapi.middleware.cors import CORSMiddleware
import json
from typing import Optional, Any  # ← 新增导入

app = FastAPI()

# CORS 设置
origins = [
    "http://localhost:5173",  # Vue 前端的地址（你可以根据实际前端地址修改）
    "http://127.0.0.1:8080",  # Vue 前端的地址
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # 允许的源
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],  # 允许的 HTTP 方法
    allow_headers=["*"],  # 允许的请求头
)


class SuggestionRequest(BaseModel):
    text: str
    cursor: Optional[Any] = None  # ← 允许 null 或不传

class RewriteRequest(BaseModel):
    sentence: str  # 用户选中的句子

@app.post("/suggest")
async def get_suggestions(request: SuggestionRequest):
    raw_result = generate_suggestions(request.text, request.cursor)
    try:
        parsed = json.loads(raw_result)
        return {"suggestions": parsed.get("suggestions", [])}
    except:
        return {"suggestions": []}

@app.post("/rewrite")
async def rewrite_sentence_endpoint(request: RewriteRequest):
    # 调用 rewrite_service 进行句子改写
    result = rewrite_sentence(request.sentence)

    # 返回 JSON 格式的结果
    return json.loads(result)  # 解析 JSON 字符串并返回