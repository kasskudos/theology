import argparse
import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parent
BASE_VIDEO_DIR = Path(os.getenv("ALEM_DA_EMOCAO_VIDEO_DIR", Path.home() / "Documents" / "Além da Emoção"))


@dataclass
class MetaConfig:
    access_token: str
    ig_user_id: str
    public_video_base_url: str = ""
    public_cover_base_url: str = ""
    graph_host: str = ""
    google_drive_api_key: str = ""


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


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


def load_config(require_base_urls: bool) -> MetaConfig:
    access_token = os.getenv("META_ACCESS_TOKEN", "").strip()
    ig_user_id = os.getenv("META_IG_USER_ID", "").strip()
    public_video_base_url = os.getenv("META_PUBLIC_VIDEO_BASE_URL", "").strip()
    public_cover_base_url = os.getenv("META_PUBLIC_COVER_BASE_URL", "").strip()
    graph_host = os.getenv("META_GRAPH_HOST", "").strip()
    google_drive_api_key = os.getenv("GOOGLE_DRIVE_API_KEY", "").strip()

    missing = [
        name
        for name, value in [
            ("META_ACCESS_TOKEN", access_token),
            ("META_IG_USER_ID", ig_user_id),
        ]
        if not value
    ]
    if require_base_urls:
        missing.extend(
            name
            for name, value in [
                ("META_PUBLIC_VIDEO_BASE_URL", public_video_base_url),
                ("META_PUBLIC_COVER_BASE_URL", public_cover_base_url),
            ]
            if not value
        )
    if missing:
        raise RuntimeError("Variaveis ausentes: " + ", ".join(missing))

    return MetaConfig(
        access_token=access_token,
        ig_user_id=ig_user_id,
        public_video_base_url=public_video_base_url.rstrip("/") + "/" if public_video_base_url else "",
        public_cover_base_url=public_cover_base_url.rstrip("/") + "/" if public_cover_base_url else "",
        graph_host=graph_host,
        google_drive_api_key=google_drive_api_key,
    )


def graph_base_for_token(token: str, configured_host: str = "") -> str:
    graph_version = os.getenv("META_GRAPH_VERSION", "v23.0")
    host = configured_host.lower().strip()
    if host in ("instagram", "graph.instagram.com"):
        domain = "graph.instagram.com"
    elif host in ("facebook", "graph.facebook.com"):
        domain = "graph.facebook.com"
    elif token.startswith("IG"):
        domain = "graph.instagram.com"
    else:
        domain = "graph.facebook.com"
    return f"https://{domain}/{graph_version}"


