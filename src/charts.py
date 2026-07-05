from pathlib import Path
from collections import Counter
import matplotlib.pyplot as plt
from src.models import Delivery, RouteMetrics


def plot_fitness_history(history: list[float], output_path: str | Path) -> None:
    """Gera o gráfico de evolução do custo do melhor indivíduo ao longo das gerações."""
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    plt.figure()
    plt.plot(range(1, len(history) + 1), history)
    plt.xlabel("Geração")
    plt.ylabel("Custo da melhor solução")
    plt.title("Evolução do Algoritmo Genético")
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()


def plot_vehicle_distances(metrics: list[RouteMetrics], output_path: str | Path) -> None:
    """Gera um gráfico de barras com a distância percorrida por veículo."""
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    labels = [f"V{metric.vehicle_id}" for metric in metrics]
    values = [metric.distance_km for metric in metrics]
    plt.figure()
    plt.bar(labels, values)
    plt.xlabel("Veículo")
    plt.ylabel("Distância em km")
    plt.title("Distância por Veículo")
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()


def plot_priority_distribution(deliveries: list[Delivery], output_path: str | Path) -> None:
    """Gera um gráfico com a quantidade de entregas por nível de prioridade."""
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    counts = Counter(delivery.priority for delivery in deliveries)
    labels = ["Regular", "Alta", "Crítica"]
    values = [counts.get(1, 0), counts.get(2, 0), counts.get(3, 0)]
    plt.figure()
    plt.bar(labels, values)
    plt.xlabel("Prioridade")
    plt.ylabel("Quantidade de entregas")
    plt.title("Distribuição de Prioridades")
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()
