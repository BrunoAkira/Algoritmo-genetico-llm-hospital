# Otimizador de Rotas Médicas com Algoritmo Genético + LLM Local

Projeto local em Python para otimizar rotas de entrega de medicamentos e insumos usando **Algoritmo Genético**. O projeto evolui o problema do **TSP** para um cenário mais realista de **VRP — Vehicle Routing Problem**, com múltiplos veículos, capacidade, autonomia e prioridades médicas.

O sistema **não possui frontend**. Ele roda pelo terminal e gera arquivos na pasta `outputs/`.

---

## Requisitos atendidos

- Representação genética de rotas para múltiplos veículos;
- Seleção por torneio;
- Crossover especializado para roteamento;
- Mutações por troca, inversão e movimentação entre veículos;
- Fitness com penalidades por:
  - distância total;
  - prioridade médica;
  - atraso projetado;
  - excesso de capacidade;
  - excesso de autonomia;
  - uso dos veículos;
- Visualização das rotas em mapa HTML com Folium;
- Gráficos com Matplotlib;
- Relatórios em Markdown;
- Integração com **LLM pré-treinada local via Ollama**, sem API paga;
- Perguntas em linguagem natural sobre as rotas.

---

## Arquivos gerados

Após executar o projeto, os principais arquivos ficam em `outputs/`:

```text
outputs/
  routes.json                       # Resultado estruturado das rotas
  routes_map.html                   # Mapa interativo das rotas
  daily_report.md                   # Relatório operacional por regras locais
  driver_instructions.md            # Instruções por regras locais
  fitness_evolution.png             # Evolução do fitness
  vehicle_distance.png              # Distância por veículo
  priority_distribution.png         # Distribuição de prioridades
  llm_driver_instructions.md        # Instruções geradas pela LLM local
  llm_operations_report.md          # Relatório gerado pela LLM local
  llm_improvement_suggestions.md    # Sugestões geradas pela LLM local
```

Os arquivos com prefixo `llm_` só são gerados quando o Ollama está habilitado.

---

## Instalação Python

Recomendado: Python 3.11.

```bash
py -3.11 -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

No Linux/Mac:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

---

## Como rodar sem LLM

Este modo executa o Algoritmo Genético, gera mapa, gráficos e relatórios básicos.

```bash
py -3.11 run.py
```

Com parâmetros:

```bash
py -3.11 run.py --generations 500 --population-size 150 --seed 42
```

---

## Como usar LLM gratuita com Ollama

A integração com LLM foi feita com **Ollama**, que permite rodar modelos pré-treinados localmente, sem OpenAI, sem cartão e sem API paga.

### 1. Instale o Ollama

Baixe em: https://ollama.com

### 2. Baixe um modelo local

Sugestão leve:

```bash
ollama pull llama3.2
```

ou:

```bash
ollama run llama3.2
```

### 3. Execute o projeto com LLM

```bash
py -3.11 run.py --use-llm --llm-model llama3.2
```

Esse comando gera também:

```text
outputs/llm_driver_instructions.md
outputs/llm_operations_report.md
outputs/llm_improvement_suggestions.md
```

### 4. Gerar relatórios LLM depois do run.py

Se você já rodou o algoritmo e já tem `outputs/routes.json`, pode gerar só os relatórios da LLM:

```bash
py -3.11 llm_report.py --model llama3.2
```

---

## Perguntas em linguagem natural

### Modo simples sem LLM

```bash
py -3.11 ask.py "Qual veículo percorreu a maior distância?"
py -3.11 ask.py "Alguma rota ultrapassou a autonomia?"
py -3.11 ask.py "Quais entregas críticas foram priorizadas?"
```

### Modo com LLM local

```bash
py -3.11 ask.py "Qual rota tem maior risco operacional e por quê?" --llm --model llama3.2
```

No modo `--llm`, a pergunta é enviada para o modelo local do Ollama junto com o conteúdo de `outputs/routes.json`.

---

## Fluxo do sistema

```text
run.py
  ↓
Carrega data/deliveries.csv e data/vehicles.csv
  ↓
Cria a população inicial do Algoritmo Genético
  ↓
Avalia cada indivíduo com a função fitness
  ↓
Aplica seleção, crossover e mutação
  ↓
Encontra a melhor solução de rotas
  ↓
Gera mapa, gráficos, JSON e relatórios locais
  ↓
Opcional: envia routes.json para LLM local via Ollama
  ↓
Gera instruções, relatório operacional e sugestões de melhoria
```

---

## Estrutura do projeto

```text
.
  run.py                    # Executa o fluxo completo
  ask.py                    # Responde perguntas sobre as rotas
  llm_report.py             # Gera relatórios LLM a partir de routes.json
  requirements.txt
  data/
    deliveries.csv          # Entregas, prioridades, prazos e cargas
    vehicles.csv            # Veículos, capacidade e autonomia
  src/
    models.py               # Classes de domínio
    data_loader.py          # Leitura dos CSVs
    distance.py             # Cálculo de distância e tempo
    fitness.py              # Função fitness e penalidades
    genetic_algorithm.py    # Seleção, crossover, mutação e evolução
    vrp_solver.py           # Orquestra o Algoritmo Genético
    map_visualizer.py       # Mapa HTML com Folium
    charts.py               # Gráficos com Matplotlib
    report_generator.py     # Relatórios locais em Markdown
    prompts.py              # Prompts usados pela LLM
    llm_service.py          # Integração com Ollama e fallback local
    qa_service.py           # Perguntas por regras ou LLM
  outputs/
  tests/
```

---

## Observação importante sobre a LLM

A LLM **não calcula as rotas**. Quem resolve o problema é o Algoritmo Genético.

A LLM é usada para:

- gerar instruções detalhadas para motoristas;
- criar relatórios operacionais;
- sugerir melhorias;
- responder perguntas em linguagem natural.

Essa separação deixa a arquitetura mais correta: o AG otimiza, a LLM explica e interpreta.
