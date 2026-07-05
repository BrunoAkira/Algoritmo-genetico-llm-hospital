from math import radians, sin, cos, sqrt, atan2
from src.models import Delivery, Vehicle


AVERAGE_SPEED_KMH = 35.0


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calcula a distância aproximada em quilômetros entre duas coordenadas geográficas."""
    earth_radius_km = 6371.0
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return earth_radius_km * c


def travel_time_minutes(distance_km: float, average_speed_kmh: float = AVERAGE_SPEED_KMH) -> float:
    """Converte distância em tempo estimado de deslocamento em minutos."""
    if average_speed_kmh <= 0:
        raise ValueError("A velocidade média deve ser maior que zero.")
    return (distance_km / average_speed_kmh) * 60


def point_for_delivery(delivery: Delivery) -> tuple[float, float]:
    """Retorna a latitude e longitude de uma entrega."""
    return delivery.lat, delivery.lon


def point_for_vehicle(vehicle: Vehicle) -> tuple[float, float]:
    """Retorna a latitude e longitude inicial de um veículo."""
    return vehicle.start_lat, vehicle.start_lon
