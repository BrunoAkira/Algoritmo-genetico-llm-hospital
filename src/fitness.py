from src.distance import haversine_km, travel_time_minutes
from src.models import Delivery, Vehicle, RouteMetrics


PENALTY_CAPACITY = 120.0
PENALTY_AUTONOMY = 150.0
PENALTY_LATE = 50.0
PENALTY_PRIORITY_DELAY = 4.0
PENALTY_VEHICLE_USED = 2.0


def route_metrics(route: list[int], vehicle: Vehicle, deliveries_by_id: dict[int, Delivery]) -> RouteMetrics:
    """Calcula distância, carga, atrasos e violações de uma rota específica."""
    current_lat = vehicle.start_lat
    current_lon = vehicle.start_lon
    distance_km = 0.0
    elapsed_min = 0.0
    load_kg = 0.0
    late_deliveries = 0
    priority_delay_score = 0.0

    for delivery_id in route:
        delivery = deliveries_by_id[delivery_id]
        leg_km = haversine_km(current_lat, current_lon, delivery.lat, delivery.lon)
        distance_km += leg_km
        elapsed_min += travel_time_minutes(leg_km)
        load_kg += delivery.demand_kg

        delay = max(0.0, elapsed_min - delivery.deadline_min)
        if delay > 0:
            late_deliveries += 1
            priority_delay_score += delay * delivery.priority

        elapsed_min += delivery.service_time_min
        current_lat = delivery.lat
        current_lon = delivery.lon

    return_km = haversine_km(current_lat, current_lon, vehicle.start_lat, vehicle.start_lon)
    distance_km += return_km
    elapsed_min += travel_time_minutes(return_km)

    return RouteMetrics(
        vehicle_id=vehicle.id,
        distance_km=distance_km,
        load_kg=load_kg,
        travel_time_min=travel_time_minutes(distance_km),
        total_time_min=elapsed_min,
        capacity_excess_kg=max(0.0, load_kg - vehicle.capacity_kg),
        autonomy_excess_km=max(0.0, distance_km - vehicle.max_distance_km),
        late_deliveries=late_deliveries,
        priority_delay_score=priority_delay_score,
    )


def evaluate_individual(individual: list[list[int]], vehicles: list[Vehicle], deliveries: list[Delivery]) -> tuple[float, list[RouteMetrics]]:
    """Avalia um indivíduo e retorna o custo total e as métricas por veículo."""
    deliveries_by_id = {delivery.id: delivery for delivery in deliveries}
    total_cost = 0.0
    metrics: list[RouteMetrics] = []

    for route, vehicle in zip(individual, vehicles):
        metric = route_metrics(route, vehicle, deliveries_by_id)
        metrics.append(metric)
        vehicle_used = 1 if route else 0
        total_cost += metric.distance_km
        total_cost += metric.capacity_excess_kg * PENALTY_CAPACITY
        total_cost += metric.autonomy_excess_km * PENALTY_AUTONOMY
        total_cost += metric.late_deliveries * PENALTY_LATE
        total_cost += metric.priority_delay_score * PENALTY_PRIORITY_DELAY
        total_cost += vehicle_used * PENALTY_VEHICLE_USED

    total_cost += missing_or_duplicated_penalty(individual, deliveries)
    return total_cost, metrics


def missing_or_duplicated_penalty(individual: list[list[int]], deliveries: list[Delivery]) -> float:
    """Penaliza cromossomos que perderam entregas ou duplicaram entregas."""
    expected_ids = {delivery.id for delivery in deliveries}
    actual_ids = [delivery_id for route in individual for delivery_id in route]
    actual_set = set(actual_ids)
    missing = len(expected_ids - actual_set)
    duplicated = len(actual_ids) - len(actual_set)
    return (missing + duplicated) * 10000.0
