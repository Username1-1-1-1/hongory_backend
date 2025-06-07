from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from tree_state import update_tree, get_tree
import json
from langchain_chain import extract_tree_command
from typing import List
import logging
import traceback

logging.basicConfig(level=logging.INFO,
                    format="🪵 [%(asctime)s] %(levelname)s - %(message)s",)

router = APIRouter()

class ChatRequest(BaseModel):
    message: str
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        self.active_connections.append(websocket)

    async def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logging.error(f"📛 브로드캐스트 중 오류: {e}")
                traceback.print_exc()
    def count(self):
        return len(self.active_connections)
manager = ConnectionManager()

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()  # 🔥 이게 빠지면 403 나옴
    await manager.connect(websocket)
    username = websocket.query_params.get("name", "익명")  # 쿼리로 이름 전달받음


    await websocket.send_json({
        "type": "tree_update",
        "tree": get_tree()
    })
    await manager.broadcast({
        "type": "chat",
        "message": f"{username}님이 입장했습니다.",
        "name": "🟢 시스템"
    })
    await manager.broadcast({
        "type": "user_count",
        "count": manager.count()
    })
    try:
        while True:
            try:
                raw_data = await websocket.receive_text()
                
            except RuntimeError as e:
                logging.warning(f"⚠️ RuntimeError 발생: {e}")
                break
            try:
                data = json.loads(raw_data)
            except json.JSONDecodeError:
                logging.warning(f"⚠️ 잘못된 JSON 형식: {raw_data}")
                continue
                
            if data.get("type") == "chat":
                message = data.get("content")
                name = data.get("name", "사용자")

                    # LangChain 처리 및 트리 추출
                parsed = json.loads(extract_tree_command(message))
                path, value = parsed.get("path"), parsed.get("value")

                logging.info(f"path = {path}, value = {value}")
                    
                if path:
                    try:
                        update_tree(path, value)
                        await manager.broadcast({
                            "type": "tree_update",
                            "tree": get_tree()
                        })
                        await manager.broadcast({
                            "type": "chat",
                            "message": "트리가 업데이트되었습니다.",
                            "name": "🤖"
                        })
                    except Exception as e:
                        logging.error(f"🚨 트리 업데이트 중 오류: {e}")
                else:
                    # 의미 없는 채팅도 broadcast에 포함
                    await manager.broadcast({
                        "type": "chat",
                        "message": message,
                        "name": name
                    })
    except WebSocketDisconnect:
        logging.info("🔌 WebSocket 연결 해제됨")
    finally:
        await manager.disconnect(websocket)

        await manager.broadcast({
            "type": "chat",
            "message": f"{username}님이 퇴장했습니다.",
            "name": "🔴 시스템"
        })
        await manager.broadcast({
            "type": "user_count",
            "count": manager.count()
        })
