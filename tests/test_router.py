import pytest
from unittest.mock import AsyncMock
from app.services.bp_agent.nodes.router import RouterNode, RouterOutput

@pytest.mark.asyncio
async def test_route_intent_search(mock_llm):
    # Setup mock structured output
    mock_structured_llm = AsyncMock()
    mock_llm.with_structured_output.return_value = mock_structured_llm
    
    mock_structured_llm.ainvoke.return_value = RouterOutput(
        intent="search",
        query_start="2024-03-01",
        query_end="2024-03-07",
        reasoning="User wants to see blood pressure data for last week."
    )
    
    node = RouterNode(mock_llm)
    state = {"input_message": "幫我查上週的血壓", "messages": []}
    
    result = await node.route_intent(state)
    
    assert result["intent"] == "search"
    assert result["query_start"] == "2024-03-01"
    assert result["query_end"] == "2024-03-07"

@pytest.mark.asyncio
async def test_route_intent_stats(mock_llm):
    # Setup mock structured output
    mock_structured_llm = AsyncMock()
    mock_llm.with_structured_output.return_value = mock_structured_llm
    
    mock_structured_llm.ainvoke.return_value = RouterOutput(
        intent="stats",
        query_start="2024-03-01",
        query_end="2024-03-07",
        reasoning="User wants analysis of data."
    )
    
    node = RouterNode(mock_llm)
    state = {"input_message": "我最近的血壓正常嗎？", "messages": []}
    
    result = await node.route_intent(state)
    
    assert result["intent"] == "stats"

@pytest.mark.asyncio
async def test_route_intent_error(mock_llm):
    mock_llm.with_structured_output.side_effect = Exception("LLM Error")
    
    node = RouterNode(mock_llm)
    state = {"input_message": "hello", "messages": []}
    
    result = await node.route_intent(state)
    
    assert result["intent"] == "general"
