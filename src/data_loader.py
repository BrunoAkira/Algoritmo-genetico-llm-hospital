from pathlib import Path
import pandas as pd
from src.models import Delivery, Vehicle


def load_deliveries(path: str | Path) -> list[Delivery]:
    """Carrega as entregas a partir de um arquivo CSV."""
    df = pd.read_csv(path)
    return [
        Delivery(
            id=int(row.id),
            name=str(row.name),
            lat=float(row.lat),
            lon=float(row.lon),
            demand_kg=float(row.demand_kg),
            priority=int(row.priority),
            service_time_min=float(row.service_time_min),
            deadline_min=float(row.deadline_min),
        )
        for row in df.itertuples(index=False)
    ]


def load_vehicles(path: str | Path) -> list[Vehicle]:
    """Carrega os veículos a partir de um arquivo CSV."""
    df = pd.read_csv(path)
    return [
        Vehicle(
            id=int(row.id),
            name=str(row.name),
            capacity_kg=float(row.capacity_kg),
            max_distance_km=float(row.max_distance_km),
            start_lat=float(row.start_lat),
            start_lon=float(row.start_lon),
        )
        for row in df.itertuples(index=False)
    ]
