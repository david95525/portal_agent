import httpx
from app.services.bp_agent.state import BPAgentState
from app.core.config import settings
from app.utils.logger import setup_logger

logger = setup_logger("DataNodes")

class DataNodes:
    def __init__(self, llm):
        self.llm = llm

    async def search_data(self, state: BPAgentState):
        query_params = state.get("query_params") or {}
        user_token = state.get("user_token")
        
        # 決定查詢範圍
        target_start = state.get("query_start") or "2025-01-01"
        target_end = state.get("query_end") or ""
        
        # 檢查緩存：如果範圍沒變，且已有數據，則跳過 API 請求
        if (state.get("data") and 
            state.get("cached_start") == target_start and 
            state.get("cached_end") == target_end):
            logger.info("[Cache Hit] Using existing data records.")
            return {"final_response": f"已為您準備好 {target_start} 起的數據。"}

        # 根據提供的 API 規格設定參數
        url = f"{settings.api_domain}/api/get_bpm_history_data"
        headers = {
            "Authorization": f"Bearer {user_token}",
            "Content-Type": "application/json"
        }
        
        params = {
            "start": target_start,
            "limit": query_params.get("limit", 500),
            "offset": query_params.get("offset", 0),
            "time_type": query_params.get("time_type", 0)
        }
        if target_end:
            params["end"] = target_end

        logger.info(f"[API Request] URL: {url}, Params: {params}")

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=headers, params=params)
                response.raise_for_status()
                result = response.json()
                
                records = result.get("data", [])
                total_num = result.get("total_num", 0)
                
                summary_lines = [f"- {r.get('date')}: 血壓 {r.get('sys')}/{r.get('dia')} mmHg" for r in records[:3]]
                response_text = f"已獲取 {target_start} 起的 {len(records)} 筆紀錄。\n" + "\n".join(summary_lines)

                return {
                    "data": records,
                    "cached_start": target_start,
                    "cached_end": target_end,
                    "final_response": response_text
                }
        except Exception as e:
            logger.error(f"[API Error] {e}")
            return {"data": [], "final_response": f"獲取數據失敗: {str(e)}"}

    async def analyze_stats(self, state: BPAgentState):
        data = state.get("data", [])
        if not data:
            return {"final_response": "目前沒有數據可供分析。"}
        
        data_summary = "\n".join([f"- {r.get('date')}: {r.get('sys')}/{r.get('dia')}" for r in data])
        prompt = (
            "你是一個專業的血壓分析助理。請根據以下數據回答用戶問題：\n"
            f"【數據列表】：\n{data_summary}\n"
            f"【用戶問題】：{state['input_message']}\n"
        )

        try:
            res = await self.llm.ainvoke(prompt)
            return {"analysis_result": res.content, "final_response": res.content}
        except Exception as e:
            return {"final_response": f"分析失敗: {e}"}
