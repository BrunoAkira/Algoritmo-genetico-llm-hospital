import argparse
from pathlib import Path

from src.llm_service import generate_ollama_outputs
from src.qa_service import load_payload


def parse_args() -> argparse.Namespace:
    """Lê os parâmetros para gerar relatórios com LLM a partir de um routes.json já existente."""
    parser = argparse.ArgumentParser(description="Gera relatórios com LLM local via Ollama.")
    parser.add_argument("--routes", default="outputs/routes.json", help="Arquivo JSON gerado pelo run.py.")
    parser.add_argument("--output-dir", default="outputs", help="Pasta onde os relatórios da LLM serão salvos.")
    parser.add_argument("--model", default="llama3.2", help="Modelo local do Ollama, por exemplo llama3.2 ou mistral.")
    parser.add_argument("--ollama-url", default="http://localhost:11434", help="URL local da API do Ollama.")
    return parser.parse_args()


def main() -> None:
    """Carrega as rotas otimizadas e gera relatórios usando uma LLM local."""
    args = parse_args()
    payload = load_payload(args.routes)
    generate_ollama_outputs(payload, Path(args.output_dir), model=args.model, base_url=args.ollama_url)
    print("Relatórios com LLM gerados em outputs/.")


if __name__ == "__main__":
    main()
