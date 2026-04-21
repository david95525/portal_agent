import asyncio
from typing import Dict, Any, List
from langchain_core.runnables import RunnableLambda, RunnableConfig
from langchain_core.messages import HumanMessage
from app.services.base import BaseAgent
from app.utils.logger import setup_logger
from app.services.bp_agent.nodes.router import RouterNode
from app.services.bp_agent.nodes.data_nodes import DataNodes

logger = setup_logger("LangChainService")

class LangChainService(BaseAgent):
    def __init__(self):
        super().__init__("LangChainService")
        self.router_manager = RouterNode(self.llm)
        self.data_manager = DataNodes(self.llm)
        
        # 定義 Chain 結構
        self.chain = self._build_chain()

    def _build_chain(self):
        """構建純 LangChain 流程 (LCEL)"""
        
        # 1. 意圖路由節點
        router_step = RunnableLambda(self.router_manager.route_intent)
        
        # 2. 數據查詢節點 (封裝成符合 LCEL 的 lambda)
        search_step = RunnableLambda(self.data_manager.search_data)
        
        # 3. 統計計算節點
        stats_step = RunnableLambda(self.data_manager.calculate_stats)
        
        # 4. 閒聊節點
        general_step = RunnableLambda(self.node_general)

        async def full_flow(input_data: Dict[str, Any], config: RunnableConfig):
            # 初始化狀態
            state = input_data
            
            # --- 執行 Router ---
            router_res = await router_step.ainvoke(state, config)
            state.update(router_res)
            
            intent = state.get("intent")
            
            # --- 根據意圖走不同路徑 ---
            if intent == "search":
                # 僅搜尋
                search_res = await search_step.ainvoke(state, config)
                state.update(search_res)
            
            elif intent == "stats":
                # 統計 (需要先搜尋數據)
                # 這裡模擬 LangGraph 的條件邊：先 search 再 stats
                search_res = await search_step.ainvoke(state, config)
                state.update(search_res)
                
                stats_res = await stats_step.ainvoke(state, config)
                state.update(stats_res)
                
            else:
                # 閒聊或其他
                general_res = await general_step.ainvoke(state, config)
                state.update(general_res)
                
            return state

        return RunnableLambda(full_flow)

    async def node_general(self, state: Dict[str, Any]):
        prompt = f"你是一個親切的生理數據助理，請回應用戶：{state['input_message']}"
        res = await self.llm.ainvoke(prompt)
        return {"final_response": res.content}

    async def get_response(self, user_id: str, message: str, user_token: str) -> Dict[str, Any]:
        """
        對齊原有的 handle_chat 接口格式
        """
        initial_state = {
            "user_id": user_id,
            "user_token": user_token,
            "input_message": message,
            "messages": [HumanMessage(content=message)],
            "data": None # 初始無數據
        }
        
        try:
            logger.info(f"Processing LCEL flow for user {user_id}: {message}")
            final_state = await self.chain.ainvoke(initial_state)
            
            return {
                "text": final_state.get("final_response", "未生成回應"),
                "intent": final_state.get("intent", "general")
            }
        except Exception as e:
            logger.error(f"Error in LangChainService flow: {e}")
            return {"text": "處理出錯，請稍後再試。", "intent": "error"}
