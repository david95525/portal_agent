from abc import ABC
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from app.core.config import settings

class BaseAgent(ABC):
    def __init__(self, service_name: str):
        self.service_name = service_name
        self.llm = self._get_llm()

    def _get_llm(self):
        provider = settings.llm_provider.lower()
        if provider == "google":
            return ChatGoogleGenerativeAI(
                model="gemini-2.5-flash",
                google_api_key=settings.gemini_api_key,
                temperature=0
            )
        elif provider == "openai":
            return ChatOpenAI(
                model="gpt-4o",
                api_key=settings.openai_api_key,
                temperature=0
            )
        else:
            raise ValueError(f"Unsupported provider: {provider}")
