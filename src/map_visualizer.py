from pathlib import Path
import folium
from src.models import Delivery, Vehicle


PRIORITY_COLORS = {1: "green", 2: "orange", 3: "red"}
ROUTE_COLORS = ["blue", "purple", "cadetblue", "darkgreen", "darkred", "black"]


def create_routes_map(individual: list[list[int]], vehicles: list[Vehicle], deliveries: list[Delivery], output_path: str | Path) -> None:
    """Gera um mapa HTML com as rotas otimizadas por veículo."""
    deliveries_by_id = {delivery.id: delivery for delivery in deliveries}
    center_lat = vehicles[0].start_lat if vehicles else deliveries[0].lat
    center_lon = vehicles[0].start_lon if vehicles else deliveries[0].lon
    fmap = folium.Map(location=[center_lat, center_lon], zoom_start=11)

    for vehicle in vehicles:
        folium.Marker(
            location=[vehicle.start_lat, vehicle.start_lon],
            popup=f"Base - {vehicle.name}",
            icon=folium.Icon(color="blue", icon="home"),
        ).add_to(fmap)

    for delivery in deliveries:
        color = PRIORITY_COLORS.get(delivery.priority, "gray")
        popup = (
            f"<b>{delivery.name}</b><br>"
            f"Prioridade: {delivery.priority}<br>"
            f"Carga: {delivery.demand_kg} kg<br>"
            f"Prazo: {delivery.deadline_min} min"
        )
        folium.Marker(
            location=[delivery.lat, delivery.lon],
            popup=popup,
            icon=folium.Icon(color=color, icon="plus-sign"),
        ).add_to(fmap)

    for index, route in enumerate(individual):
        if not route:
            continue
        vehicle = vehicles[index]
        points = [[vehicle.start_lat, vehicle.start_lon]]
        points.extend([[deliveries_by_id[delivery_id].lat, deliveries_by_id[delivery_id].lon] for delivery_id in route])
        points.append([vehicle.start_lat, vehicle.start_lon])
        folium.PolyLine(
            locations=points,
            color=ROUTE_COLORS[index % len(ROUTE_COLORS)],
            weight=4,
            opacity=0.8,
            tooltip=f"Rota {vehicle.name}",
        ).add_to(fmap)

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    fmap.save(str(output_path))
