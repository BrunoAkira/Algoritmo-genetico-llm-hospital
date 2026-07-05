# Otimizador de Rotas Médicas com Algoritmo Genético

Projeto local em Python para otimizar rotas de entrega de medicamentos e insumos usando Algoritmo Genético, evoluindo a ideia de TSP para VRP — Vehicle Routing Problem.

O sistema não possui frontend. Ele roda via terminal e gera arquivos em `outputs/`:

- `routes_map.html`: mapa interativo das rotas;
- `daily_report.md`: relatório operacional em Markdown;
- `routes.json`: rotas otimizadas em formato estruturado;
- `fitness_evolution.png`: gráfico de evolução do algoritmo;
- `vehicle_distance.png`: gráfico de distância por veículo;
- `priority_distribution.png`: gráfico de entregas por prioridade.

## Funcionalidades

- Representação genética para múltiplos veículos;
- Seleção por torneio;
- Crossover especializado para roteamento;
- Mutações por troca, inversão e movimentação entre veículos;
- Fitness com penalidades por:
  - distância total;
  - atraso em entregas;
  - prioridade médica;
  - excesso de capacidade;
  - excesso de autonomia;
  - uso desnecessário de veículos;
- Geração de mapa com Folium;
- Geração de gráficos com Matplotlib;
- Geração de relatório diário;
- Serviço de LLM opcional para criar instruções e responder perguntas.

## Instalação

Crie e ative um ambiente virtual:

```bash
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
```

Linux/Mac:

```bash
source .venv/bin/activate
```

Instale as dependências:

```bash
pip install -r requirements.txt
```

## Como rodar

```bash
python run.py
```

Com parâmetros:

```bash
python run.py --generations 500 --population-size 120 --seed 42
```

Após executar, veja os resultados na pasta `outputs/`.

## Perguntas em linguagem natural

Depois de gerar as rotas, você pode perguntar sobre o resultado:

```bash
python ask.py "Qual veículo percorreu a maior distância?"
python ask.py "Alguma rota ultrapassou a autonomia?"
python ask.py "Quais entregas críticas foram priorizadas?"
```

Por padrão, o projeto usa uma camada local simples baseada em regras. Caso queira usar uma LLM real, configure uma chave de API e adapte `src/llm_service.py`.

## Dados

Os dados de exemplo ficam em:

- `data/deliveries.csv`
- `data/vehicles.csv`

Você pode editar esses arquivos para simular outras entregas e frotas.

## Estrutura

```text
medical_vrp_ga/
  run.py
  ask.py
  requirements.txt
  README.md
  data/
    deliveries.csv
    vehicles.csv
  src/
    models.py
    data_loader.py
    distance.py
    fitness.py
    genetic_algorithm.py
    vrp_solver.py
    map_visualizer.py
    charts.py
    report_generator.py
    llm_service.py
    qa_service.py
  outputs/
  tests/
```

## Publicar no GitHub

Depois de revisar:

```bash
git init
git add .
git commit -m "Versao inicial do otimizador VRP medico"
git branch -M main
git remote add origin https://github.com/SEU_USUARIO/NOME_DO_REPO.git
git push -u origin main
```