def api_post(path: str, params: dict[str, str]) -> dict:
    graph_base = graph_base_for_token(
        params.get("access_token", ""),
        os.getenv("META_GRAPH_HOST", ""),
    )
    data = urllib.parse.urlencode(params).encode("utf-8")
    request = urllib.request.Request(
        f"{graph_base}/{path.lstrip('/')}",
        data=data,
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        body = error.read().decode("utf-8", errors="replace")
        raise RuntimeError(
            f"Erro HTTP {error.code} na Meta Graph API.\n"
            f"Endpoint: {graph_base}/{path.lstrip('/')}\n"
            f"Resposta: {body}"
        ) from error


def api_get(path: str, params: dict[str, str]) -> dict:
    graph_base = graph_base_for_token(
        params.get("access_token", ""),
        os.getenv("META_GRAPH_HOST", ""),
    )
    url = f"{graph_base}/{path.lstrip('/')}?" + urllib.parse.urlencode(params)
    request = urllib.request.Request(url, method="GET")
    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        body = error.read().decode("utf-8", errors="replace")
        raise RuntimeError(
            f"Erro HTTP {error.code} na Meta Graph API.\n"
            f"Endpoint: {url}\n"
            f"Resposta: {body}"
        ) from error


def public_url(base_url: str, filename: str) -> str:
    return urllib.parse.urljoin(base_url, urllib.parse.quote(filename))


def load_asset_urls(path: Path | None) -> dict:
    if not path:
        return {}
    if not path.exists():
        raise RuntimeError(f"Mapa de URLs nao encontrado: {path}")
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise RuntimeError(f"Mapa de URLs invalido: {path}")
    return data


def drive_media_url(file_id: str, api_key: str) -> str:
    query = urllib.parse.urlencode({"alt": "media", "key": api_key})
    return f"https://www.googleapis.com/drive/v3/files/{file_id}?{query}"


def redact_url_secrets(url: str) -> str:
    parsed = urllib.parse.urlsplit(url)
    query = urllib.parse.parse_qsl(parsed.query, keep_blank_values=True)
    redacted_query = urllib.parse.urlencode(
        [(key, "[REDACTED]") if key.lower() == "key" else (key, value) for key, value in query]
    )
    return urllib.parse.urlunsplit(
        (parsed.scheme, parsed.netloc, parsed.path, redacted_query, parsed.fragment)
    )


def asset_urls_for_cut(asset_urls: dict, number: int, google_drive_api_key: str) -> tuple[str, str] | None:
    item = asset_urls.get(str(number))
    if not item:
        return None

    if google_drive_api_key and item.get("video_drive_id") and item.get("cover_drive_id"):
        video_url = drive_media_url(item["video_drive_id"], google_drive_api_key)
        cover_url = drive_media_url(item["cover_drive_id"], google_drive_api_key)
    else:
        video_url = item.get("video_url", "").strip()
        cover_url = item.get("cover_url", "").strip()

    if not video_url or not cover_url:
        raise RuntimeError(f"Mapa de URLs incompleto para o corte {number}")
    return video_url, cover_url


def create_reel_container(config: MetaConfig, video_url: str, cover_url: str, caption: str) -> str:
    response = api_post(
        f"{config.ig_user_id}/media",
        {
            "access_token": config.access_token,
            "media_type": "REELS",
            "video_url": video_url,
            "cover_url": cover_url,
            "caption": caption,
            "share_to_feed": "true",
        },
    )
    creation_id = response.get("id")
    if not creation_id:
        raise RuntimeError(f"Resposta sem creation_id: {response}")
    return creation_id


def publish_container(config: MetaConfig, creation_id: str) -> str:
    response = api_post(
        f"{config.ig_user_id}/media_publish",
        {
            "access_token": config.access_token,
            "creation_id": creation_id,
        },
    )
    media_id = response.get("id")
    if not media_id:
        raise RuntimeError(f"Resposta sem media_id: {response}")
    return media_id


def wait_until_container_ready(config: MetaConfig, creation_id: str, timeout_seconds: int = 600) -> dict:
    deadline = time.time() + timeout_seconds
    last_response = {}

    while time.time() < deadline:
        response = api_get(
            creation_id,
            {
                "access_token": config.access_token,
                "fields": "status_code,status",
            },
        )
        last_response = response
        status_code = response.get("status_code")
        status = response.get("status")
        print(f"Status container {creation_id}: {status_code or status or response}")

        if status_code == "FINISHED":
            return response
        if status_code in {"ERROR", "EXPIRED"}:
            raise RuntimeError(f"Container nao ficou publicavel: {response}")

        time.sleep(20)

    raise RuntimeError(f"Container nao ficou pronto dentro do tempo limite: {last_response}")


def create_comment(config: MetaConfig, media_id: str, message: str) -> str:
    response = api_post(
        f"{media_id}/comments",
        {
            "access_token": config.access_token,
            "message": message,
        },
    )
    comment_id = response.get("id")
    if not comment_id:
        raise RuntimeError(f"Resposta sem comment_id: {response}")
    return comment_id


def find_episode_dir(episode_dir: str) -> Path:
    path = Path(episode_dir)
    if path.exists():
        return path

    cleaned = episode_dir.strip().upper().replace(" ", "")
    match = cleaned if cleaned.startswith("EP") else f"EP{cleaned}"
    digits = "".join(char for char in match if char.isdigit())
    if digits:
        path = BASE_VIDEO_DIR / f"EP{int(digits)}"
    if not path.exists():
        raise RuntimeError(f"Pasta nao encontrada: {path}")
    return path


def publish_cut(config: MetaConfig, episode_dir: Path, number: int, dry_run: bool, asset_urls: dict) -> dict:
    video = episode_dir / f"corte {number}.mp4"
    cover = episode_dir / f"capa_{number:02d}.png"
    caption = episode_dir / f"legenda_{number:02d}.txt"
    comment = episode_dir / f"comentario_fixado_{number:02d}.txt"

    for path in (video, cover, caption, comment):
        if not path.exists():
            raise RuntimeError(f"Arquivo necessario nao encontrado: {path}")

    mapped_urls = asset_urls_for_cut(asset_urls, number, config.google_drive_api_key)
    if mapped_urls:
        video_url, cover_url = mapped_urls
    elif config.public_video_base_url and config.public_cover_base_url:
        video_url = public_url(config.public_video_base_url, video.name)
        cover_url = public_url(config.public_cover_base_url, cover.name)
    else:
        raise RuntimeError(
            "URLs publicas ausentes. Use --asset-urls apontando para drive_urls.json "
            "ou configure META_PUBLIC_VIDEO_BASE_URL e META_PUBLIC_COVER_BASE_URL."
        )
    caption_text = read_text(caption).strip()
    comment_text = read_text(comment).strip()

    payload = {
        "cut": number,
        "video_url": redact_url_secrets(video_url),
        "cover_url": redact_url_secrets(cover_url),
        "caption_file": str(caption),
        "comment_file": str(comment),
    }

    if dry_run:
        payload["status"] = "dry-run"
        return payload

    creation_id = create_reel_container(config, video_url, cover_url, caption_text)
    payload["creation_id"] = creation_id

    payload["container_status"] = wait_until_container_ready(config, creation_id)

    media_id = publish_container(config, creation_id)
    payload["media_id"] = media_id

    comment_id = create_comment(config, media_id, comment_text)
    payload["comment_id"] = comment_id
    payload["status"] = "published"
    payload["pin_note"] = "Fixar comentario ainda deve ser feito manualmente se a API nao disponibilizar esse recurso."
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Publica Reels do Alem da Emocao usando Instagram Graph API."
    )
    parser.add_argument("episode_dir", help="Pasta externa do episodio, ex: C:\\...\\EP2")
    parser.add_argument("--cut", type=int, action="append", help="Corte especifico. Pode repetir.")
    parser.add_argument("--asset-urls", help="Mapa JSON gerado por drive_upload.py, ex: drive_urls.json.")
    parser.add_argument("--env-file", default=str(PROJECT_DIR / ".env.meta"), help="Arquivo local com credenciais Meta.")
    parser.add_argument("--dry-run", action="store_true", help="Mostra payloads sem publicar.")
    parser.add_argument(
        "--schedule-at",
        help=(
            "Reservado para agendamento nativo da Meta. "
            "A Instagram API atual deste fluxo nao expõe agendamento de Reels."
        ),
    )
    parser.add_argument("--out", help="Arquivo JSONL de resultado.")
    args = parser.parse_args()

    if args.schedule_at:
        print(
            "ERRO: agendamento nativo de Reels nao esta disponivel neste endpoint da Instagram API.\n"
            "Nao sera criado agendamento local. Use Meta Business Suite manualmente ou outro endpoint oficial "
            "que exponha agendamento nativo para a conta."
        )
        return 1

    try:
        load_env_file(Path(args.env_file))
        episode_dir = find_episode_dir(args.episode_dir)
        asset_urls_path = Path(args.asset_urls) if args.asset_urls else episode_dir / "drive_urls.json"
        asset_urls = load_asset_urls(asset_urls_path) if asset_urls_path.exists() else {}
        config = load_config(require_base_urls=not bool(asset_urls))
    except RuntimeError as error:
        print(f"ERRO: {error}")
        return 1

    cuts = args.cut
    if not cuts:
        cuts = sorted(
            int(path.stem.split("_")[-1])
            for path in episode_dir.glob("legenda_*.txt")
        )

    results = []
    for number in cuts:
        try:
            print(f"Publicacao Meta: corte {number}")
            result = publish_cut(config, episode_dir, number, dry_run=args.dry_run, asset_urls=asset_urls)
            print(json.dumps(result, ensure_ascii=False, indent=2))
            results.append(result)
        except RuntimeError as error:
            print(f"ERRO: {error}")
            return 1

    if args.out:
        out_path = Path(args.out)
        out_path.write_text(
            "\n".join(json.dumps(item, ensure_ascii=False) for item in results) + "\n",
            encoding="utf-8",
        )
        print(f"Resultado salvo em: {out_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
