# Arquitetura do Sistema de Otimização de Rotas

## Visão geral

O sistema possui duas camadas principais:

1. **Camada de otimização**, responsável por calcular rotas usando Algoritmo Genético.
2. **Camada de interpretação**, responsável por usar uma LLM local via Ollama para gerar instruções, relatórios, sugestões e respostas em linguagem natural.

A LLM não substitui o algoritmo de otimização. Ela recebe o resultado estruturado em `outputs/routes.json` e interpreta esse resultado.

---

## Diagrama geral

```text
                 +----------------------+
                 |        run.py        |
                 +----------+-----------+
                            |
        +-------------------+--------------------+
        |                   |                    |
        v                   v                    v
  optimize              llm-report               ask
  (AG + artefatos)      (relatórios LLM)         (perguntas LLM)
        |                   |                    |
        v                   |                    |
+------------------+        |                    |
| Leitura dos CSVs |        |                    |
| data_loader.py   |        |                    |
+--------+---------+        |                    |
         |                  |                    |
         v                  |                    |
+------------------+        |                    |
| VRPSolver        |        |                    |
| vrp_solver.py    |        |                    |
+--------+---------+        |                    |
         |                  |                    |
         v                  |                    |
+-------------------------+ |                    |
| Algoritmo Genético      | |                    |
| genetic_algorithm.py    | |                    |
| - seleção               | |                    |
| - crossover             | |                    |
| - mutação               | |                    |
| - elitismo              | |                    |
+------------+------------+ |                    |
             |              |                    |
             v              |                    |
+-------------------------+ |                    |
| Função fitness          | |                    |
| fitness.py              | |                    |
| - distância             | |                    |
| - prioridade            | |                    |
| - capacidade            | |                    |
| - autonomia             | |                    |
| - atrasos               | |                    |
+------------+------------+ |                    |
             |              |                    |
             v              |                    |
+-------------------------+ |                    |
| Melhor solução VRP      | |                    |
+------------+------------+ |                    |
             |              |                    |
             v              v                    v
        outputs/routes.json ----------------> qa_service.py
             |                                         |
             |                                         v
             |                                  prompts.py
             |                                         |
             v                                         v
+-------------------------+          +-------------------------+
| Artefatos técnicos      |          | llm_service.py          |
| - routes_map.html       |          | chamada HTTP ao Ollama  |
| - gráficos PNG          |          +-----------+-------------+
| - daily_report.md       |                      |
| - driver_instructions.md|                      v
| - performance_comparison|          +-------------------------+
+-------------------------+          | Ollama + Llama 3.2      |
                                     | execução local          |
                                     +-----------+-------------+
                                                 |
                                                 v
                                     +-------------------------+
                                     | Artefatos da LLM        |
                                     | - llm_driver...md       |
                                     | - llm_operations...md   |
                                     | - llm_improvement...md  |
                                     | - respostas no terminal |
                                     +-------------------------+
```

---

## Fluxos disponíveis no `run.py`

### 1. Otimização

```bash
python run.py
```

ou:

```bash
python run.py optimize
```

Fluxo:

```text
CSV de entregas e veículos
        ↓
Modelos de domínio
        ↓
População inicial
        ↓
Avaliação por fitness
        ↓
Seleção, crossover, mutação e elitismo
        ↓
Melhor solução
        ↓
Mapa, gráficos, relatórios técnicos e routes.json
```

---

### 2. Otimização com LLM

```bash
python run.py optimize --llm --llm-model llama3.2
```

Fluxo:

```text
Algoritmo Genético
        ↓
routes.json
        ↓
Prompts
        ↓
Ollama
        ↓
Relatórios, instruções e sugestões gerados pela LLM
```

---

### 3. Relatórios da LLM a partir de um resultado existente

```bash
python run.py llm-report --llm-model llama3.2
```

Esse fluxo pressupõe que `outputs/routes.json` já foi gerado.

---

### 4. Perguntas em linguagem natural com LLM

```bash
python run.py ask "Qual rota tem maior risco operacional?" --llm-model llama3.2
```

Esse modo sempre usa a LLM local via Ollama. Não há perguntas por regras locais, pois o requisito do projeto pede uso de uma LLM pré-treinada.

---

### 5. Menu interativo

```bash
python run.py menu
```

O menu é um recurso de apresentação. Ele não é necessário para a execução automatizada, mas facilita demonstrar o sistema ao vivo.

```text
1 - Executar Algoritmo Genético e gerar artefatos
2 - Gerar relatórios com LLM local (Ollama)
3 - Perguntar sobre as rotas com LLM local (Ollama)
4 - Sair
```

---

## Papel de cada módulo

### `src/genetic_algorithm.py`

Implementa a lógica evolutiva: população inicial, seleção, crossover, mutação, reparo e elitismo.

### `src/fitness.py`

Calcula o custo de uma solução considerando distância, prioridade, capacidade, autonomia, atraso e penalidades por cromossomos inválidos.

### `src/vrp_solver.py`

Orquestra o uso do Algoritmo Genético para o problema de roteamento de veículos.

### `src/report_generator.py`

Gera relatórios determinísticos e salva o `routes.json`.

### `src/map_visualizer.py`

Gera o mapa interativo das rotas com Folium.

### `src/charts.py`

Gera gráficos de apoio com Matplotlib.

### `src/baseline.py`

Gera um comparativo de desempenho contra uma heurística simples de vizinho mais próximo.

### `src/prompts.py`

Centraliza os prompts usados pela LLM para relatórios, instruções, melhorias e perguntas.

### `src/llm_service.py`

Faz a comunicação HTTP com o Ollama em `http://localhost:11434/api/generate`.

### `src/qa_service.py`

Carrega o `routes.json` e delega perguntas em linguagem natural para a LLM local.

---

## Saídas geradas

```text
outputs/routes.json
outputs/routes_map.html
outputs/fitness_evolution.png
outputs/vehicle_distance.png
outputs/priority_distribution.png
outputs/daily_report.md
outputs/driver_instructions.md
outputs/performance_comparison.md
outputs/llm_driver_instructions.md
outputs/llm_operations_report.md
outputs/llm_improvement_suggestions.md
```
