import json
from pathlib import Path


def load_payload(path: str | Path) -> dict:
    """Carrega o resultado das rotas salvo em JSON."""
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def answer_question(question: str, payload: dict) -> str:
    """Responde perguntas simples em linguagem natural sobre as rotas geradas."""
    q = question.lower()
    routes = payload.get("routes", [])

    if "maior distância" in q or "maior distancia" in q or "mais distância" in q or "mais distancia" in q:
        route = max(routes, key=lambda item: item["distance_km"])
        return f"O veículo com maior distância é {route['vehicle_name']}, com {route['distance_km']} km."

    if "autonomia" in q or "ultrapassou" in q:
        exceeded = [route for route in routes if route["autonomy_excess_km"] > 0]
        if not exceeded:
            return "Nenhuma rota ultrapassou a autonomia máxima dos veículos."
        names = ", ".join(f"{route['vehicle_name']} (+{route['autonomy_excess_km']} km)" for route in exceeded)
        return f"As rotas que ultrapassaram a autonomia foram: {names}."

    if "capacidade" in q or "carga" in q:
        exceeded = [route for route in routes if route["capacity_excess_kg"] > 0]
        if not exceeded:
            return "Nenhuma rota ultrapassou a capacidade de carga dos veículos."
        names = ", ".join(f"{route['vehicle_name']} (+{route['capacity_excess_kg']} kg)" for route in exceeded)
        return f"As rotas que ultrapassaram a capacidade foram: {names}."

    if "crítica" in q or "critica" in q or "prioridade" in q:
        critical = []
        for route in routes:
            for stop in route["stops"]:
                if stop["priority"] == 3:
                    critical.append(f"{stop['name']} em {route['vehicle_name']}")
        return "Entregas críticas: " + ("; ".join(critical) if critical else "nenhuma entrega crítica encontrada.")

    if "atraso" in q or "atrasadas" in q:
        total_late = sum(route["late_deliveries"] for route in routes)
        return f"O planejamento possui {total_late} entregas com atraso projetado."

    if "custo" in q:
        return f"O custo total da solução foi {payload.get('total_cost')}."

    return "Não encontrei uma resposta específica. Tente perguntar sobre distância, autonomia, capacidade, prioridade, atraso ou custo."
