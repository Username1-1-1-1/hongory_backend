from fastapi import APIRouter, WebSocket
from pydantic import BaseModel
from tree_state import update_tree, get_tree
import json
from langchain_chain import extract_tree_command
from typing import List

router = APIRouter()
connections = []

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
            await connection.send_text(message)

manager = ConnectionManager()

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()  # 🔥 이게 빠지면 403 나옴
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.broadcast(data)
    except Exception as e:
        print(f"WebSocket 오류: {e}")
    finally:
        await manager.disconnect(websocket)


@router.post("/chat")
async def handle_chat(data: ChatRequest):
    user_input = data.message
    result = extract_tree_command(user_input)
    
    print(result)
    result = json.loads(result)
    path = result.get("path")
    value = result.get("value")
    if not isinstance(path, list) or not path:
        return{"tree": get_tree()}
    update_tree(path, value)
    await broadcast_tree()
    return {"message": "트리 업데이트 완료", "tree": get_tree()}

async def broadcast_tree():
    tree_data = get_tree()  # tree_state.py의 함수
    for conn in connections:
        await conn.send_json({"type": "tree_update", "tree": tree_data})
