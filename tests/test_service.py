import pytest
from unittest.mock import AsyncMock, MagicMock
from app.services.bp_agent.service import BPAgentService

@pytest.mark.asyncio
async def test_bp_agent_service_initialize(mock_sqlite_saver, mock_llm_classes):
    service = BPAgentService()
    await service.initialize()
    
    assert service.memory is not None
    assert service.app is not None
    mock_sqlite_saver.from_conn_string.assert_called_once()

@pytest.mark.asyncio
async def test_bp_agent_service_handle_chat(mock_sqlite_saver, mock_llm_classes):
    service = BPAgentService()
    # Mock self.app.ainvoke
    mock_app = AsyncMock()
    mock_app.ainvoke.return_value = {
        "final_response": "Hello!",
        "intent": "general"
    }
    service.app = mock_app
    service.memory = MagicMock()
    
    result = await service.handle_chat("user1", "hi", "token1")
    
    assert result["text"] == "Hello!"
    assert result["intent"] == "general"
    mock_app.ainvoke.assert_called_once()

@pytest.mark.asyncio
async def test_bp_agent_service_error_handling(mock_sqlite_saver, mock_llm_classes):
    service = BPAgentService()
    mock_app = AsyncMock()
    mock_app.ainvoke.side_effect = Exception("Workflow Error")
    service.app = mock_app
    service.memory = MagicMock()
    
    result = await service.handle_chat("user1", "hi", "token1")
    
    assert result["intent"] == "error"
    assert "處理出錯" in result["text"]
