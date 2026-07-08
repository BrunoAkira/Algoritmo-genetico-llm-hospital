# Sistema de Otimização de Rotas Hospitalares com AG e LLM Local

Este projeto otimiza rotas de entrega de **medicamentos e insumos hospitalares** usando **Algoritmo Genético**. O problema parte do **TSP** e é ampliado para **VRP**, pois considera múltiplos veículos, capacidade de carga, autonomia, prioridade de entrega e penalidades operacionais.

A parte de LLM usa **Ollama** com um modelo pré-treinado local, como `llama3.2`. Não há uso de OpenAI, API paga, chave externa ou cartão de crédito.

O projeto não possui frontend. Tudo roda localmente pelo terminal e os resultados são gerados na pasta `outputs/`.

---

## 1. Pré-requisitos no Windows

- Python 3.11;
- Git Bash ou PowerShell;
- Ollama instalado para usar a LLM local.

Verifique o Python:

```bash
py -3.11 --version
```

---

## 2. Instalação local com venv

No Git Bash:

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

---

## 3. Configurar o Ollama

Instale o Ollama pelo site oficial:

```text
https://ollama.com/download
```

Feche e abra o terminal depois da instalação. Teste:

```bash
ollama --version
```

Baixe o modelo local:

```bash
ollama pull llama3.2
```

Teste o modelo:

```bash
ollama run llama3.2
```

Para sair do chat do Ollama:

```text
/bye
```

Se o Git Bash não encontrar o comando `ollama`, adicione o caminho temporariamente:

```bash
export PATH="$PATH:/c/Users/bruno/AppData/Local/Programs/Ollama"
ollama --version
```

---

## 4. Rodar o Algoritmo Genético

```bash
python run.py
```

ou explicitamente:

```bash
python run.py optimize
```

Com parâmetros opcionais:

```bash
python run.py optimize --generations 500 --population-size 150 --mutation-rate 0.30 --seed 42
```

Esse comando gera os artefatos técnicos do AG:

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

## 5. Rodar o AG e a LLM no mesmo comando

Depois de instalar o Ollama e baixar o modelo:

```bash
python run.py optimize --llm --llm-model llama3.2
```

Esse comando executa a otimização e, em seguida, usa a LLM para gerar:

```text
outputs/llm_driver_instructions.md
outputs/llm_operations_report.md
outputs/llm_improvement_suggestions.md
```

---

## 6. Gerar relatórios da LLM depois da otimização

Use este comando quando `outputs/routes.json` já existir:

```bash
python run.py llm-report --llm-model llama3.2
```

Esse fluxo atende aos requisitos de:

- gerar instruções detalhadas para motoristas;
- criar relatório operacional;
- sugerir melhorias com base nas rotas otimizadas.

---

## 7. Fazer perguntas em linguagem natural com LLM

O projeto responde perguntas usando a LLM local via Ollama. Não há modo de perguntas por regras locais, pois o requisito do projeto pede uso de uma LLM pré-treinada.

Exemplos:

```bash
python run.py ask "Qual veículo percorreu a maior distância?" --llm-model llama3.2
python run.py ask "Qual rota apresenta maior risco operacional e por quê?" --llm-model llama3.2
python run.py ask "Sugira melhorias para reduzir atrasos nas entregas críticas" --llm-model llama3.2
```

Esse fluxo atende ao requisito de permitir perguntas em linguagem natural sobre rotas e entregas.

---

## 8. Menu interativo para apresentação

O menu não é obrigatório para o funcionamento do projeto. Ele existe apenas para facilitar a demonstração durante a apresentação.

```bash
python run.py menu
```

Opções do menu:

```text
1 - Executar Algoritmo Genético e gerar artefatos
2 - Gerar relatórios com LLM local (Ollama)
3 - Perguntar sobre as rotas com LLM local (Ollama)
4 - Sair
```

Para entrega técnica ou execução automatizada, prefira os comandos diretos (`optimize`, `llm-report` e `ask`).

---

## 9. Visualizar os resultados

Abrir o mapa:

```bash
start outputs/routes_map.html
```

Abrir gráficos:

```bash
start outputs/fitness_evolution.png
start outputs/vehicle_distance.png
start outputs/priority_distribution.png
```

Abrir relatórios no VS Code:

```bash
code outputs/daily_report.md
code outputs/driver_instructions.md
code outputs/performance_comparison.md
code outputs/llm_operations_report.md
code outputs/llm_driver_instructions.md
code outputs/llm_improvement_suggestions.md
```

No VS Code, use `Ctrl + Shift + V` para abrir o preview do Markdown.

---

## 10. Rodar testes automatizados

```bash
pytest -q
```

Os testes validam:

- carregamento de dados;
- representação genética;
- crossover, mutação e reparo;
- penalizações da função fitness;
- geração de prompts para a LLM;
- chamadas centralizadas pelo `run.py`;
- comparativo com heurística de vizinho mais próximo;
- delegação das perguntas para a LLM sem conectar ao Ollama durante o teste.

---

## 11. Estrutura do projeto

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
│   ├── report_generator.py        # Relatórios técnicos locais
│   ├── baseline.py                # Comparativo com heurística gulosa
│   ├── prompts.py                 # Prompts enviados à LLM
│   ├── llm_service.py             # Integração com Ollama
│   └── qa_service.py              # Perguntas em linguagem natural via LLM
└── tests/
    └── test_basic.py              # Testes automatizados
```

---

## 12. Papel da LLM

A LLM não calcula as rotas. O cálculo é feito pelo Algoritmo Genético.

A LLM interpreta `outputs/routes.json` para:

- gerar instruções detalhadas para motoristas;
- criar relatório operacional;
- sugerir melhorias;
- responder perguntas em linguagem natural.

A comunicação com o Ollama usa o endpoint local:

```text
http://localhost:11434/api/generate
```
