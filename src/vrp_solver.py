import random
from src.models import Delivery, Vehicle, RouteMetrics
from src.genetic_algorithm import Individual, create_population, evolve_population
from src.fitness import evaluate_individual


class VRPSolver:
    """Executa o algoritmo genético para resolver o problema de roteamento de veículos."""

    def __init__(
        self,
        deliveries: list[Delivery],
        vehicles: list[Vehicle],
        population_size: int = 100,
        generations: int = 300,
        elite_size: int = 5,
        mutation_rate: float = 0.25,
        seed: int | None = None,
    ) -> None:
        """Inicializa o solucionador com dados e parâmetros do algoritmo genético."""
        self.deliveries = deliveries
        self.vehicles = vehicles
        self.population_size = population_size
        self.generations = generations
        self.elite_size = elite_size
        self.mutation_rate = mutation_rate
        self.seed = seed
        self.history: list[float] = []

    def solve(self) -> tuple[Individual, float, list[RouteMetrics], list[float]]:
        """Executa as gerações do algoritmo e retorna a melhor solução encontrada."""
        if self.seed is not None:
            random.seed(self.seed)

        population = create_population(self.population_size, self.deliveries, self.vehicles)
        best_individual = population[0]
        best_cost, best_metrics = evaluate_individual(best_individual, self.vehicles, self.deliveries)

        for _ in range(self.generations):
            population = evolve_population(
                population=population,
                vehicles=self.vehicles,
                deliveries=self.deliveries,
                elite_size=self.elite_size,
                mutation_rate=self.mutation_rate,
            )
            current_best = min(population, key=lambda ind: evaluate_individual(ind, self.vehicles, self.deliveries)[0])
            current_cost, current_metrics = evaluate_individual(current_best, self.vehicles, self.deliveries)
            self.history.append(current_cost)
            if current_cost < best_cost:
                best_individual = current_best
                best_cost = current_cost
                best_metrics = current_metrics

        return best_individual, best_cost, best_metrics, self.history
