from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.langchain_service import LangChainService

router = APIRouter()
lc_service = LangChainService()

class LCChatRequest(BaseModel):
    user_id: str
    message: str
    user_token: str

@router.post("/chat")
async def langchain_chat(request: LCChatRequest):
    try:
        # 調用移植後的 LangChain 流程
        response = await lc_service.get_response(
            request.user_id, 
            request.message, 
            request.user_token
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
