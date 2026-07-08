from pathlib import Path

from src.data_loader import load_deliveries, load_vehicles
from src.fitness import evaluate_individual
from src.genetic_algorithm import create_initial_individual, repair_individual, crossover, mutate
from src.prompts import build_driver_instructions_prompt, build_operations_report_prompt, build_question_prompt
from src.report_generator import build_routes_payload, save_routes_json
from src.vrp_solver import VRPSolver


def test_load_input_files():
    """Verifica se os arquivos CSV principais são carregados corretamente."""
    deliveries = load_deliveries("data/deliveries.csv")
    vehicles = load_vehicles("data/vehicles.csv")

    assert len(deliveries) > 0
    assert len(vehicles) > 0
    assert all(delivery.priority in (1, 2, 3) for delivery in deliveries)
    assert all(vehicle.capacity_kg > 0 for vehicle in vehicles)


def test_individual_contains_all_deliveries_once():
    """Verifica se o indivíduo inicial contém todas as entregas exatamente uma vez."""
    deliveries = load_deliveries("data/deliveries.csv")
    vehicles = load_vehicles("data/vehicles.csv")
    individual = create_initial_individual(deliveries, vehicles)

    ids = [delivery_id for route in individual for delivery_id in route]

    assert len(individual) == len(vehicles)
    assert sorted(ids) == sorted(delivery.id for delivery in deliveries)


def test_repair_removes_duplicates_and_restores_missing():
    """Verifica se o reparo remove duplicatas e reinsere entregas ausentes."""
    deliveries = load_deliveries("data/deliveries.csv")
    broken = [[1, 1, 2], [3], []]
    repaired = repair_individual(broken, deliveries)

    ids = [delivery_id for route in repaired for delivery_id in route]

    assert sorted(ids) == sorted(delivery.id for delivery in deliveries)
    assert len(ids) == len(set(ids))


def test_crossover_and_mutation_keep_valid_individual_after_repair():
    """Valida que crossover e mutação continuam gerando soluções reparáveis e completas."""
    deliveries = load_deliveries("data/deliveries.csv")
    vehicles = load_vehicles("data/vehicles.csv")
    parent_a = create_initial_individual(deliveries, vehicles)
    parent_b = create_initial_individual(deliveries, vehicles)

    child = crossover(parent_a, parent_b, len(vehicles))
    child = mutate(child, mutation_rate=1.0)
    child = repair_individual(child, deliveries)
    ids = [delivery_id for route in child for delivery_id in route]

    assert sorted(ids) == sorted(delivery.id for delivery in deliveries)


def test_fitness_penalizes_invalid_routes():
    """Compara uma rota válida com uma rota duplicada para confirmar penalização de cromossomos inválidos."""
    deliveries = load_deliveries("data/deliveries.csv")
    vehicles = load_vehicles("data/vehicles.csv")
    valid = create_initial_individual(deliveries, vehicles)
    invalid = [route[:] for route in valid]

    invalid[0].append(valid[0][0])

    valid_cost, _ = evaluate_individual(valid, vehicles, deliveries)
    invalid_cost, _ = evaluate_individual(invalid, vehicles, deliveries)

    assert invalid_cost > valid_cost


def test_solver_runs_and_returns_history():
    """Executa poucas gerações para validar o fluxo principal do Algoritmo Genético."""
    deliveries = load_deliveries("data/deliveries.csv")
    vehicles = load_vehicles("data/vehicles.csv")
    solver = VRPSolver(deliveries, vehicles, population_size=12, generations=5, elite_size=2, mutation_rate=0.3, seed=123)

    best_individual, best_cost, metrics, history = solver.solve()

    assert best_cost > 0
    assert len(best_individual) == len(vehicles)
    assert len(metrics) == len(vehicles)
    assert len(history) == 5


