import json
import urllib.error
import urllib.request
from pathlib import Path

from src.prompts import (
    build_driver_instructions_prompt,
    build_improvement_prompt,
    build_operations_report_prompt,
    build_question_prompt,
)


class OllamaLLMService:
    """Integra o projeto com uma LLM local via Ollama, sem API paga e sem chave externa."""

    def __init__(self, model: str = "llama3.2", base_url: str = "http://localhost:11434") -> None:
        """Define o modelo local e o endereço da API REST do Ollama."""
        self.model = model
        self.base_url = base_url.rstrip("/")

    def generate(self, prompt: str) -> str:
        """Envia um prompt ao Ollama e retorna o texto gerado pela LLM local."""
        url = f"{self.base_url}/api/generate"
        body = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                # Temperatura baixa reduz respostas criativas demais e deixa o relatório mais consistente.
                "temperature": 0.2,
                # Limita o tamanho da resposta para evitar relatórios excessivamente longos.
                "num_predict": 1200,
            },
        }
        request = urllib.request.Request(
            url=url,
            data=json.dumps(body).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with urllib.request.urlopen(request, timeout=180) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except urllib.error.URLError as exc:
            raise RuntimeError(
                "Não foi possível conectar ao Ollama. "
                "Verifique se o Ollama está instalado e rodando com: ollama serve"
            ) from exc

        return payload.get("response", "").strip()

    def generate_driver_instructions(self, payload: dict) -> str:
        """Gera instruções detalhadas para motoristas a partir do JSON de rotas."""
        return self.generate(build_driver_instructions_prompt(payload))

    def generate_operations_report(self, payload: dict) -> str:
        """Gera relatório operacional com análise de eficiência, riscos e melhorias."""
        return self.generate(build_operations_report_prompt(payload))

    def suggest_improvements(self, payload: dict) -> str:
        """Gera sugestões de melhoria logística usando a LLM local."""
        return self.generate(build_improvement_prompt(payload))

    def answer_question(self, payload: dict, question: str) -> str:
        """Responde perguntas em linguagem natural sobre as rotas usando a LLM local."""
        return self.generate(build_question_prompt(payload, question))


class LocalRuleBasedService:
    """Gera textos por regras locais quando a LLM não está habilitada ou disponível."""

    def generate_driver_instructions_for_route(self, route: dict) -> str:
        """Cria instruções simples para uma rota específica sem usar LLM."""
        if not route["stops"]:
            return f"{route['vehicle_name']}: veículo sem entregas programadas."

        stops = " -> ".join(stop["name"] for stop in route["stops"])
        critical = [stop["name"] for stop in route["stops"] if stop["priority"] == 3]
        critical_text = ""
        if critical:
            critical_text = " Priorize atenção nas entregas críticas: " + ", ".join(critical) + "."

        return (
            f"{route['vehicle_name']}: sair da base e seguir a sequência {stops}. "
            f"Distância estimada: {route['distance_km']} km. "
            f"Carga estimada: {route['load_kg']} kg."
            f"{critical_text} Conferir comprovante de entrega em cada parada."
        )

    def generate_operations_summary(self, payload: dict) -> str:
        """Cria um resumo operacional simples com métricas calculadas pelo algoritmo."""
        total_distance = sum(route["distance_km"] for route in payload["routes"])
        total_late = sum(route["late_deliveries"] for route in payload["routes"])
        overloaded = [route["vehicle_name"] for route in payload["routes"] if route["capacity_excess_kg"] > 0]
        autonomy = [route["vehicle_name"] for route in payload["routes"] if route["autonomy_excess_km"] > 0]
        return (
            f"Resumo operacional: a malha planejada possui {total_distance:.2f} km de distância estimada. "
            f"Foram identificadas {total_late} entregas com atraso projetado. "
            f"Veículos com excesso de capacidade: {', '.join(overloaded) if overloaded else 'nenhum'}. "
            f"Veículos com excesso de autonomia: {', '.join(autonomy) if autonomy else 'nenhum'}."
        )

    def suggest_improvements(self, payload: dict) -> list[str]:
        """Sugere melhorias por regras para manter o projeto útil mesmo sem Ollama."""
        suggestions = []
        for route in payload["routes"]:
            if route["capacity_excess_kg"] > 0:
                suggestions.append(f"Redistribuir carga do {route['vehicle_name']} para evitar excesso de capacidade.")
            if route["autonomy_excess_km"] > 0:
                suggestions.append(f"Reduzir distância do {route['vehicle_name']} ou alocar veículo com maior autonomia.")
            if route["late_deliveries"] > 0:
                suggestions.append(f"Revisar a ordem de entregas do {route['vehicle_name']} para reduzir atrasos.")
        if not suggestions:
            suggestions.append("Manter o planejamento atual e monitorar tempos reais de entrega para calibrar o modelo.")
        return suggestions


def save_text(path: str | Path, content: str) -> None:
    """Salva um texto em arquivo, criando a pasta de destino quando necessário."""
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as file:
        file.write(content)


def generate_rule_based_driver_file(payload: dict, output_path: str | Path) -> None:
    """Gera o arquivo de instruções por regras locais, sem depender de LLM."""
    service = LocalRuleBasedService()
    lines = ["# Instruções para Motoristas", "", "Fonte: regras locais do sistema, sem LLM.", ""]
    for route in payload["routes"]:
        lines.append(f"- {service.generate_driver_instructions_for_route(route)}")
    lines.extend(["", "## Resumo operacional", "", service.generate_operations_summary(payload), "", "## Sugestões de melhoria", ""])
    for suggestion in service.suggest_improvements(payload):
        lines.append(f"- {suggestion}")
    save_text(output_path, "\n".join(lines))


def generate_ollama_outputs(payload: dict, output_dir: str | Path, model: str = "llama3.2", base_url: str = "http://localhost:11434") -> None:
    """Gera relatórios com LLM local usando Ollama e salva os arquivos em outputs/."""
    service = OllamaLLMService(model=model, base_url=base_url)
    output_dir = Path(output_dir)

    # Cada chamada usa um prompt específico para atender os requisitos de instruções, relatórios e melhorias.
    driver_instructions = service.generate_driver_instructions(payload)
    operations_report = service.generate_operations_report(payload)
    improvements = service.suggest_improvements(payload)

    save_text(output_dir / "llm_driver_instructions.md", driver_instructions)
    save_text(output_dir / "llm_operations_report.md", operations_report)
    save_text(output_dir / "llm_improvement_suggestions.md", improvements)
