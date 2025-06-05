from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from tree_state import update_tree, get_tree
import json
from langchain_chain import extract_tree_command
from typing import List

router = APIRouter()

class ChatRequest(BaseModel):
    message: str
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        self.active_connections.append(websocket)

    async def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_json(message)

manager = ConnectionManager()

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()  # 🔥 이게 빠지면 403 나옴
    await manager.connect(websocket)
    try:
        while True:
            raw_data = await websocket.receive_text()
            data = json.loads(raw_data)
            
            if data.get("type") == "chat":
                message = data.get("content")
                name = data.get("name", "사용자")

                # LangChain 처리 및 트리 추출
                parsed = json.loads(extract_tree_command(message))
                path, value = parsed.get("path"), parsed.get("value")

                if path:
                    update_tree(path, value)
                    await manager.broadcast({
                        "type": "tree_update",
                        "tree": get_tree()
                    })
                # 채팅 응답 broadcast
                await manager.broadcast({
                    "type": "chat",
                    "message": message,
                    "name": name
                })
    except WebSocketDisconnect:
        await manager.disconnect(websocket)

