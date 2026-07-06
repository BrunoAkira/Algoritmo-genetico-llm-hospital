import json


SYSTEM_PROMPT = """
Você é uma LLM pré-treinada atuando como especialista em logística hospitalar.
Sua função é interpretar rotas otimizadas por Algoritmo Genético para entregas
medicamentosas e de insumos. Responda sempre em português, com linguagem clara,
objetiva e operacional. Não invente dados: use apenas as informações do JSON.
""".strip()


def payload_to_json(payload: dict) -> str:
    """Converte o resultado das rotas em JSON formatado para ser usado nos prompts."""
    return json.dumps(payload, ensure_ascii=False, indent=2)


def build_driver_instructions_prompt(payload: dict) -> str:
    """Monta o prompt que pede instruções detalhadas para motoristas e equipes de entrega."""
    return f"""
{SYSTEM_PROMPT}

Tarefa:
Gere instruções detalhadas para os motoristas e equipes de entrega com base nas rotas abaixo.

As instruções devem conter:
1. Sequência recomendada de paradas por veículo;
2. Entregas críticas e cuidados especiais;
3. Alertas de capacidade, autonomia e atrasos;
4. Orientações operacionais para conferência, comprovante e comunicação com a central;
5. Um resumo final por veículo.

Dados das rotas otimizadas:
{payload_to_json(payload)}
""".strip()


def build_operations_report_prompt(payload: dict) -> str:
    """Monta o prompt que pede um relatório diário ou semanal sobre eficiência das rotas."""
    return f"""
{SYSTEM_PROMPT}

Tarefa:
Crie um relatório operacional em Markdown sobre a eficiência das rotas otimizadas.

O relatório deve conter:
1. Resumo executivo;
2. Distância total e uso dos veículos;
3. Situação das entregas críticas;
4. Avaliação de capacidade e autonomia;
5. Economia e eficiência operacional percebida;
6. Riscos encontrados;
7. Sugestões práticas de melhoria;
8. Conclusão.

Dados das rotas otimizadas:
{payload_to_json(payload)}
""".strip()


def build_improvement_prompt(payload: dict) -> str:
    """Monta o prompt que pede sugestões de melhoria com base nos padrões das rotas."""
    return f"""
{SYSTEM_PROMPT}

Tarefa:
Analise os dados das rotas e sugira melhorias no processo logístico hospitalar.

Considere:
- Priorização de medicamentos críticos;
- Uso da frota;
- Capacidade dos veículos;
- Autonomia máxima;
- Atrasos projetados;
- Redistribuição de entregas;
- Possíveis ajustes nos dados de entrada.

Responda em tópicos objetivos e aplicáveis.

Dados das rotas otimizadas:
{payload_to_json(payload)}
""".strip()


def build_question_prompt(payload: dict, question: str) -> str:
    """Monta o prompt de perguntas e respostas em linguagem natural sobre as rotas."""
    return f"""
{SYSTEM_PROMPT}

Tarefa:
Responda à pergunta do usuário usando apenas o JSON das rotas.
Se a informação não estiver disponível nos dados, diga claramente que ela não está disponível.

Pergunta do usuário:
{question}

Dados das rotas otimizadas:
{payload_to_json(payload)}
""".strip()
