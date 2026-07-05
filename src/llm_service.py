import json


class LocalLLMService:
    """Gera textos em linguagem natural usando regras locais sem depender de API externa."""

    def generate_driver_instructions(self, route: dict) -> str:
        """Cria instruções resumidas para o motorista de uma rota."""
        if not route["stops"]:
            return f"{route['vehicle_name']}: veículo sem entregas programadas."
        stops = " -> ".join(stop["name"] for stop in route["stops"])
        critical = [stop["name"] for stop in route["stops"] if stop["priority"] == 3]
        critical_text = " Priorize atenção nas entregas críticas: " + ", ".join(critical) + "." if critical else ""
        return (
            f"{route['vehicle_name']}: sair da base e seguir a sequência {stops}. "
            f"Distância estimada: {route['distance_km']} km. "
            f"Carga estimada: {route['load_kg']} kg."
            f"{critical_text} Conferir comprovante de entrega em cada parada."
        )

    def generate_operations_summary(self, payload: dict) -> str:
        """Cria um resumo operacional do conjunto de rotas otimizadas."""
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
        """Sugere melhorias operacionais com base nas métricas das rotas."""
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


def build_llm_context(payload: dict) -> str:
    """Prepara um contexto textual estruturado para uso em prompts de LLM."""
    return json.dumps(payload, ensure_ascii=False, indent=2)
