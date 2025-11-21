from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from starlette.websockets import WebSocketDisconnect
from app.core.suggester import get_dummy_suggestions

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.websocket("/ws/suggest")
async def suggest(ws: WebSocket):
    await ws.accept()
    print("Client connected.")

    try:
        while True:
            data = await ws.receive_json()
            text = data.get("text", "")

            print("Received from client:", text[:50])  # 打印前50字符

            suggestions = get_dummy_suggestions(text)
            await ws.send_json(suggestions)

    except WebSocketDisconnect:
        print("Client disconnected")