def test_payload_and_json_generation(tmp_path):
    """Valida se o resultado estruturado pode ser montado e salvo em JSON."""
    deliveries = load_deliveries("data/deliveries.csv")
    vehicles = load_vehicles("data/vehicles.csv")
    individual = create_initial_individual(deliveries, vehicles)
    cost, metrics = evaluate_individual(individual, vehicles, deliveries)
    payload = build_routes_payload(individual, vehicles, deliveries, metrics, cost)
    output_file = tmp_path / "routes.json"

    save_routes_json(payload, output_file)

    assert output_file.exists()
    assert "routes" in payload
    assert len(payload["routes"]) == len(vehicles)


def test_prompts_contain_required_context():
    """Garante que os prompts da LLM carregam os dados e orientam respostas em português."""
    payload = {"total_cost": 10, "routes": [{"vehicle_name": "Veículo 1", "stops": []}]}

    driver_prompt = build_driver_instructions_prompt(payload)
    report_prompt = build_operations_report_prompt(payload)
    question_prompt = build_question_prompt(payload, "Qual veículo está vazio?")

    assert "motoristas" in driver_prompt.lower()
    assert "relatório operacional" in report_prompt.lower()
    assert "Qual veículo está vazio?" in question_prompt
    assert "Veículo 1" in question_prompt


from src.baseline import build_nearest_neighbor_solution, generate_performance_comparison


def test_baseline_comparison_file_is_generated(tmp_path):
    """Garante que o comparativo de desempenho com uma abordagem alternativa é gerado."""
    deliveries = load_deliveries("data/deliveries.csv")
    vehicles = load_vehicles("data/vehicles.csv")
    baseline = build_nearest_neighbor_solution(deliveries, vehicles)
    cost, _ = evaluate_individual(baseline, vehicles, deliveries)
    output_file = tmp_path / "performance_comparison.md"

    generate_performance_comparison(baseline, cost, deliveries, vehicles, output_file)

    content = output_file.read_text(encoding="utf-8")
    assert output_file.exists()
    assert "Comparativo de Desempenho" in content
    assert "Vizinho mais próximo" in content

from types import SimpleNamespace
from unittest.mock import patch

from run import ask_about_routes, generate_llm_reports, run_optimization


def test_run_optimization_generates_main_outputs(tmp_path):
    """Valida que o run.py centralizado executa a otimização e gera os principais arquivos."""
    args = SimpleNamespace(
        deliveries="data/deliveries.csv",
        vehicles="data/vehicles.csv",
        population_size=12,
        generations=5,
        elite_size=2,
        mutation_rate=0.3,
        seed=7,
        output_dir=str(tmp_path),
        llm=False,
    )

    payload = run_optimization(args)

    assert "routes" in payload
    assert (tmp_path / "routes.json").exists()
    assert (tmp_path / "daily_report.md").exists()
    assert (tmp_path / "driver_instructions.md").exists()
    assert (tmp_path / "performance_comparison.md").exists()


def test_run_ask_about_routes_delegates_to_llm(tmp_path):
    """Garante que perguntas em linguagem natural são delegadas para a LLM via run.py."""
    payload = {"total_cost": 100, "routes": [{"vehicle_name": "Van 1", "distance_km": 12, "stops": []}]}
    output_file = tmp_path / "routes.json"
    save_routes_json(payload, output_file)

    with patch("run.answer_question_with_llm", return_value="Resposta gerada pela LLM") as mocked_answer:
        response = ask_about_routes(
            question="Qual veículo percorreu a maior distância?",
            routes_path=output_file,
            model="llama3.2",
            ollama_url="http://localhost:11434",
        )

    assert response == "Resposta gerada pela LLM"
    mocked_answer.assert_called_once()


def test_run_llm_report_delegates_to_ollama_service(tmp_path):
    """Confirma que o run.py chama o serviço de LLM sem precisar conectar ao Ollama durante o teste."""
    payload = {"total_cost": 100, "routes": []}
    routes_file = tmp_path / "routes.json"
    save_routes_json(payload, routes_file)

    with patch("run.generate_ollama_outputs") as mocked_generate:
        generate_llm_reports(routes_file, tmp_path, model="llama3.2", ollama_url="http://localhost:11434")

    mocked_generate.assert_called_once()
