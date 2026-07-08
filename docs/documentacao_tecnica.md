# Documentação Técnica

## Objetivo técnico

O projeto implementa um sistema local para otimização de rotas hospitalares. O problema parte do TSP, mas é ampliado para VRP, pois existem múltiplos veículos, capacidade de carga, autonomia e prioridades distintas entre entregas.

---

## Representação genética

Cada indivíduo representa uma solução completa de roteamento.

```python
[
    [1, 4, 7],      # rota do veículo 1
    [2, 5],         # rota do veículo 2
    [3, 6, 8, 9],   # rota do veículo 3
]
```

Cada número representa uma entrega. Cada lista interna representa uma rota de veículo.

---

## Operadores genéticos

### Seleção

A seleção é feita por torneio. Alguns indivíduos são sorteados e o de menor custo é escolhido como pai.

### Crossover

O crossover usa uma adaptação do OX. As rotas são transformadas em uma sequência única de entregas, uma parte da sequência vem de um pai e o restante é preenchido com a ordem do outro pai.

### Mutação

O projeto usa mutações para manter diversidade:

- troca entre entregas;
- inversão de trecho dentro de uma rota;
- movimentação de uma entrega de um veículo para outro.

### Reparo

Após crossover e mutação, o reparo garante que nenhuma entrega seja duplicada ou perdida.

---

## Função fitness

A função fitness calcula o custo de cada solução. Quanto menor o custo, melhor a solução.

```text
fitness =
    distância_total
  + penalidade_por_excesso_de_capacidade
  + penalidade_por_excesso_de_autonomia
  + penalidade_por_atrasos
  + penalidade_por_atrasos_ponderados_pela_prioridade
  + penalidade_por_uso_de_veículos
  + penalidade_por_entregas_ausentes_ou_duplicadas
```

Entregas críticas possuem peso maior, principalmente quando há atraso projetado.

---

## Arquivo principal

A execução foi centralizada em `run.py`.

Principais modos:

```bash
python run.py
python run.py optimize
python run.py optimize --llm --llm-model llama3.2
python run.py llm-report --llm-model llama3.2
python run.py ask "Pergunta sobre as rotas" --llm-model llama3.2
python run.py menu
```

Com isso, o projeto fica mais simples de apresentar e não depende de scripts separados para demonstrar a LLM.

---

## Relatórios e visualizações

O sistema gera:

- `routes.json`: resultado estruturado;
- `routes_map.html`: mapa interativo;
- `fitness_evolution.png`: evolução do fitness;
- `vehicle_distance.png`: distância por veículo;
- `priority_distribution.png`: distribuição das prioridades;
- `daily_report.md`: relatório técnico local;
- `driver_instructions.md`: instruções determinísticas para motoristas;
- `performance_comparison.md`: comparação entre Algoritmo Genético e heurística gulosa.

---

## Integração com LLM local

A integração com LLM usa Ollama e modelo Llama 3.2 por padrão.

Arquivos principais:

- `src/prompts.py`: contém os prompts;
- `src/llm_service.py`: comunica com o Ollama;
- `src/qa_service.py`: encaminha perguntas para a LLM;
- `run.py`: centraliza os comandos de relatório e perguntas.

A chamada ao Ollama é feita para:

```text
http://localhost:11434/api/generate
```

Não há uso de OpenAI, chave de API ou serviço pago.

---

## Prompts

Os prompts foram separados em funções para facilitar manutenção:

- instruções para motoristas;
- relatório operacional;
- sugestões de melhoria;
- perguntas sobre rotas.

A LLM recebe o `routes.json` como contexto e deve responder somente com base nos dados fornecidos.

---

## Comparativo de desempenho

O arquivo `src/baseline.py` implementa uma heurística simples de vizinho mais próximo. Essa heurística serve como referência para comparar o desempenho do Algoritmo Genético.

O resultado é salvo em:

```text
outputs/performance_comparison.md
```

---

## Testes automatizados

Os testes ficam em `tests/` e podem ser executados com:

```bash
pytest -q
```

Eles validam carregamento dos dados, operadores genéticos, fitness, prompts, funções do `run.py`, delegação para a LLM e comparativo de desempenho.
