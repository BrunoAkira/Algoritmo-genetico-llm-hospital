# Arquitetura do Projeto - Sistema de Otimização de Rotas (VRP + Algoritmo Genético + LLM)

## Visão Geral

O projeto é dividido em duas grandes camadas:

1.  **Camada de Otimização (Algoritmo Genético)** -- responsável por
    encontrar as melhores rotas.
2.  **Camada de Inteligência (LLM)** -- responsável por interpretar os
    resultados e gerar relatórios em linguagem natural.

------------------------------------------------------------------------

# Fluxo Geral

``` text
run.py
 │
 ├── Carrega arquivos CSV
 │
 ├── Cria objetos de Entregas e Veículos
 │
 ├── Executa o Algoritmo Genético
 │
 ├── Calcula o Fitness das soluções
 │
 ├── Seleção → Crossover → Mutação
 │
 ├── Obtém a melhor solução
 │
 ├── Gera outputs/
 │      ├── routes.json
 │      ├── routes_map.html
 │      ├── fitness_evolution.png
 │      ├── report.md
 │      └── driver_instructions.md
 │
 └── (Opcional)
        ↓
      LLM
        ↓
      Relatórios inteligentes
```

------------------------------------------------------------------------

# Responsabilidade de cada arquivo

## run.py

Arquivo principal do sistema.

Responsabilidades:

-   carregar dados;
-   iniciar o algoritmo genético;
-   gerar os arquivos de saída;
-   coordenar todo o fluxo.

------------------------------------------------------------------------

## src/data_loader.py

Responsável pela leitura dos arquivos CSV.

Entrada:

-   deliveries.csv
-   vehicles.csv

Saída:

-   objetos utilizados pelo algoritmo.

------------------------------------------------------------------------

## src/models.py

Define os modelos do domínio.

Exemplos:

-   Delivery
-   Vehicle
-   Route

------------------------------------------------------------------------

## src/distance.py

Calcula a distância entre os pontos da rota.

É utilizado pelo Fitness.

------------------------------------------------------------------------

## src/fitness.py

Calcula o custo da solução.

Exemplo conceitual:

    fitness =
        distância_total
      + penalidade_capacidade
      + penalidade_autonomia
      + penalidade_prioridade
      + penalidade_atraso

Quanto menor o fitness, melhor a solução.

------------------------------------------------------------------------

## src/genetic_algorithm.py

Núcleo do projeto.

Executa:

-   população inicial;
-   seleção;
-   crossover;
-   mutação;
-   elitismo;
-   evolução das gerações.

------------------------------------------------------------------------

## src/map_visualizer.py

Responsável por gerar:

    outputs/routes_map.html

Biblioteca utilizada:

-   Folium

------------------------------------------------------------------------

## src/chart_generator.py

Responsável por gerar:

    outputs/fitness_evolution.png

Biblioteca utilizada:

-   Matplotlib

------------------------------------------------------------------------

## src/report_generator.py

Gera os relatórios básicos do sistema.

Exemplo:

-   report.md
-   driver_instructions.md

------------------------------------------------------------------------

## outputs/routes.json

Arquivo mais importante do sistema.

Contém:

-   rotas;
-   veículos;
-   distância;
-   carga;
-   prioridades;
-   métricas.

É utilizado posteriormente pela LLM.

------------------------------------------------------------------------

# Funcionamento do Algoritmo Genético

``` text
Criar população inicial
        ↓
Calcular Fitness
        ↓
Selecionar pais
        ↓
Aplicar Crossover
        ↓
Aplicar Mutação
        ↓
Gerar nova população
        ↓
Repetir por N gerações
        ↓
Melhor solução encontrada
```

------------------------------------------------------------------------

# Fluxo da LLM

A LLM não calcula a rota.

Ela interpreta o resultado produzido pelo Algoritmo Genético.

Fluxo:

``` text
outputs/routes.json
        ↓
llm_service.py
        ↓
Monta Prompt
        ↓
OpenAI API
        ↓
Resposta
        ↓
Relatórios
```

------------------------------------------------------------------------

# Biblioteca utilizada na LLM

-   openai
-   python-dotenv

A biblioteca **openai** realiza a comunicação com o modelo de linguagem.

A biblioteca **python-dotenv** lê a chave da API armazenada no arquivo
`.env`.

------------------------------------------------------------------------

# Responsabilidades da LLM

A LLM pode:

-   gerar instruções para motoristas;
-   produzir relatórios operacionais;
-   responder perguntas em linguagem natural;
-   sugerir melhorias logísticas;
-   explicar as decisões do algoritmo.

Ela **não participa da otimização das rotas**.

------------------------------------------------------------------------

# Resumo da Arquitetura

``` text
                 +----------------------+
                 |      run.py          |
                 +----------+-----------+
                            |
        +-------------------+------------------+
        |                                      |
        v                                      v
 Carrega Dados                        Algoritmo Genético
(data_loader.py)                   (genetic_algorithm.py)
                                               |
                                               v
                                          fitness.py
                                               |
                                               v
                                    Melhor solução encontrada
                                               |
                  +----------------------------+----------------------------+
                  |                             |                            |
                  v                             v                            v
          routes.json                 routes_map.html           fitness_evolution.png
                  |
                  v
            LLM (OpenAI)
                  |
                  +-----------------------------+
                  |                             |
                  v                             v
      Relatório Operacional         Instruções para Motoristas
```
