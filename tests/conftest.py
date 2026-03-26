import pytest
import pytest_asyncio
from unittest.mock import MagicMock, AsyncMock
from app.core.config import settings

@pytest.fixture(autouse=True)
def mock_settings(monkeypatch):
    monkeypatch.setattr(settings, "gemini_api_key", "test_key")
    monkeypatch.setattr(settings, "api_domain", "https://api.test.com")
    monkeypatch.setattr(settings, "llm_provider", "google")

@pytest.fixture(autouse=True)
def mock_llm_classes(mocker):
    mocker.patch("app.services.base.ChatGoogleGenerativeAI", return_value=MagicMock())
    mocker.patch("app.services.base.ChatOpenAI", return_value=MagicMock())

@pytest.fixture
def mock_llm():
    mock = MagicMock()
    mock.ainvoke = AsyncMock()
    mock.with_structured_output = MagicMock()
    return mock

@pytest_asyncio.fixture
async def mock_sqlite_saver(mocker):
    mock = AsyncMock()
    # from_conn_string should be a regular mock that returns an async context manager
    mock.from_conn_string = MagicMock(return_value=mock)
    # Mock __aenter__ and __aexit__ to work with AsyncExitStack
    mock.__aenter__ = AsyncMock(return_value=mock)
    mock.__aexit__ = AsyncMock(return_value=None)
    
    mocker.patch("langgraph.checkpoint.sqlite.aio.AsyncSqliteSaver.from_conn_string", mock.from_conn_string)
    return mock
