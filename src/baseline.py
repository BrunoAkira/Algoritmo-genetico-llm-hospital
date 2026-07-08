from pathlib import Path

from src.distance import haversine_km
from src.fitness import evaluate_individual
from src.models import Delivery, Vehicle
from src.genetic_algorithm import Individual


def build_nearest_neighbor_solution(deliveries: list[Delivery], vehicles: list[Vehicle]) -> Individual:
    """Cria uma solução gulosa simples para servir como comparação com o Algoritmo Genético.

    A estratégia escolhe, para cada veículo, a entrega ainda não atendida mais próxima
    do ponto atual. Ela não tenta evoluir soluções, por isso funciona como baseline
    simples para demonstrar o ganho obtido pelo AG.
    """
    remaining = {delivery.id: delivery for delivery in deliveries}
    individual: Individual = [[] for _ in vehicles]

    for vehicle_index, vehicle in enumerate(vehicles):
        current_lat = vehicle.start_lat
        current_lon = vehicle.start_lon
        current_load = 0.0

        while remaining:
            feasible = [
                delivery
                for delivery in remaining.values()
                if current_load + delivery.demand_kg <= vehicle.capacity_kg
            ]

            # Se nenhuma entrega cabe no veículo atual, passa para o próximo veículo.
            if not feasible:
                break

            nearest = min(
                feasible,
                key=lambda delivery: haversine_km(current_lat, current_lon, delivery.lat, delivery.lon),
            )
            individual[vehicle_index].append(nearest.id)
            current_load += nearest.demand_kg
            current_lat = nearest.lat
            current_lon = nearest.lon
            del remaining[nearest.id]

    # Caso ainda existam entregas, distribui as restantes para manter uma solução completa.
    # A função fitness penalizará eventuais excessos de capacidade ou autonomia.
    for index, delivery_id in enumerate(list(remaining.keys())):
        individual[index % len(vehicles)].append(delivery_id)
        del remaining[delivery_id]

    return individual


def generate_performance_comparison(
    ga_individual: Individual,
    ga_cost: float,
    deliveries: list[Delivery],
    vehicles: list[Vehicle],
    output_path: str | Path,
) -> None:
    """Gera um comparativo simples entre o AG e uma heurística gulosa de vizinho mais próximo."""
    baseline_individual = build_nearest_neighbor_solution(deliveries, vehicles)
    baseline_cost, baseline_metrics = evaluate_individual(baseline_individual, vehicles, deliveries)
    ga_metrics_cost, ga_metrics = evaluate_individual(ga_individual, vehicles, deliveries)

    baseline_distance = sum(metric.distance_km for metric in baseline_metrics)
    ga_distance = sum(metric.distance_km for metric in ga_metrics)
    improvement = 0.0
    if baseline_cost > 0:
        improvement = ((baseline_cost - ga_cost) / baseline_cost) * 100

    lines = [
        "# Comparativo de Desempenho",
        "",
        "Este comparativo usa uma heurística gulosa de vizinho mais próximo como baseline.",
        "A heurística escolhe sempre a entrega mais próxima disponível, sem evolução genética.",
        "",
        "| Abordagem | Custo fitness | Distância total estimada | Observação |",
        "|---|---:|---:|---|",
        f"| Algoritmo Genético | {ga_cost:.2f} | {ga_distance:.2f} km | Solução evoluída com seleção, crossover e mutação |",
        f"| Vizinho mais próximo | {baseline_cost:.2f} | {baseline_distance:.2f} km | Heurística gulosa usada como referência |",
        "",
        f"**Melhoria estimada do AG sobre o baseline:** {improvement:.2f}%",
        "",
        "## Interpretação",
        "",
        "O Algoritmo Genético tende a encontrar soluções melhores porque avalia diversas combinações de rotas ao longo das gerações.",
        "A heurística gulosa é rápida, mas pode tomar decisões locais ruins, pois escolhe a próxima entrega mais próxima sem considerar o impacto global na frota.",
        "",
        "## Observação",
        "",
        "Como o AG é heurístico e utiliza aleatoriedade, os resultados podem variar conforme a semente, tamanho da população e número de gerações.",
    ]

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as file:
        file.write("\n".join(lines))
