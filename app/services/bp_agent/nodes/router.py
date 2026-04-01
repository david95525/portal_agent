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

        # 獲取歷史對話，僅取最近 5 則以節省 Token 並保持焦點
        history = ""
        if state.get("messages"):
            recent_messages = state["messages"][-5:]
            history = "\n".join([f"{m.type}: {m.content}" for m in recent_messages])

        prompt = (
            f"【當前系統日期】今天是 {current_date}。\n"
            f"【前次執行意圖】：{state.get('last_intent', '無')}\n"
            f"【對話背景】：\n{history}\n\n"
            "請根據對話背景與用戶輸入判斷意圖並提取日期範圍（YYYY-MM-DD）：\n\n"
            "【意圖類型】：\n"
            "1. 'search': 查詢具體數據紀錄。\n"
            "2. 'stats': 對數據進行數值統計計算（如：筆數、平均值、最高最低、大於某值的次數等），不包含健康分析或診斷建議。\n"
            "3. 'general': 寒暄或無法識別之請求。\n\n"
            "【決策準則】：\n"
            "- 如果用戶問『我的數據正常嗎』，則意圖為 'stats'，以便提供數據統計結果，但不進行醫學診斷。\n"
            "- 如果用戶問『上個月平均多少』或『幾筆大於120』，意圖為 'stats'。\n"
            "- 日期提取請嚴格遵守 YYYY-MM-DD 格式。\n"
            f"【用戶輸入】：{state['input_message']}\n"
        )

        try:
            structured_llm = self.llm.with_structured_output(RouterOutput)
            res: RouterOutput = await structured_llm.ainvoke(prompt)
            logger.info(f"[Router Decision] Intent: {res.intent}, Range: {res.query_start} ~ {res.query_end}")

            return {
                "intent": res.intent,
                "last_intent": res.intent,
                "query_start": res.query_start,
                "query_end": res.query_end
            }
        except Exception as e:
            logger.error(f"Router Error: {e}")
            return {"intent": "general"}
