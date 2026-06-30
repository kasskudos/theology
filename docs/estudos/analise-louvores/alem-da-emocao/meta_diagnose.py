import argparse
import json
import os
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parent


def load_env_file(path: Path) -> None:
    if not path.exists():
        return

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


def graph_get(path: str, params: dict[str, str]) -> tuple[bool, dict]:
    graph_version = os.getenv("META_GRAPH_VERSION", "v23.0")
    token = params.get("access_token", "")
    configured_host = os.getenv("META_GRAPH_HOST", "").strip().lower()
    if configured_host in ("instagram", "graph.instagram.com"):
        domain = "graph.instagram.com"
    elif configured_host in ("facebook", "graph.facebook.com"):
        domain = "graph.facebook.com"
    elif token.startswith("IG"):
        domain = "graph.instagram.com"
    else:
        domain = "graph.facebook.com"

    base = f"https://{domain}/{graph_version}/{path.lstrip('/')}"
    url = base + "?" + urllib.parse.urlencode(params)
    request = urllib.request.Request(url, method="GET")

    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            return True, json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        body = error.read().decode("utf-8", errors="replace")
        try:
            return False, json.loads(body)
        except json.JSONDecodeError:
            return False, {"error": {"message": body, "code": error.code}}


def summarize_error(data: dict) -> str:
    error = data.get("error", {})
    message = error.get("message", "(sem mensagem)")
    code = error.get("code", "(sem codigo)")
    error_type = error.get("type", "(sem tipo)")
    return f"{error_type} code={code}: {message}"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Diagnostica token/permissoes da Meta sem publicar nada."
    )
    parser.add_argument("--env-file", default=str(PROJECT_DIR / ".env.meta"))
    args = parser.parse_args()

    load_env_file(Path(args.env_file))

    token = os.getenv("META_ACCESS_TOKEN", "").strip()
    ig_user_id = os.getenv("META_IG_USER_ID", "").strip()

    if not token or not ig_user_id:
        print("ERRO: META_ACCESS_TOKEN e META_IG_USER_ID precisam estar configurados.")
        return 1

    print("Diagnostico Meta")
    print(f"IG User ID: {ig_user_id}")
    print(f"Token configurado: sim ({len(token)} caracteres)")
    print(f"Host Graph: {'graph.instagram.com' if token.startswith('IG') else 'graph.facebook.com'}")
    print("")

    checks = [
        ("Token basico", "me", {"fields": "id,name", "access_token": token}),
        (
            "Conta Instagram",
            ig_user_id,
            {"fields": "id,username,name,account_type", "access_token": token},
        ),
        (
            "Limite de publicacao",
            f"{ig_user_id}/content_publishing_limit",
            {"fields": "config,quota_usage", "access_token": token},
        ),
    ]

    failed = False
    for label, path, params in checks:
        ok, data = graph_get(path, params)
        if ok:
            print(f"OK: {label}")
            safe_data = {key: value for key, value in data.items() if key != "access_token"}
            print(json.dumps(safe_data, ensure_ascii=False, indent=2))
        else:
            failed = True
            print(f"FALHA: {label}")
            print(summarize_error(data))
        print("")

    if failed:
        print("Resultado: token/permissao ainda nao esta pronto para publicar.")
        return 1

    print("Resultado: token e conta responderam. Proximo teste pode ser criacao de container.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
