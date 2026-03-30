from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.bp_agent.service import BPAgentService

router = APIRouter()
bp_service = BPAgentService()

class ChatRequest(BaseModel):
    user_id: str
    message: str
    user_token: str

@router.post("/chat")
async def chat(request: ChatRequest):
    try:
        response = await bp_service.handle_chat(request.user_id, request.message, request.user_token)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
