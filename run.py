import argparse
from pathlib import Path
from src.data_loader import load_deliveries, load_vehicles
from src.vrp_solver import VRPSolver
from src.report_generator import build_routes_payload, save_routes_json, generate_markdown_report
from src.baseline import generate_performance_comparison
from src.map_visualizer import create_routes_map
from src.charts import plot_fitness_history, plot_vehicle_distances, plot_priority_distribution
from src.llm_service import generate_ollama_outputs, generate_rule_based_driver_file


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
    parser.add_argument("--use-llm", action="store_true", help="Gera relatórios com LLM local via Ollama.")
    parser.add_argument("--llm-model", default="llama3.2", help="Modelo local do Ollama usado na geração dos textos.")
    parser.add_argument("--ollama-url", default="http://localhost:11434", help="URL local da API do Ollama.")
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

    # Sempre gera um arquivo de instruções por regras para que o projeto funcione sem dependências externas.
    generate_rule_based_driver_file(payload, output_dir / "driver_instructions.md")

    # Gera um comparativo com uma heurística simples, requisito importante para analisar desempenho.
    generate_performance_comparison(
        ga_individual=best_individual,
        ga_cost=best_cost,
        deliveries=deliveries,
        vehicles=vehicles,
        output_path=output_dir / "performance_comparison.md",
    )

    if args.use_llm:
        # Quando habilitado, este bloco atende ao requisito de utilizar uma LLM pré-treinada.
        # A integração usa Ollama local, portanto não exige API paga nem chave da OpenAI.
        generate_ollama_outputs(
            payload=payload,
            output_dir=output_dir,
            model=args.llm_model,
            base_url=args.ollama_url,
        )

    print("Otimização concluída.")
    print(f"Custo total: {best_cost:.2f}")
    print("Arquivos gerados em outputs/.")


if __name__ == "__main__":
    main()
