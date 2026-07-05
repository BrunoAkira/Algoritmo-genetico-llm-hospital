import argparse
from src.qa_service import load_payload, answer_question


def parse_args() -> argparse.Namespace:
    """Lê a pergunta e o caminho do arquivo de rotas pelo terminal."""
    parser = argparse.ArgumentParser(description="Pergunte sobre as rotas otimizadas.")
    parser.add_argument("question", help="Pergunta em linguagem natural sobre as rotas.")
    parser.add_argument("--routes", default="outputs/routes.json", help="Arquivo JSON gerado pelo run.py.")
    return parser.parse_args()


def main() -> None:
    """Carrega as rotas geradas e responde a pergunta do usuário."""
    args = parse_args()
    payload = load_payload(args.routes)
    print(answer_question(args.question, payload))


if __name__ == "__main__":
    main()
