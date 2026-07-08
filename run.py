import argparse
from pathlib import Path

from src.baseline import generate_performance_comparison
from src.charts import plot_fitness_history, plot_priority_distribution, plot_vehicle_distances
from src.data_loader import load_deliveries, load_vehicles
from src.llm_service import generate_ollama_outputs, generate_rule_based_driver_file
from src.map_visualizer import create_routes_map
from src.qa_service import answer_question, answer_question_with_llm, load_payload
from src.report_generator import build_routes_payload, generate_markdown_report, save_routes_json
from src.vrp_solver import VRPSolver


DEFAULT_OUTPUT_DIR = Path("outputs")


def add_optimization_arguments(parser: argparse.ArgumentParser) -> None:
    """Adiciona ao parser os parâmetros usados na execução do Algoritmo Genético."""
    parser.add_argument("--deliveries", default="data/deliveries.csv", help="Caminho do CSV de entregas.")
    parser.add_argument("--vehicles", default="data/vehicles.csv", help="Caminho do CSV de veículos.")
    parser.add_argument("--population-size", type=int, default=120, help="Tamanho da população genética.")
    parser.add_argument("--generations", type=int, default=400, help="Quantidade de gerações do algoritmo.")
    parser.add_argument("--elite-size", type=int, default=6, help="Quantidade de indivíduos preservados por elitismo.")
    parser.add_argument("--mutation-rate", type=float, default=0.30, help="Taxa de mutação por indivíduo.")
    parser.add_argument("--seed", type=int, default=42, help="Semente aleatória para reprodutibilidade.")
    parser.add_argument("--output-dir", default="outputs", help="Pasta onde os arquivos serão gerados.")


def add_llm_arguments(parser: argparse.ArgumentParser) -> None:
    """Adiciona parâmetros de configuração da LLM local executada pelo Ollama."""
    parser.add_argument("--llm", action="store_true", help="Usa LLM local via Ollama quando aplicável.")
    parser.add_argument("--llm-model", default="llama3.2", help="Modelo local do Ollama, por exemplo llama3.2.")
    parser.add_argument("--ollama-url", default="http://localhost:11434", help="URL local da API do Ollama.")


def parse_args() -> argparse.Namespace:
    """Lê os argumentos do terminal e organiza os modos do sistema em um único arquivo run.py."""
    parser = argparse.ArgumentParser(
        description="Sistema local de otimização de rotas hospitalares com AG e LLM via Ollama."
    )
    subparsers = parser.add_subparsers(dest="command")

    optimize_parser = subparsers.add_parser("optimize", help="Executa o Algoritmo Genético e gera os artefatos.")
    add_optimization_arguments(optimize_parser)
    add_llm_arguments(optimize_parser)

    report_parser = subparsers.add_parser("llm-report", help="Gera relatórios com LLM a partir do routes.json.")
    report_parser.add_argument("--routes", default="outputs/routes.json", help="Arquivo JSON gerado pela otimização.")
    report_parser.add_argument("--output-dir", default="outputs", help="Pasta onde os relatórios da LLM serão salvos.")
    add_llm_arguments(report_parser)

    ask_parser = subparsers.add_parser("ask", help="Responde perguntas sobre rotas usando regras locais ou LLM.")
    ask_parser.add_argument("question", help="Pergunta em linguagem natural sobre as rotas.")
    ask_parser.add_argument("--routes", default="outputs/routes.json", help="Arquivo JSON gerado pela otimização.")
    add_llm_arguments(ask_parser)

    menu_parser = subparsers.add_parser("menu", help="Abre um menu interativo para demonstração local.")
    add_optimization_arguments(menu_parser)
    add_llm_arguments(menu_parser)

    # Compatibilidade com o modo antigo: `python run.py --generations 10` continua executando a otimização.
    add_optimization_arguments(parser)
    add_llm_arguments(parser)

    args = parser.parse_args()
    if args.command is None:
        args.command = "optimize"
    return args


