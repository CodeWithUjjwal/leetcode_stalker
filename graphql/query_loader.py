from pathlib import Path

_QUERIES_DIR = Path(__file__).resolve().parent / "queries"

def load_graphql_query(file_name: str) -> str:
    return (_QUERIES_DIR / f"{file_name}.graphql").read_text(encoding = "utf-8")