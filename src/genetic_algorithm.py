import random
from copy import deepcopy
from src.models import Delivery, Vehicle
from src.fitness import evaluate_individual


Individual = list[list[int]]


def create_initial_individual(deliveries: list[Delivery], vehicles: list[Vehicle]) -> Individual:
    """Cria um indivíduo inicial distribuindo entregas entre os veículos disponíveis."""
    delivery_ids = [delivery.id for delivery in deliveries]
    random.shuffle(delivery_ids)
    individual: Individual = [[] for _ in vehicles]
    for index, delivery_id in enumerate(delivery_ids):
        individual[index % len(vehicles)].append(delivery_id)
    return individual


def create_population(size: int, deliveries: list[Delivery], vehicles: list[Vehicle]) -> list[Individual]:
    """Cria a população inicial com indivíduos aleatórios."""
    return [create_initial_individual(deliveries, vehicles) for _ in range(size)]


def flatten_individual(individual: Individual) -> list[int]:
    """Transforma rotas de múltiplos veículos em uma sequência única de entregas."""
    return [delivery_id for route in individual for delivery_id in route]


def split_sequence(sequence: list[int], route_sizes: list[int], vehicle_count: int) -> Individual:
    """Reconstrói rotas de veículos a partir de uma sequência única e tamanhos de rota."""
    routes: Individual = []
    cursor = 0
    for size in route_sizes[:vehicle_count]:
        routes.append(sequence[cursor:cursor + size])
        cursor += size
    while len(routes) < vehicle_count:
        routes.append([])
    remaining = sequence[cursor:]
    for index, delivery_id in enumerate(remaining):
        routes[index % vehicle_count].append(delivery_id)
    return routes


def tournament_selection(population: list[Individual], vehicles: list[Vehicle], deliveries: list[Delivery], tournament_size: int = 4) -> Individual:
    """Seleciona um indivíduo por torneio, favorecendo os menores custos."""
    competitors = random.sample(population, k=min(tournament_size, len(population)))
    competitors.sort(key=lambda ind: evaluate_individual(ind, vehicles, deliveries)[0])
    return deepcopy(competitors[0])


def order_crossover_sequence(parent_a: list[int], parent_b: list[int]) -> list[int]:
    """Aplica crossover OX em duas sequências de entregas sem repetir genes."""
    if len(parent_a) <= 2:
        return parent_a[:]
    start, end = sorted(random.sample(range(len(parent_a)), 2))
    child = [None] * len(parent_a)
    # O trecho central vem do primeiro pai; o restante é preenchido na ordem do segundo pai.
    child[start:end] = parent_a[start:end]
    fill_values = [gene for gene in parent_b if gene not in child]
    fill_index = 0
    for index in range(len(child)):
        if child[index] is None:
            child[index] = fill_values[fill_index]
            fill_index += 1
    return child


def crossover(parent_a: Individual, parent_b: Individual, vehicle_count: int) -> Individual:
    """Combina dois indivíduos usando OX na sequência e herança parcial de tamanhos de rota."""
    seq_a = flatten_individual(parent_a)
    seq_b = flatten_individual(parent_b)
    child_sequence = order_crossover_sequence(seq_a, seq_b)
    sizes_a = [len(route) for route in parent_a]
    sizes_b = [len(route) for route in parent_b]
    # Além da ordem das entregas, herdamos parcialmente a divisão entre veículos.
    child_sizes = [random.choice([a, b]) for a, b in zip(sizes_a, sizes_b)]
    return split_sequence(child_sequence, child_sizes, vehicle_count)


def mutate_swap(individual: Individual) -> None:
    """Troca duas entregas de posição, podendo ser na mesma rota ou em rotas diferentes."""
    non_empty_routes = [index for index, route in enumerate(individual) if route]
    if len(non_empty_routes) == 0:
        return
    route_a_index = random.choice(non_empty_routes)
    route_b_index = random.choice(non_empty_routes)
    route_a = individual[route_a_index]
    route_b = individual[route_b_index]
    pos_a = random.randrange(len(route_a))
    pos_b = random.randrange(len(route_b))
    route_a[pos_a], route_b[pos_b] = route_b[pos_b], route_a[pos_a]


def mutate_invert(individual: Individual) -> None:
    """Inverte um trecho de uma rota para explorar ordens alternativas de entrega."""
    candidate_routes = [route for route in individual if len(route) >= 3]
    if not candidate_routes:
        return
    route = random.choice(candidate_routes)
    start, end = sorted(random.sample(range(len(route)), 2))
    route[start:end + 1] = reversed(route[start:end + 1])


def mutate_move(individual: Individual) -> None:
    """Move uma entrega de um veículo para outro, alterando a divisão de carga."""
    source_indexes = [index for index, route in enumerate(individual) if route]
    if not source_indexes:
        return
    source_index = random.choice(source_indexes)
    target_index = random.randrange(len(individual))
    delivery = individual[source_index].pop(random.randrange(len(individual[source_index])))
    insert_pos = random.randrange(len(individual[target_index]) + 1)
    individual[target_index].insert(insert_pos, delivery)


def mutate(individual: Individual, mutation_rate: float) -> Individual:
    """Aplica mutações especializadas em um indivíduo conforme a taxa informada."""
    mutated = deepcopy(individual)
    if random.random() < mutation_rate:
        random.choice([mutate_swap, mutate_invert, mutate_move])(mutated)
    return mutated


def repair_individual(individual: Individual, deliveries: list[Delivery]) -> Individual:
    """Corrige um indivíduo removendo duplicatas e reinserindo entregas ausentes."""
    expected_ids = [delivery.id for delivery in deliveries]
    expected_set = set(expected_ids)
    seen = set()
    repaired: Individual = []
    for route in individual:
        new_route = []
        for delivery_id in route:
            if delivery_id in expected_set and delivery_id not in seen:
                new_route.append(delivery_id)
                seen.add(delivery_id)
        repaired.append(new_route)
    missing = [delivery_id for delivery_id in expected_ids if delivery_id not in seen]
    for index, delivery_id in enumerate(missing):
        repaired[index % len(repaired)].append(delivery_id)
    return repaired


def evolve_population(population: list[Individual], vehicles: list[Vehicle], deliveries: list[Delivery], elite_size: int, mutation_rate: float) -> list[Individual]:
    """Gera uma nova população preservando elite e criando descendentes por crossover e mutação."""
    # Elitismo: mantém as melhores soluções para não perder bons resultados entre gerações.
    ranked = sorted(population, key=lambda ind: evaluate_individual(ind, vehicles, deliveries)[0])
    next_population = [deepcopy(ind) for ind in ranked[:elite_size]]
    while len(next_population) < len(population):
        parent_a = tournament_selection(ranked, vehicles, deliveries)
        parent_b = tournament_selection(ranked, vehicles, deliveries)
        child = crossover(parent_a, parent_b, len(vehicles))
        child = mutate(child, mutation_rate)
        # O reparo garante que nenhuma entrega seja perdida ou duplicada após crossover/mutação.
        child = repair_individual(child, deliveries)
        next_population.append(child)
    return next_population
