from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from app.services.suggest_service import generate_suggestions
from app.services.rewrite_service import rewrite_sentence
from fastapi.middleware.cors import CORSMiddleware
import json
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
    text: str  # 用户输入的文本
    cursor: dict  # 用户光标位置（这里暂时没有用到，但你可以根据需求使用）

class RewriteRequest(BaseModel):
    sentence: str  # 用户选中的句子

@app.post("/suggest")
async def get_suggestions(request: SuggestionRequest):
    """
    获取用户当前输入的补全建议（top 3）
    """
    suggestions = generate_suggestions(request.text, request.cursor)
    return {"suggestions": suggestions}


@app.post("/rewrite")
async def rewrite_sentence_endpoint(request: RewriteRequest):
    # 调用 rewrite_service 进行句子改写
    result = rewrite_sentence(request.sentence)

    # 返回 JSON 格式的结果
    return json.loads(result)  # 解析 JSON 字符串并返回

@app.websocket("/ws/suggest")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket 路由，用于实时获取建议
    """
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            # 处理 WebSocket 请求并返回补全建议
            response = await handle_suggest_request(data)
            await websocket.send_text(response)
    except WebSocketDisconnect:
        print("Client disconnected")

async def handle_suggest_request(data: str):
    """
    处理 WebSocket 请求并返回建议
    """
    # 将 data 转换为实际的 text 和 cursor（这里假设 data 只是简单的文本）
    # 如果需要可以在这里解析出光标等信息
    text = data.strip()
    suggestions = generate_suggestions(text, {})
    return str(suggestions)
