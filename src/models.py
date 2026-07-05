from dataclasses import dataclass


@dataclass(frozen=True)
class Delivery:
    """Representa uma entrega de medicamento ou insumo."""
    id: int
    name: str
    lat: float
    lon: float
    demand_kg: float
    priority: int
    service_time_min: float
    deadline_min: float


@dataclass(frozen=True)
class Vehicle:
    """Representa um veículo disponível para realizar entregas."""
    id: int
    name: str
    capacity_kg: float
    max_distance_km: float
    start_lat: float
    start_lon: float


@dataclass
class RouteMetrics:
    """Armazena indicadores calculados para uma rota de veículo."""
    vehicle_id: int
    distance_km: float
    load_kg: float
    travel_time_min: float
    total_time_min: float
    capacity_excess_kg: float
    autonomy_excess_km: float
    late_deliveries: int
    priority_delay_score: float
