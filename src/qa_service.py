import json
from pathlib import Path

from src.llm_service import OllamaLLMService


def load_payload(path: str | Path) -> dict:
    """Carrega o resultado das rotas salvo em JSON pelo run.py."""
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def answer_question_with_llm(question: str, payload: dict, model: str = "llama3.2", base_url: str = "http://localhost:11434") -> str:
    """Responde perguntas em linguagem natural usando uma LLM local servida pelo Ollama."""
    service = OllamaLLMService(model=model, base_url=base_url)
    return service.answer_question(payload, question)
