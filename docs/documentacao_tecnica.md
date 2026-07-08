# Documentação Técnica

## Dados de entrada

O sistema usa dois arquivos principais.

### data/deliveries.csv

Representa as entregas de medicamentos e insumos.

Campos esperados:

- `id`: identificador da entrega;
- `name`: nome do destino;
- `lat` e `lon`: coordenadas geográficas;
- `demand_kg`: peso/carga da entrega;
- `priority`: prioridade da entrega, sendo 1 regular, 2 alta e 3 crítica;
- `service_time_min`: tempo de atendimento no local;
- `deadline_min`: prazo máximo desejado em minutos.

### data/vehicles.csv

Representa os veículos disponíveis.

Campos esperados:

- `id`: identificador do veículo;
- `name`: nome do veículo;
- `capacity_kg`: capacidade máxima de carga;
- `max_distance_km`: autonomia máxima;
- `start_lat` e `start_lon`: posição inicial/base.

---

## Representação genética

Cada indivíduo é uma lista de rotas, onde cada rota pertence a um veículo.

Exemplo:

```python
[
    [3, 5, 1],
    [2, 8],
    [4, 6, 7]
]
```

Nesse exemplo:

- o primeiro veículo atende as entregas 3, 5 e 1;
- o segundo veículo atende as entregas 2 e 8;
- o terceiro veículo atende as entregas 4, 6 e 7.

Essa representação permite sair do TSP simples e trabalhar com VRP, pois há múltiplos veículos.

---

## Operadores genéticos

### Seleção

A seleção é feita por torneio. Alguns indivíduos são sorteados e o de menor custo é escolhido como pai.

### Crossover

O crossover usa uma adaptação do OX (Order Crossover). Primeiro, as rotas são transformadas em uma sequência única de entregas. Depois, uma parte da sequência vem de um pai e o restante é preenchido com a ordem do outro pai.

Após isso, a sequência é novamente dividida entre os veículos.

### Mutação

O projeto usa três tipos de mutação:

- troca entre entregas;
- inversão de trecho dentro de uma rota;
- movimentação de uma entrega de um veículo para outro.

Essas mutações aumentam a diversidade e ajudam a evitar convergência prematura.

### Reparo

Após crossover e mutação, o reparo garante que:

- nenhuma entrega seja duplicada;
- nenhuma entrega seja perdida;
- todas as entregas apareçam exatamente uma vez.

---

## Função fitness

A função fitness calcula o custo de cada solução. Quanto menor o custo, melhor a solução.

Componentes principais:

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

A prioridade influencia o custo porque atrasos em entregas críticas recebem peso maior.

---

## Relatórios e visualizações

O sistema gera:

- `routes.json`: resultado estruturado;
- `routes_map.html`: mapa interativo;
- `fitness_evolution.png`: evolução do fitness;
- `vehicle_distance.png`: distância por veículo;
- `priority_distribution.png`: distribuição das prioridades;
- `daily_report.md`: relatório operacional por regras;
- `driver_instructions.md`: instruções locais para motoristas;
- `performance_comparison.md`: comparação entre o Algoritmo Genético e uma heurística gulosa de vizinho mais próximo.

---

## Integração com LLM local

A LLM usa Ollama e modelo Llama 3.2 por padrão.

Arquivos principais:

- `src/prompts.py`: contém os prompts;
- `src/llm_service.py`: comunica com o Ollama;
- `llm_report.py`: gera relatórios com LLM;
- `ask.py`: permite perguntas em linguagem natural.

A chamada ao Ollama é feita para:

```text
http://localhost:11434/api/generate
```

Não há uso de OpenAI, chave de API ou serviço pago.

---

## Testes automatizados

Os testes ficam em `tests/` e podem ser executados com:

```bash
pytest -q
```

Eles validam partes essenciais do projeto para aumentar a confiabilidade antes da apresentação.


---

## Comparativo de desempenho

O arquivo `src/baseline.py` implementa uma heurística simples de vizinho mais próximo. Essa heurística serve como referência para comparar o desempenho do Algoritmo Genético.

O resultado é salvo em:

```text
outputs/performance_comparison.md
```

Esse comparativo ajuda a demonstrar que o AG não apenas gera uma rota, mas também pode ser analisado contra uma abordagem alternativa mais simples.
