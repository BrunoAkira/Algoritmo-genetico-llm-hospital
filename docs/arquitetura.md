# Arquitetura do Sistema de Otimização de Rotas

## Visão geral

O sistema possui duas camadas principais:

1. **Camada de otimização**, responsável por calcular rotas usando Algoritmo Genético.
2. **Camada de interpretação**, responsável por usar uma LLM local via Ollama para gerar textos, relatórios e respostas em linguagem natural.

A LLM não substitui o algoritmo de otimização. Ela recebe o resultado estruturado em `outputs/routes.json` e interpreta esse resultado.

---

## Diagrama geral

```text
                 +----------------------+
                 |        run.py        |
                 +----------+-----------+
                            |
                            v
                +------------------------+
                | Leitura dos dados CSV  |
                | data_loader.py         |
                +----------+-------------+
                           |
                           v
                +------------------------+
                | Modelos de domínio     |
                | models.py              |
                +----------+-------------+
                           |
                           v
                +------------------------+
                | VRPSolver              |
                | vrp_solver.py          |
                +----------+-------------+
                           |
                           v
                +------------------------+
                | Algoritmo Genético     |
                | genetic_algorithm.py   |
                +----------+-------------+
                           |
       +-------------------+-------------------+
       |                   |                   |
       v                   v                   v
 +------------+      +-------------+      +------------+
 | Seleção    |      | Crossover   |      | Mutação    |
 +------------+      +-------------+      +------------+
       \                   |                   /
        \__________________|__________________/
                           |
                           v
                +------------------------+
                | Função fitness         |
                | fitness.py             |
                +----------+-------------+
                           |
                           v
                +------------------------+
                | Melhor solução         |
                +----------+-------------+
                           |
         +-----------------+-------------------+----------------+
         |                 |                   |                |
         v                 v                   v                v
 routes.json       routes_map.html    fitness_evolution.png   daily_report.md     performance_comparison.md
 report_generator  baseline.py  map_visualizer     charts.py               report_generator
         |
         v
 +------------------------------+
 | Integração opcional com LLM   |
 | llm_report.py / ask.py --llm  |
 +--------------+---------------+
                |
                v
 +------------------------------+
 | prompts.py                   |
 | Montagem dos prompts          |
 +--------------+---------------+
                |
                v
 +------------------------------+
 | llm_service.py               |
 | Chamada HTTP ao Ollama        |
 +--------------+---------------+
                |
                v
 +------------------------------+
 | Ollama + Llama 3.2 local      |
 +--------------+---------------+
                |
                v
 llm_driver_instructions.md / llm_operations_report.md / llm_improvement_suggestions.md
```

---

## Fluxo do `run.py`

```text
python run.py
   ↓
Lê data/deliveries.csv
   ↓
Lê data/vehicles.csv
   ↓
Cria população inicial
   ↓
Calcula fitness dos indivíduos
   ↓
Aplica seleção por torneio
   ↓
Aplica crossover OX adaptado
   ↓
Aplica mutações especializadas
   ↓
Repara indivíduos inválidos
   ↓
Repete por N gerações
   ↓
Seleciona melhor solução
   ↓
Gera JSON, mapa, gráficos e relatórios locais
```

---

## Fluxo da LLM com Ollama

```text
python llm_report.py
   ↓
Lê outputs/routes.json
   ↓
Monta prompts em prompts.py
   ↓
Envia prompt para llm_service.py
   ↓
llm_service.py chama http://localhost:11434/api/generate
   ↓
Ollama executa o modelo local, por exemplo llama3.2
   ↓
Resposta textual é salva em Markdown
```

Arquivos gerados pela LLM:

```text
outputs/llm_driver_instructions.md
outputs/llm_operations_report.md
outputs/llm_improvement_suggestions.md
```

---

## Fluxo de perguntas em linguagem natural

```text
python ask.py "Pergunta" --llm --model llama3.2
   ↓
ask.py lê outputs/routes.json
   ↓
qa_service.py chama OllamaLLMService
   ↓
prompts.py monta o prompt de pergunta e resposta
   ↓
llm_service.py envia o prompt ao Ollama
   ↓
A LLM responde com base nas rotas
```

Também existe modo sem LLM:

```text
python ask.py "Qual veículo percorreu a maior distância?"
```

Esse modo usa regras locais para perguntas simples e ajuda nos testes mesmo sem Ollama.

---

## Decisão arquitetural sobre LLM

O projeto utiliza **Ollama** para evitar dependência de APIs pagas. A integração usa chamada HTTP local para `http://localhost:11434/api/generate`.

Vantagens dessa decisão:

- não exige chave de API;
- não usa OpenAI ou serviços pagos;
- funciona localmente;
- atende ao requisito de usar uma LLM pré-treinada;
- facilita demonstrações acadêmicas.
