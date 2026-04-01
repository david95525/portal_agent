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
            records = state.get("data")
            full_data_str = "\n".join([f"- {r.get('date')}: 血壓 {r.get('sys')}/{r.get('dia')} mmHg" for r in records])
            response_text = f"已為您準備好 {target_start} 起的數據（共 {len(records)} 筆）：\n{full_data_str}"
            return {"final_response": response_text}

        # 使用配置中的域名與端點
        url = f"{settings.api_domain}{settings.get_bpm_history_endpoint}"
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
                
                # 一律返回完整列表的字串表示
                full_data_str = "\n".join([f"- {r.get('date')}: 血壓 {r.get('sys')}/{r.get('dia')} mmHg" for r in records])
                response_text = f"已為您獲取 {target_start} 起的完整紀錄（共 {len(records)} 筆）：\n{full_data_str}"

                return {
                    "data": records,
                    "cached_start": target_start,
                    "cached_end": target_end,
                    "final_response": response_text
                }
        except Exception as e:
            logger.error(f"[API Error] {e}")
            return {"data": [], "final_response": f"獲取數據失敗: {str(e)}"}

    async def calculate_stats(self, state: BPAgentState):
        data = state.get("data", [])
        if not data:
            return {"final_response": "目前沒有數據可供統計。"}
        
        data_summary = "\n".join([f"- {r.get('date')}: {r.get('sys')}/{r.get('dia')}" for r in data])
        
        prompt = (
            "你是一個專業的血壓數據統計助理。請根據以下數據，精確回答用戶關於『統計』的問題：\n"
            f"【數據列表】：\n{data_summary}\n\n"
            f"【用戶問題】：{state['input_message']}\n\n"
            "【工作準則】：\n"
            "1. 僅提供數據統計結果，例如：平均值、大於/小於某數值的筆數、最大值、最小值、趨勢變化（上升或下降百分比）等。\n"
            "2. 嚴禁提供任何醫學分析、健康建議、衛教提示或個人化評論（例如不要說『您的血壓很健康』或『請諮詢醫生』）。\n"
            "3. 若用戶問『正常嗎』或要求分析，請回覆：『我僅提供數據統計服務，您的平均值為 X/Y，大於 120 的有 Z 筆...』，以此類推。\n"
            "4. 請以條列式或簡潔的文字回覆統計結果。"
        )

        try:
            res = await self.llm.ainvoke(prompt)
            return {"stats_result": res.content, "final_response": res.content}
        except Exception as e:
            logger.error(f"Stats Calculation Error: {e}")
            return {"final_response": f"統計失敗: {e}"}
