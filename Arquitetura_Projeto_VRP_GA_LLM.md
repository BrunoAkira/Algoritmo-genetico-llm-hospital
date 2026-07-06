# Arquitetura do Projeto - Sistema de Otimização de Rotas (VRP + Algoritmo Genético + LLM com Ollama)

## Objetivo

O sistema utiliza um Algoritmo Genético para resolver um problema de
roteamento de veículos (VRP), baseado no TSP, e utiliza uma LLM
executada localmente via **Ollama** para gerar relatórios, instruções e
responder perguntas em linguagem natural.

## Fluxo Geral

``` text
run.py
   │
   ├── Carrega dados (CSV)
   │
   ├── Executa o Algoritmo Genético
   │      ├── Seleção
   │      ├── Crossover
   │      ├── Mutação
   │      └── Fitness
   │
   ├── Melhor solução
   │
   ├── Gera:
   │      ├── outputs/routes.json
   │      ├── outputs/routes_map.html
   │      ├── outputs/fitness_evolution.png
   │      ├── outputs/report.md
   │      └── outputs/driver_instructions.md
   │
   └── (Opcional)
          ↓
     python llm_report.py
          ↓
      prompts.py
          ↓
      llm_service.py
          ↓
        Ollama
          ↓
      Modelo Llama 3.2
          ↓
   outputs/llm_report.md
   outputs/llm_driver_instructions.md

Perguntas em linguagem natural

python ask.py --llm "Pergunta"

        ↓

routes.json
        ↓
prompts.py
        ↓
llm_service.py
        ↓
Ollama
        ↓
Resposta da LLM
```

## Responsabilidade dos arquivos

### run.py

Coordena toda a execução do sistema, desde a leitura dos dados até a
geração dos artefatos.

### data_loader.py

Lê os arquivos CSV de entregas e veículos.

### genetic_algorithm.py

Implementa população inicial, seleção, crossover, mutação, elitismo e
evolução das gerações.

### fitness.py

Calcula o custo de cada solução considerando distância, prioridades,
capacidade, autonomia e penalidades.

### map_visualizer.py

Gera o mapa HTML utilizando Folium.

### chart_generator.py

Gera gráficos da evolução do fitness utilizando Matplotlib.

### report_generator.py

Gera os relatórios básicos do algoritmo (sem LLM).

### llm/prompts.py

Centraliza todos os prompts enviados para a LLM.

### llm/llm_service.py

Realiza a comunicação com o Ollama e abstrai as chamadas ao modelo Llama
3.2.

### llm_report.py

Lê o arquivo routes.json, envia os dados para a LLM e gera: -
llm_report.md - llm_driver_instructions.md

### ask.py

Permite fazer perguntas em linguagem natural sobre as rotas utilizando o
Ollama.

## Tecnologias

-   Python 3.11
-   Algoritmo Genético
-   Folium
-   Matplotlib
-   Ollama
-   Llama 3.2

Toda a parte de LLM é executada localmente, sem utilização de APIs
pagas.

## Atendimento aos requisitos

-   Algoritmo Genético para VRP
-   Fitness com múltiplas restrições
-   Prioridade de entregas
-   Capacidade dos veículos
-   Autonomia
-   Múltiplos veículos
-   Visualização em mapa
-   Relatórios automáticos
-   Instruções para motoristas com LLM
-   Sugestões de melhoria com LLM
-   Perguntas em linguagem natural utilizando uma LLM pré-treinada
    executada localmente (Ollama).
