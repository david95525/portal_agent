from typing import Annotated, List, Optional, TypedDict, Literal, Dict, Any
import operator
from langchain_core.messages import BaseMessage

class BPAgentState(TypedDict):
    # 基礎資訊
    user_id: str
    user_token: str
    input_message: str
    messages: Annotated[List[BaseMessage], operator.add]
    
    # 意圖與歷史
    intent: Literal["search", "stats", "general", "error"]
    last_intent: Optional[str]
    
    # 查詢參數 (當前要求的範圍)
    query_start: Optional[str]
    query_end: Optional[str]
    
    # 數據緩存 (目前 state 裡有的數據範圍)
    cached_start: Optional[str]
    cached_end: Optional[str]
    data: Optional[List[Dict[str, Any]]]
    
    analysis_result: Optional[str]
    query_params: Optional[Dict[str, Any]]
    
    final_response: str
