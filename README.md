# Sistema de Otimização de Rotas Hospitalares com Algoritmo Genético e LLM Local

Este projeto otimiza rotas de entrega de **medicamentos e insumos hospitalares** usando um **Algoritmo Genético**. Ele parte do problema do **Caixeiro Viajante (TSP)** e evolui para um cenário de **VRP — Vehicle Routing Problem**, com múltiplos veículos, capacidade de carga, autonomia e prioridades de entrega.

A integração com LLM é feita com **Ollama**, rodando localmente. Dessa forma, o projeto usa uma LLM pré-treinada sem API paga, sem chave da OpenAI e sem cartão de crédito.

O projeto não possui frontend. Ele roda pelo terminal e gera arquivos em `outputs/`.

---

## 1. Pré-requisitos

- Python 3.11 recomendado;
- Git Bash, PowerShell ou terminal equivalente;
- Ollama instalado para testar a parte de LLM.

Verifique o Python:

```bash
py -3.11 --version
```

---

## 2. Instalação local

No Windows com Git Bash:

```bash
cd ~/Downloads/Algoritmo-genetico-llm-hospital
py -3.11 -m venv .venv
source .venv/Scripts/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

No PowerShell:

```powershell
cd $HOME\Downloads\Algoritmo-genetico-llm-hospital
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

No Linux/Mac:

```bash
cd ~/Downloads/Algoritmo-genetico-llm-hospital
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

---

## 3. Como rodar o projeto

A partir desta versão, o projeto é executado por um único arquivo principal: **`run.py`**.

### Opção A — rodar a otimização diretamente

```bash
python run.py
```

Esse comando executa o Algoritmo Genético e gera mapa, gráficos, JSON e relatórios locais sem LLM.

Equivalente explícito:

```bash
python run.py optimize
```

Com parâmetros opcionais:

```bash
python run.py optimize --generations 500 --population-size 150 --mutation-rate 0.30 --seed 42
```

Arquivos gerados:

```text
outputs/routes.json
outputs/routes_map.html
outputs/fitness_evolution.png
outputs/vehicle_distance.png
outputs/priority_distribution.png
outputs/daily_report.md
outputs/driver_instructions.md
outputs/performance_comparison.md
```

---

### Opção B — rodar otimização e LLM no mesmo comando

Depois de instalar o Ollama e baixar o modelo, rode:

```bash
python run.py optimize --llm --llm-model llama3.2
```

Esse comando executa o Algoritmo Genético e também gera arquivos produzidos pela LLM:

```text
outputs/llm_driver_instructions.md
outputs/llm_operations_report.md
outputs/llm_improvement_suggestions.md
```

---

### Opção C — gerar apenas os relatórios da LLM depois da otimização

Use esta opção quando `outputs/routes.json` já existe:

```bash
python run.py llm-report --llm-model llama3.2
```

Esse comando usa o resultado salvo pelo Algoritmo Genético e envia os dados para a LLM local via Ollama.

---

### Opção D — perguntar sobre as rotas

Perguntas por regras locais, sem LLM:

```bash
python run.py ask "Qual veículo percorreu a maior distância?"
python run.py ask "Alguma rota ultrapassou a autonomia?"
python run.py ask "Quais entregas críticas foram priorizadas?"
```

Perguntas usando LLM local via Ollama:

```bash
python run.py ask "Qual rota tem maior risco operacional e por quê?" --llm --llm-model llama3.2
python run.py ask "Sugira melhorias para reduzir atrasos nas entregas críticas" --llm --llm-model llama3.2
```

Essa funcionalidade atende ao requisito de permitir perguntas em linguagem natural sobre rotas e entregas.

---

### Opção E — menu interativo para apresentação

```bash
python run.py menu
```

O menu permite:

```text
1 - Executar Algoritmo Genético e gerar artefatos
2 - Gerar relatórios com LLM local (Ollama)
3 - Perguntar sobre as rotas sem LLM
4 - Perguntar sobre as rotas com LLM local (Ollama)
5 - Sair
```

Essa é a melhor opção para demonstrar o sistema em uma apresentação.

---

## 4. Configurar a LLM local com Ollama

Instale o Ollama pelo site oficial:

```text
https://ollama.com/download
```

Feche e abra o terminal depois da instalação. Em seguida, teste:

```bash
ollama --version
```

Baixe um modelo pré-treinado:

```bash
ollama pull llama3.2
```

Teste o modelo:

```bash
ollama run llama3.2
```

Digite uma mensagem simples. Para sair:

```text
/bye
```

Se o Git Bash não encontrar o comando `ollama`, adicione o caminho ao PATH temporariamente:

```bash
export PATH="$PATH:/c/Users/bruno/AppData/Local/Programs/Ollama"
ollama --version
```

---

## 5. Visualizar os resultados

Abrir o mapa no Windows:

```bash
start outputs/routes_map.html
```

Abrir relatórios Markdown no VS Code:

```bash
code outputs/daily_report.md
code outputs/driver_instructions.md
code outputs/performance_comparison.md
code outputs/llm_operations_report.md
```

No VS Code, use `Ctrl + Shift + V` para abrir o preview do Markdown.

Abrir os gráficos:

```bash
start outputs/fitness_evolution.png
start outputs/vehicle_distance.png
start outputs/priority_distribution.png
```

---

## 6. Rodar os testes automatizados

```bash
pytest -q
```

Os testes validam funcionalidades principais, como:

- carregamento dos dados;
- representação genética;
- reparo de cromossomos inválidos;
- penalização de rotas inválidas;
- geração de prompts para LLM;
- perguntas locais sem LLM;
- funções do `run.py`;
- execução básica do solver;
- comparativo com heurística de vizinho mais próximo.

---

## 7. Estrutura do projeto

```text
.
├── run.py                         # Arquivo principal: otimização, LLM, perguntas e menu
├── requirements.txt               # Dependências Python
├── data/
│   ├── deliveries.csv             # Entregas, prioridades, prazos e cargas
│   └── vehicles.csv               # Veículos, capacidade e autonomia
├── docs/
│   ├── arquitetura.md             # Fluxo e arquitetura do sistema
│   └── documentacao_tecnica.md    # Explicação técnica dos módulos
├── src/
│   ├── models.py                  # Modelos de domínio
│   ├── data_loader.py             # Leitura dos CSVs
│   ├── distance.py                # Distância geográfica e tempo estimado
│   ├── fitness.py                 # Função fitness e penalidades
│   ├── genetic_algorithm.py       # Seleção, crossover, mutação e elitismo
│   ├── vrp_solver.py              # Orquestra o AG
│   ├── map_visualizer.py          # Mapa HTML com Folium
│   ├── charts.py                  # Gráficos com Matplotlib
│   ├── report_generator.py        # Relatórios locais
│   ├── baseline.py                # Comparativo com heurística gulosa
│   ├── prompts.py                 # Prompts enviados à LLM
│   ├── llm_service.py             # Integração com Ollama
│   └── qa_service.py              # Perguntas locais ou via LLM
└── tests/
    └── test_basic.py              # Testes automatizados
```

---

## 8. Papel da LLM no projeto

A LLM não calcula as rotas. O cálculo é feito pelo Algoritmo Genético.

A LLM interpreta `outputs/routes.json` para:

- gerar instruções detalhadas para motoristas;
- criar relatório operacional;
- sugerir melhorias no processo;
- responder perguntas em linguagem natural sobre as entregas.

A integração é feita localmente via Ollama, usando o endpoint:

```text
http://localhost:11434/api/generate
```

Não há uso de OpenAI, chave de API ou serviço pago.
