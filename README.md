# Sistema de Otimização de Rotas Hospitalares com AG + LLM Local

Este projeto otimiza rotas de entrega de **medicamentos e insumos hospitalares** usando um **Algoritmo Genético**. Ele parte do problema do **Caixeiro Viajante (TSP)** e evolui para um cenário de **VRP — Vehicle Routing Problem**, com múltiplos veículos, capacidade, autonomia e prioridades de entrega.

A parte de LLM é feita com **Ollama**, rodando localmente. Assim, o projeto usa uma LLM pré-treinada sem API paga, sem chave da OpenAI e sem cartão de crédito.

O projeto não possui frontend. Ele roda pelo terminal e gera arquivos em `outputs/`.

---

## 1. Pré-requisitos

- Python 3.11 recomendado;
- Git Bash, PowerShell ou terminal equivalente;
- Ollama instalado apenas se você quiser testar a parte de LLM.

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

## 3. Rodar somente o Algoritmo Genético

Este comando executa a otimização, gera mapa, gráficos, JSON e relatórios locais sem LLM:

```bash
python run.py
```

Com parâmetros opcionais:

```bash
python run.py --generations 500 --population-size 150 --mutation-rate 0.30 --seed 42
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

## 4. Visualizar os resultados

Abrir o mapa no Windows:

```bash
start outputs/routes_map.html
```

Abrir relatórios Markdown no VS Code:

```bash
code outputs/daily_report.md
code outputs/driver_instructions.md
outputs/performance_comparison.md
```

No VS Code, use `Ctrl + Shift + V` para abrir o preview do Markdown.

Abrir os gráficos:

```bash
start outputs/fitness_evolution.png
start outputs/vehicle_distance.png
start outputs/priority_distribution.png
```

---

## 5. Configurar a LLM local com Ollama

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

## 6. Rodar o projeto com LLM

Depois de instalar o Ollama e baixar o modelo, rode:

```bash
python run.py --use-llm --llm-model llama3.2
```

Esse comando executa o Algoritmo Genético e também gera os arquivos da LLM:

```text
outputs/llm_driver_instructions.md
outputs/llm_operations_report.md
outputs/llm_improvement_suggestions.md
```

Também é possível gerar somente os relatórios da LLM depois de já ter executado `run.py`:

```bash
python llm_report.py --model llama3.2
```

---

## 7. Fazer perguntas sobre as rotas

Modo local, sem LLM:

```bash
python ask.py "Qual veículo percorreu a maior distância?"
python ask.py "Alguma rota ultrapassou a autonomia?"
python ask.py "Quais entregas críticas foram priorizadas?"
```

Modo com LLM local via Ollama:

```bash
python ask.py "Qual rota tem maior risco operacional e por quê?" --llm --model llama3.2
python ask.py "Sugira melhorias para reduzir atrasos nas entregas críticas" --llm --model llama3.2
```

---

## 8. Rodar os testes automatizados

```bash
pytest -q
```

Os testes validam funcionalidades principais, como:

- carregamento dos dados;
- representação genética;
- reparo de cromossomos inválidos;
- penalização de capacidade/autonomia;
- geração de prompts para a LLM;
- perguntas locais sem LLM;
- execução básica do solver;
- comparativo com heurística de vizinho mais próximo.

---

## 9. Estrutura do projeto

```text
.
├── run.py                         # Executa o fluxo principal
├── ask.py                         # Perguntas sobre rotas, com ou sem LLM
├── llm_report.py                  # Gera relatórios com LLM a partir do routes.json
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

## 10. Observação sobre a LLM

A LLM não calcula as rotas. O cálculo das rotas é feito pelo Algoritmo Genético.

A LLM interpreta o arquivo `outputs/routes.json` para:

- gerar instruções detalhadas para motoristas;
- criar relatório operacional;
- sugerir melhorias;
- responder perguntas em linguagem natural.

Essa separação deixa o projeto mais claro: o AG resolve o problema matemático e a LLM explica os resultados.
