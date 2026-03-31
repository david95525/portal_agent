import os
import asyncio
from langgraph.graph import StateGraph, START, END
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from contextlib import AsyncExitStack

from app.services.base import BaseAgent
from app.utils.logger import setup_logger
from app.services.bp_agent.state import BPAgentState
from app.services.bp_agent.nodes.router import RouterNode
from app.services.bp_agent.nodes.data_nodes import DataNodes
from app.core.config import settings

logger = setup_logger("BPAgentService")


class BPAgentService(BaseAgent):

    def __init__(self):
        super().__init__("BPAgentService")
        self.db_path = settings.state_db_path
        self.memory = None
        self.app = None
        self._exit_stack = AsyncExitStack()
        self._init_lock = asyncio.Lock()

    async def initialize(self):
        async with self._init_lock:
            if self.memory is None:
                # 確保目錄存在
                os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

                self.memory = await self._exit_stack.enter_async_context(
                    AsyncSqliteSaver.from_conn_string(self.db_path))
                workflow = self._build_workflow()
                self.app = workflow.compile(checkpointer=self.memory)
                logger.info(
                    f"BPAgent LangGraph Compiled Successfully (DB: {self.db_path})"
                )

    def _build_workflow(self):
        graph = StateGraph(BPAgentState)

        router_manager = RouterNode(self.llm)
        data_manager = DataNodes(self.llm)

        graph.add_node("router", router_manager.route_intent)
        graph.add_node("search", data_manager.search_data)
        graph.add_node("stats", data_manager.analyze_stats)
        graph.add_node("general", self.node_general)

        # 預留未來節點
        # graph.add_node("oxygen", oxygen_node)
        # graph.add_node("visualize", viz_node)

        graph.add_edge(START, "router")

        def supervisor_route(state: BPAgentState):
            intent = state["intent"]
            if intent == "search":
                return "search"
            if intent == "stats":
                # 檢查是否需要重新抓取數據
                need_fetch = (
                    not state.get("data")
                    or state.get("cached_start") != state.get("query_start")
                    or state.get("cached_end") != state.get("query_end"))
                return "search" if need_fetch else "stats"
            return intent if intent == "general" else "general"

        graph.add_conditional_edges("router", supervisor_route, {
            "search": "search",
            "stats": "stats",
            "general": "general"
        })

        def after_search(state: BPAgentState):
            return "stats" if state["intent"] == "stats" else END

        graph.add_conditional_edges("search", after_search)
        graph.add_edge("stats", END)
        graph.add_edge("general", END)

        return graph

    async def node_general(self, state: BPAgentState):
        prompt = f"你是一個親切的血壓數據助理，請回應用戶：{state['input_message']}"
        res = await self.llm.ainvoke(prompt)
        return {"final_response": res.content}

    async def handle_chat(self, user_id: str, message: str, user_token: str):
        if self.app is None:
            await self.initialize()

        config = {"configurable": {"thread_id": user_id}}
        initial_state = {
            "user_id": user_id,
            "user_token": user_token,
            "input_message": message,
            "messages": [HumanMessage(content=message)]
        }

        try:
            final_state = await self.app.ainvoke(initial_state, config=config)
            return {
                "text": final_state["final_response"],
                "intent": final_state.get("intent", "general")
            }
        except Exception as e:
            logger.error(f"Execution Error: {e}")
            return {"text": "處理出錯，請稍後再試。", "intent": "error"}

    async def close(self):
        await self._exit_stack.aclose()
