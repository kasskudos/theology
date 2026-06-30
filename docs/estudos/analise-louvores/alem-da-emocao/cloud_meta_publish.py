import argparse
import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo


BASE_DIR = Path(__file__).resolve().parent
SCHEDULES_DIR = BASE_DIR / "schedules"


def required_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise RuntimeError(f"Variavel ausente: {name}")
    return value


def graph_base(token: str) -> str:
    version = os.getenv("META_GRAPH_VERSION", "v23.0")
    host = os.getenv("META_GRAPH_HOST", "").strip().lower()
    if host in ("instagram", "graph.instagram.com") or token.startswith("IG"):
        return f"https://graph.instagram.com/{version}"
    return f"https://graph.facebook.com/{version}"


def api_post(path: str, params: dict[str, str]) -> dict:
    token = params.get("access_token", "")
    data = urllib.parse.urlencode(params).encode("utf-8")
    request = urllib.request.Request(
        f"{graph_base(token)}/{path.lstrip('/')}",
        data=data,
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        body = error.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Meta HTTP {error.code}: {body}") from error


def api_get(path: str, params: dict[str, str]) -> dict:
    token = params.get("access_token", "")
    url = f"{graph_base(token)}/{path.lstrip('/')}?" + urllib.parse.urlencode(params)
    request = urllib.request.Request(url, method="GET")
    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        body = error.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Meta HTTP {error.code}: {body}") from error


def drive_media_url(file_id: str, api_key: str) -> str:
    query = urllib.parse.urlencode({"alt": "media", "key": api_key})
    return f"https://www.googleapis.com/drive/v3/files/{file_id}?{query}"


def wait_until_ready(access_token: str, creation_id: str, timeout_seconds: int = 600) -> dict:
    deadline = time.time() + timeout_seconds
    last_response = {}
    while time.time() < deadline:
        response = api_get(
            creation_id,
            {"access_token": access_token, "fields": "status_code,status"},
        )
        last_response = response
        status_code = response.get("status_code")
        print(f"Container {creation_id}: {status_code or response}")
        if status_code == "FINISHED":
            return response
        if status_code in {"ERROR", "EXPIRED"}:
            raise RuntimeError(f"Container nao publicavel: {response}")
        time.sleep(20)
    raise RuntimeError(f"Container nao ficou pronto: {last_response}")


def publish_item(item: dict, access_token: str, ig_user_id: str, drive_api_key: str, dry_run: bool) -> dict:
    video_url = drive_media_url(item["video_drive_id"], drive_api_key)
    cover_url = drive_media_url(item["cover_drive_id"], drive_api_key)
    payload = {
        "cut": item["cut"],
        "date": item["date"],
        "time": item["time"],
        "video_drive_id": item["video_drive_id"],
        "cover_drive_id": item["cover_drive_id"],
    }

    if dry_run:
        payload["status"] = "dry-run"
        return payload

    container = api_post(
        f"{ig_user_id}/media",
        {
            "access_token": access_token,
            "media_type": "REELS",
            "video_url": video_url,
            "cover_url": cover_url,
            "caption": item["caption"],
            "share_to_feed": "true",
        },
    )
    creation_id = container["id"]
    payload["creation_id"] = creation_id
    payload["container_status"] = wait_until_ready(access_token, creation_id)

    published = api_post(
        f"{ig_user_id}/media_publish",
        {"access_token": access_token, "creation_id": creation_id},
    )
    media_id = published["id"]
    payload["media_id"] = media_id

    comment = item.get("comment", "").strip()
    if comment:
        comment_response = api_post(
            f"{media_id}/comments",
            {"access_token": access_token, "message": comment},
        )
        payload["comment_id"] = comment_response.get("id")

    payload["status"] = "published"
    return payload


def normalize_episode(value: str) -> str:
    digits = "".join(char for char in value if char.isdigit())
    if not digits:
        raise RuntimeError(f"Episodio invalido: {value}")
    return f"EP{int(digits):02d}"


def load_schedules(schedule_path: str | None, episode: str | None) -> list[tuple[Path, dict]]:
    if schedule_path:
        path = Path(schedule_path)
        return [(path, json.loads(path.read_text(encoding="utf-8")))]

    if episode:
        path = SCHEDULES_DIR / f"{normalize_episode(episode)}.json"
        return [(path, json.loads(path.read_text(encoding="utf-8")))]

    schedules = []
    for path in sorted(SCHEDULES_DIR.glob("*.json")):
        schedules.append((path, json.loads(path.read_text(encoding="utf-8"))))
    if not schedules:
        raise RuntimeError(f"Nenhuma agenda encontrada em: {SCHEDULES_DIR}")
    return schedules


def select_items(schedule: dict, cut: int | None, run_date: str | None) -> list[dict]:
    items = schedule["items"]
    if cut is not None:
        return [item for item in items if int(item["cut"]) == cut]

    timezone = ZoneInfo(schedule.get("timezone", "America/Sao_Paulo"))
    today = run_date or datetime.now(timezone).date().isoformat()
    return [item for item in items if item["date"] == today]


def main() -> int:
    parser = argparse.ArgumentParser(description="Publica cortes agendados do Alem da Emocao em ambiente cloud.")
    parser.add_argument("--schedule", help="Arquivo JSON de agenda. Padrao: todas as agendas em schedules/.")
    parser.add_argument("--episode", help="Episodio especifico, exemplo EP03.")
    parser.add_argument("--cut", type=int, help="Publica um corte especifico.")
    parser.add_argument("--date", help="Data YYYY-MM-DD a publicar. Padrao: hoje em America/Sao_Paulo.")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    try:
        access_token = required_env("META_ACCESS_TOKEN")
        ig_user_id = os.getenv("META_IG_USER_ID", "").strip() or os.getenv("META_IG_USER_ID_INSTAGRAM", "").strip()
        if not ig_user_id:
            raise RuntimeError("Variavel ausente: META_IG_USER_ID")
        drive_api_key = required_env("GOOGLE_DRIVE_API_KEY")

        schedules = load_schedules(args.schedule, args.episode)
        selected = []
        for schedule_path, schedule in schedules:
            for item in select_items(schedule, args.cut, args.date):
                item = dict(item)
                item["_schedule_path"] = str(schedule_path)
                item["_episode"] = schedule.get("episode", schedule_path.stem)
                selected.append(item)
        if not selected:
            print("Nenhum corte selecionado para esta execucao.")
            return 0

        for item in selected:
            print(f"Publicando {item['_episode']} corte {item['cut']} ({item['date']} {item['time']})")
            result = publish_item(item, access_token, ig_user_id, drive_api_key, args.dry_run)
            print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except RuntimeError as error:
        print(f"ERRO: {error}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
