from fastapi import APIRouter
from pydantic import BaseModel
from tree_state import update_tree, get_tree, refactor
import json
from langchain_chain import extract_tree_command

router = APIRouter()

class ChatRequest(BaseModel):
    message: str

@router.post("/chat")
def handle_chat(data: ChatRequest):
    user_input = data.message
    result = extract_tree_command(user_input)
    
    print(result)
    result = json.loads(result)
    path = result.get("path")
    value = result.get("value")
    if not isinstance(path, list) or not path:
        return{"tree": get_tree()}
    update_tree(path, value)
    return {"message": "트리 업데이트 완료", "tree": get_tree()}
