from pathlib import Path
import json
from src.models import Delivery, Vehicle, RouteMetrics


def priority_label(priority: int) -> str:
    """Converte o valor numérico de prioridade em texto explicativo."""
    return {1: "Regular", 2: "Alta", 3: "Crítica"}.get(priority, "Desconhecida")


def build_routes_payload(individual: list[list[int]], vehicles: list[Vehicle], deliveries: list[Delivery], metrics: list[RouteMetrics], cost: float) -> dict:
    """Monta um dicionário estruturado com rotas, métricas e entregas."""
    deliveries_by_id = {delivery.id: delivery for delivery in deliveries}
    routes = []
    for route, vehicle, metric in zip(individual, vehicles, metrics):
        routes.append({
            "vehicle_id": vehicle.id,
            "vehicle_name": vehicle.name,
            "capacity_kg": vehicle.capacity_kg,
            "max_distance_km": vehicle.max_distance_km,
            "distance_km": round(metric.distance_km, 2),
            "load_kg": round(metric.load_kg, 2),
            "total_time_min": round(metric.total_time_min, 2),
            "capacity_excess_kg": round(metric.capacity_excess_kg, 2),
            "autonomy_excess_km": round(metric.autonomy_excess_km, 2),
            "late_deliveries": metric.late_deliveries,
            "stops": [
                {
                    "id": delivery_id,
                    "name": deliveries_by_id[delivery_id].name,
                    "priority": deliveries_by_id[delivery_id].priority,
                    "priority_label": priority_label(deliveries_by_id[delivery_id].priority),
                    "demand_kg": deliveries_by_id[delivery_id].demand_kg,
                    "deadline_min": deliveries_by_id[delivery_id].deadline_min,
                }
                for delivery_id in route
            ],
        })
    return {"total_cost": round(cost, 2), "routes": routes}


def save_routes_json(payload: dict, output_path: str | Path) -> None:
    """Salva as rotas otimizadas em um arquivo JSON."""
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(payload, file, ensure_ascii=False, indent=2)


def generate_markdown_report(payload: dict, output_path: str | Path) -> None:
    """Gera um relatório operacional em Markdown com resumo das rotas."""
    total_distance = sum(route["distance_km"] for route in payload["routes"])
    total_load = sum(route["load_kg"] for route in payload["routes"])
    total_late = sum(route["late_deliveries"] for route in payload["routes"])
    lines = [
        "# Relatório Diário de Rotas Médicas",
        "",
        f"**Custo total da solução:** {payload['total_cost']}",
        f"**Distância total estimada:** {total_distance:.2f} km",
        f"**Carga total transportada:** {total_load:.2f} kg",
        f"**Entregas em atraso:** {total_late}",
        "",
        "## Rotas por veículo",
        "",
    ]

    for route in payload["routes"]:
        lines.extend([
            f"### {route['vehicle_name']}",
            f"- Distância: {route['distance_km']} km",
            f"- Carga: {route['load_kg']} kg de {route['capacity_kg']} kg",
            f"- Autonomia: {route['distance_km']} km de {route['max_distance_km']} km",
            f"- Tempo total estimado: {route['total_time_min']} min",
            f"- Excesso de capacidade: {route['capacity_excess_kg']} kg",
            f"- Excesso de autonomia: {route['autonomy_excess_km']} km",
            "- Sequência de entregas:",
        ])
        if route["stops"]:
            for position, stop in enumerate(route["stops"], start=1):
                lines.append(
                    f"  {position}. {stop['name']} — prioridade {stop['priority_label']}, "
                    f"carga {stop['demand_kg']} kg, prazo {stop['deadline_min']} min"
                )
        else:
            lines.append("  - Veículo não utilizado.")
        lines.append("")

    lines.extend([
        "## Observações",
        "",
        "- Rotas com prioridade crítica devem ser revisadas primeiro pela operação.",
        "- Excesso de capacidade ou autonomia indica que os dados de frota ou entregas devem ser ajustados.",
        "- O resultado é heurístico: novas execuções podem encontrar soluções diferentes.",
    ])

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as file:
        file.write("\n".join(lines))
