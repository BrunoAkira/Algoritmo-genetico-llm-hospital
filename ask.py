import argparse
from src.qa_service import load_payload, answer_question, answer_question_with_llm


def parse_args() -> argparse.Namespace:
    """Lê a pergunta, o arquivo de rotas e a opção de usar LLM local pelo terminal."""
    parser = argparse.ArgumentParser(description="Pergunte sobre as rotas otimizadas.")
    parser.add_argument("question", help="Pergunta em linguagem natural sobre as rotas.")
    parser.add_argument("--routes", default="outputs/routes.json", help="Arquivo JSON gerado pelo run.py.")
    parser.add_argument("--llm", action="store_true", help="Usa LLM local via Ollama em vez das regras simples.")
    parser.add_argument("--model", default="llama3.2", help="Modelo local do Ollama, por exemplo llama3.2 ou mistral.")
    parser.add_argument("--ollama-url", default="http://localhost:11434", help="URL local da API do Ollama.")
    return parser.parse_args()


def main() -> None:
    """Carrega as rotas geradas e responde a pergunta do usuário."""
    args = parse_args()
    payload = load_payload(args.routes)

    if args.llm:
        # Modo exigido para atender a parte de LLM do trabalho: usa modelo pré-treinado local.
        print(answer_question_with_llm(args.question, payload, model=args.model, base_url=args.ollama_url))
    else:
        # Modo local sem LLM: útil para testes rápidos quando o Ollama não estiver rodando.
        print(answer_question(args.question, payload))


if __name__ == "__main__":
    main()
