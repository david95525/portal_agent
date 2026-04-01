import pytest
import respx
from httpx import Response
from unittest.mock import MagicMock
from app.services.bp_agent.nodes.data_nodes import DataNodes

@pytest.mark.asyncio
@respx.mock
async def test_search_data_success(mock_llm):
    # Mock API call
    respx.get("https://api.test.com/api/get_bpm_history_data").mock(return_value=Response(200, json={
        "data": [
            {"date": "2024-03-01", "sys": 120, "dia": 80},
            {"date": "2024-03-02", "sys": 122, "dia": 82}
        ],
        "total_num": 2
    }))
    
    node = DataNodes(mock_llm)
    state = {
        "user_token": "test_token",
        "query_start": "2024-03-01",
        "query_end": "2024-03-02"
    }
    
    result = await node.search_data(state)
    
    assert len(result["data"]) == 2
    assert "cached_start" in result
    assert "final_response" in result
    assert "120/80" in result["final_response"]

@pytest.mark.asyncio
async def test_search_data_cache_hit(mock_llm):
    node = DataNodes(mock_llm)
    state = {
        "data": [{"date": "2024-03-01", "sys": 120, "dia": 80}],
        "cached_start": "2024-03-01",
        "cached_end": "2024-03-02",
        "query_start": "2024-03-01",
        "query_end": "2024-03-02"
    }
    
    result = await node.search_data(state)
    assert "已為您準備好" in result["final_response"]

@pytest.mark.asyncio
async def test_calculate_stats_success(mock_llm):
    mock_llm.ainvoke.return_value = MagicMock(content="您的平均血壓為 120/80。")
    
    node = DataNodes(mock_llm)
    state = {
        "data": [{"date": "2024-03-01", "sys": 120, "dia": 80}],
        "input_message": "我的平均血壓是多少？"
    }
    
    result = await node.calculate_stats(state)
    
    assert result["stats_result"] == "您的平均血壓為 120/80。"
    assert result["final_response"] == "您的平均血壓為 120/80。"

@pytest.mark.asyncio
async def test_calculate_stats_no_data(mock_llm):
    node = DataNodes(mock_llm)
    state = {"data": []}
    
    result = await node.calculate_stats(state)
    assert "沒有數據" in result["final_response"]
