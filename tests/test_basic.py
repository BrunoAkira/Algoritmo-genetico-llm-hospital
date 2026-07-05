from src.data_loader import load_deliveries, load_vehicles
from src.genetic_algorithm import create_initial_individual, repair_individual


def test_individual_contains_all_deliveries_once():
    """Verifica se o indivíduo inicial contém todas as entregas uma única vez."""
    deliveries = load_deliveries("data/deliveries.csv")
    vehicles = load_vehicles("data/vehicles.csv")
    individual = create_initial_individual(deliveries, vehicles)
    ids = [delivery_id for route in individual for delivery_id in route]
    assert sorted(ids) == sorted(delivery.id for delivery in deliveries)


def test_repair_removes_duplicates_and_restores_missing():
    """Verifica se o reparo remove duplicatas e reinsere entregas ausentes."""
    deliveries = load_deliveries("data/deliveries.csv")
    broken = [[1, 1, 2], [3], []]
    repaired = repair_individual(broken, deliveries)
    ids = [delivery_id for route in repaired for delivery_id in route]
    assert sorted(ids) == sorted(delivery.id for delivery in deliveries)