def run_optimization(args: argparse.Namespace) -> dict:
    """Executa o Algoritmo Genético, salva mapa/gráficos/relatórios e retorna o payload das rotas."""
    output_dir = Path(args.output_dir)
    output_dir.mkdir(exist_ok=True)

    # Entrada do problema: entregas e veículos são carregados de CSV para facilitar testes e ajustes.
    deliveries = load_deliveries(args.deliveries)
    vehicles = load_vehicles(args.vehicles)

    # VRPSolver encapsula o Algoritmo Genético aplicado ao problema de múltiplos veículos.
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

    # O routes.json é o contrato entre otimização, relatórios, visualizações e LLM.
    payload = build_routes_payload(best_individual, vehicles, deliveries, metrics, best_cost)
    save_routes_json(payload, output_dir / "routes.json")

    # Artefatos locais sem LLM: mapa, gráficos e relatórios determinísticos.
    generate_markdown_report(payload, output_dir / "daily_report.md")
    create_routes_map(best_individual, vehicles, deliveries, output_dir / "routes_map.html")
    plot_fitness_history(history, output_dir / "fitness_evolution.png")
    plot_vehicle_distances(metrics, output_dir / "vehicle_distance.png")
    plot_priority_distribution(deliveries, output_dir / "priority_distribution.png")
    generate_rule_based_driver_file(payload, output_dir / "driver_instructions.md")

    # Comparativo obrigatório para demonstrar desempenho contra uma abordagem simples.
    generate_performance_comparison(
        ga_individual=best_individual,
        ga_cost=best_cost,
        deliveries=deliveries,
        vehicles=vehicles,
        output_path=output_dir / "performance_comparison.md",
    )

    if getattr(args, "llm", False):
        # Atende à integração com LLM usando Ollama local, sem API paga.
        generate_llm_reports(output_dir / "routes.json", output_dir, args.llm_model, args.ollama_url)

    print("Otimização concluída.")
    print(f"Custo total: {best_cost:.2f}")
    print(f"Arquivos gerados em {output_dir}/.")
    return payload


def generate_llm_reports(routes_path: str | Path, output_dir: str | Path, model: str, ollama_url: str) -> None:
    """Lê o routes.json e gera relatórios/instruções/sugestões usando a LLM local via Ollama."""
    payload = load_payload(routes_path)
    generate_ollama_outputs(payload=payload, output_dir=Path(output_dir), model=model, base_url=ollama_url)
    print("Relatórios com LLM gerados.")


def ask_about_routes(question: str, routes_path: str | Path, use_llm: bool, model: str, ollama_url: str) -> str:
    """Responde uma pergunta sobre as rotas usando regras locais ou LLM, conforme a opção escolhida."""
    payload = load_payload(routes_path)
    if use_llm:
        return answer_question_with_llm(question, payload, model=model, base_url=ollama_url)
    return answer_question(question, payload)


def run_interactive_menu(args: argparse.Namespace) -> None:
    """Exibe um menu simples no terminal para demonstrar otimização, LLM e perguntas em um único programa."""
    output_dir = Path(args.output_dir)
    routes_path = output_dir / "routes.json"

    while True:
        print("\n=== Sistema de Otimização de Rotas Hospitalares ===")
        print("1 - Executar Algoritmo Genético e gerar artefatos")
        print("2 - Gerar relatórios com LLM local (Ollama)")
        print("3 - Perguntar sobre as rotas sem LLM")
        print("4 - Perguntar sobre as rotas com LLM local (Ollama)")
        print("5 - Sair")
        option = input("Escolha uma opção: ").strip()

        if option == "1":
            run_optimization(args)
        elif option == "2":
            generate_llm_reports(routes_path, output_dir, args.llm_model, args.ollama_url)
        elif option in {"3", "4"}:
            question = input("Digite sua pergunta: ").strip()
            if not question:
                print("Pergunta vazia. Tente novamente.")
                continue
            response = ask_about_routes(
                question=question,
                routes_path=routes_path,
                use_llm=(option == "4"),
                model=args.llm_model,
                ollama_url=args.ollama_url,
            )
            print("\nResposta:")
            print(response)
        elif option == "5":
            print("Encerrando.")
            break
        else:
            print("Opção inválida.")


def main() -> None:
    """Direciona a execução para otimização, relatórios LLM, perguntas ou menu interativo."""
    args = parse_args()

    if args.command == "optimize":
        run_optimization(args)
    elif args.command == "llm-report":
        generate_llm_reports(args.routes, args.output_dir, args.llm_model, args.ollama_url)
    elif args.command == "ask":
        print(ask_about_routes(args.question, args.routes, args.llm, args.llm_model, args.ollama_url))
    elif args.command == "menu":
        run_interactive_menu(args)


if __name__ == "__main__":
    main()
