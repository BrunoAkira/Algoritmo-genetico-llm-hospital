import argparse
from pathlib import Path
from src.data_loader import load_deliveries, load_vehicles
from src.vrp_solver import VRPSolver
from src.report_generator import build_routes_payload, save_routes_json, generate_markdown_report
from src.map_visualizer import create_routes_map
from src.charts import plot_fitness_history, plot_vehicle_distances, plot_priority_distribution
from src.llm_service import LocalLLMService


def parse_args() -> argparse.Namespace:
    """Lê os parâmetros de execução informados no terminal."""
    parser = argparse.ArgumentParser(description="Otimizador local de rotas médicas com Algoritmo Genético.")
    parser.add_argument("--deliveries", default="data/deliveries.csv", help="Caminho do CSV de entregas.")
    parser.add_argument("--vehicles", default="data/vehicles.csv", help="Caminho do CSV de veículos.")
    parser.add_argument("--population-size", type=int, default=120, help="Tamanho da população genética.")
    parser.add_argument("--generations", type=int, default=400, help="Quantidade de gerações do algoritmo.")
    parser.add_argument("--elite-size", type=int, default=6, help="Quantidade de indivíduos preservados por elitismo.")
    parser.add_argument("--mutation-rate", type=float, default=0.30, help="Taxa de mutação por indivíduo.")
    parser.add_argument("--seed", type=int, default=42, help="Semente aleatória para reprodutibilidade.")
    return parser.parse_args()


def main() -> None:
    """Executa o fluxo completo de otimização, visualização e geração de relatórios."""
    args = parse_args()
    output_dir = Path("outputs")
    output_dir.mkdir(exist_ok=True)

    deliveries = load_deliveries(args.deliveries)
    vehicles = load_vehicles(args.vehicles)

    solver = VRPSolver(
        deliveries=deliveries,
        vehicles=vehicles,
        population_size=args.population_size,
        generations=args.generations,
        elite_size=args.elite_size,
        mutation_rate=args.mutation_rate,
        seed=args.seed,
    )
    best_individual, best_cost, metrics, history = solver.solve()
    payload = build_routes_payload(best_individual, vehicles, deliveries, metrics, best_cost)

    save_routes_json(payload, output_dir / "routes.json")
    generate_markdown_report(payload, output_dir / "daily_report.md")
    create_routes_map(best_individual, vehicles, deliveries, output_dir / "routes_map.html")
    plot_fitness_history(history, output_dir / "fitness_evolution.png")
    plot_vehicle_distances(metrics, output_dir / "vehicle_distance.png")
    plot_priority_distribution(deliveries, output_dir / "priority_distribution.png")

    llm = LocalLLMService()
    with open(output_dir / "driver_instructions.md", "w", encoding="utf-8") as file:
        file.write("# Instruções para Motoristas\n\n")
        for route in payload["routes"]:
            file.write(f"- {llm.generate_driver_instructions(route)}\n")
        file.write("\n## Resumo operacional\n\n")
        file.write(llm.generate_operations_summary(payload) + "\n")
        file.write("\n## Sugestões de melhoria\n\n")
        for suggestion in llm.suggest_improvements(payload):
            file.write(f"- {suggestion}\n")

    print("Otimização concluída.")
    print(f"Custo total: {best_cost:.2f}")
    print("Arquivos gerados em outputs/.")


if __name__ == "__main__":
    main()
