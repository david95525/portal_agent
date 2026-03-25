from typing import Optional, Literal
from pydantic import BaseModel, Field
from datetime import datetime
from app.services.bp_agent.state import BPAgentState
from app.utils.logger import setup_logger

logger = setup_logger("RouterNode")

class RouterOutput(BaseModel):
    """意圖路由與日期解析的統一輸出結構"""
    intent: Literal["search", "stats", "general"] = Field(description="用戶的主要意圖 ID")
    query_start: Optional[str] = Field(
        default=None, description="解析出的查詢起始日期，格式為 YYYY-MM-DD")
    query_end: Optional[str] = Field(
        default=None, description="解析出的查詢結束日期，格式為 YYYY-MM-DD")
    reasoning: str = Field(description="判定意圖與日期的簡短理由")

class RouterNode:
    def __init__(self, llm):
        self.llm = llm

    async def route_intent(self, state: BPAgentState):
        current_date = datetime.now().strftime("%Y-%m-%d")
        structured_llm = self.llm.with_structured_output(RouterOutput)

        # 獲取歷史對話，幫助理解「那昨天呢」等連續問題
        history = ""
        if state.get("messages"):
            # 取最近 5 則訊息作為背景
            history = "\n".join([f"{m.type}: {m.content}" for m in state["messages"][-5:]])

        prompt = (
            f"【現在日期參考】今天是 {current_date}。\n"
            f"【上一輪意圖】：{state.get('last_intent', 'None')}\n"
            f"【對話歷史背景】：\n{history}\n\n"
            "你是一個專業的任務分發中心。請根據歷史與用戶輸入判斷意圖並提取日期範圍：\n\n"
            "【意圖 ID 清單】：\n"
            "1. 'search': 用戶想單純查詢特定的數據紀錄。\n"
            "2. 'stats': 用戶想看數據分析、平均值、或針對數據提問（通常需要先獲取數據）。\n"
            "3. 'general': 一般寒暄或無法歸類的請求。\n\n"
            "【決策準則】：\n"
            "- 如果用戶說『那昨天呢』，若歷史是統計，則意圖仍為 'stats'，日期改為昨天。\n"
            "- 如果用戶問『我的數據正常嗎』，則意圖為 'stats'。\n"
            "- 日期提取請嚴格遵守 YYYY-MM-DD 格式。\n"
            f"【當前用戶輸入】：{state['input_message']}\n"
        )
        
        try:
            res: RouterOutput = await structured_llm.ainvoke(prompt)
            logger.info(f"[Router Decision] Intent: {res.intent}, Range: {res.query_start} ~ {res.query_end}, Reason: {res.reasoning}")
            
            return {
                "intent": res.intent,
                "last_intent": res.intent,
                "query_start": res.query_start,
                "query_end": res.query_end
            }
        except Exception as e:
            logger.error(f"Router Error: {e}")
            return {"intent": "general"}
