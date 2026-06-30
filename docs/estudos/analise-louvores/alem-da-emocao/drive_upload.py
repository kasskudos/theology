import argparse
import json
import re
from pathlib import Path


BASE_VIDEO_DIR = Path(r"C:\Users\PICHAU\Documents\Além da Emoção")
PROJECT_DIR = Path(__file__).resolve().parent
DEFAULT_CREDENTIALS = PROJECT_DIR / "google_client_secret.json"
DEFAULT_TOKEN = PROJECT_DIR / "google_token.json"

SCOPES = ["https://www.googleapis.com/auth/drive.file"]


def import_google_libs():
    try:
        import google.auth
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from googleapiclient.discovery import build
        from googleapiclient.http import MediaFileUpload
    except ImportError as error:
        raise RuntimeError(
            "Dependencias do Google Drive ausentes. Instale com:\n"
            "py -m pip install google-api-python-client google-auth-oauthlib google-auth-httplib2"
        ) from error

    return google.auth, Request, Credentials, InstalledAppFlow, build, MediaFileUpload


def normalize_episode(value: str) -> tuple[str, int]:
    cleaned = value.strip().upper().replace(" ", "")
    match = re.fullmatch(r"(?:EP)?0*(\d+)", cleaned)
    if not match:
        raise RuntimeError(f"Episodio invalido: {value}. Use algo como EP02 ou 2.")

    number = int(match.group(1))
    return f"EP{number:02d}", number


def resolve_episode_dir(value: str) -> tuple[str, Path]:
    path = Path(value)
    if path.exists():
        match = re.search(r"EP0*(\d+)$", path.name, flags=re.IGNORECASE)
        if not match:
            raise RuntimeError(f"Nao consegui descobrir o numero do episodio pela pasta: {path}")
        episode_id, _ = normalize_episode(match.group(1))
        return episode_id, path

    episode_id, episode_number = normalize_episode(value)
    episode_dir = BASE_VIDEO_DIR / f"EP{episode_number}"
    if not episode_dir.exists():
        raise RuntimeError(f"Pasta do episodio nao encontrada: {episode_dir}")
    return episode_id, episode_dir


def load_existing_map(path: Path) -> dict:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def save_map(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def get_credentials(credentials_path: Path, token_path: Path):
    _, Request, Credentials, InstalledAppFlow, _, _ = import_google_libs()

    creds = None
    if token_path.exists():
        creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)

    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())

    if not creds or not creds.valid:
        if not credentials_path.exists():
            raise RuntimeError(
                f"Arquivo de credenciais nao encontrado: {credentials_path}\n"
                "Baixe o OAuth Client do Google Cloud como app Desktop e salve com esse nome."
            )
        flow = InstalledAppFlow.from_client_secrets_file(str(credentials_path), SCOPES)
        creds = flow.run_local_server(port=0)

    token_path.write_text(creds.to_json(), encoding="utf-8")
    return creds


def get_adc_credentials():
    google_auth, Request, _, _, _, _ = import_google_libs()
    creds, _ = google_auth.default(scopes=SCOPES)
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    return creds


def build_drive_service(credentials_path: Path, token_path: Path, auth_mode: str):
    _, _, _, _, build, _ = import_google_libs()
    if auth_mode == "oauth":
        creds = get_credentials(credentials_path, token_path)
    elif auth_mode == "adc":
        creds = get_adc_credentials()
    elif credentials_path.exists():
        creds = get_credentials(credentials_path, token_path)
    else:
        creds = get_adc_credentials()
    return build("drive", "v3", credentials=creds)


def q_escape(value: str) -> str:
    return value.replace("\\", "\\\\").replace("'", "\\'")


def find_or_create_folder(service, folder_name: str, parent_id: str | None) -> str:
    query_parts = [
        "mimeType = 'application/vnd.google-apps.folder'",
        "trashed = false",
        f"name = '{q_escape(folder_name)}'",
    ]
    if parent_id:
        query_parts.append(f"'{q_escape(parent_id)}' in parents")

    result = service.files().list(
        q=" and ".join(query_parts),
        fields="files(id, name)",
        pageSize=1,
        spaces="drive",
    ).execute()
    files = result.get("files", [])
    if files:
        return files[0]["id"]

    metadata = {
        "name": folder_name,
        "mimeType": "application/vnd.google-apps.folder",
    }
    if parent_id:
        metadata["parents"] = [parent_id]

    folder = service.files().create(body=metadata, fields="id").execute()
    return folder["id"]


def make_public(service, file_id: str) -> None:
    service.permissions().create(
        fileId=file_id,
        body={"type": "anyone", "role": "reader"},
        fields="id",
    ).execute()


def upload_file(service, local_path: Path, folder_id: str) -> dict:
    _, _, _, _, _, MediaFileUpload = import_google_libs()
    media = MediaFileUpload(str(local_path), resumable=True)
    metadata = {"name": local_path.name, "parents": [folder_id]}

    created = service.files().create(
        body=metadata,
        media_body=media,
        fields="id, name, webViewLink",
    ).execute()
    make_public(service, created["id"])

    return {
        "drive_id": created["id"],
        "web_view_link": created.get("webViewLink", ""),
        "download_url": f"https://drive.google.com/uc?export=download&id={created['id']}",
    }


def discover_cuts(episode_dir: Path) -> list[int]:
    cuts = []
    for path in episode_dir.glob("corte *.mp4"):
        match = re.fullmatch(r"corte\s+(\d+)", path.stem, flags=re.IGNORECASE)
        if match:
            cuts.append(int(match.group(1)))
    return sorted(cuts)


def validate_assets(episode_dir: Path, number: int) -> tuple[Path, Path]:
    video = episode_dir / f"corte {number}.mp4"
    cover = episode_dir / f"capa_{number:02d}.png"
    missing = [str(path) for path in (video, cover) if not path.exists()]
    if missing:
        raise RuntimeError("Arquivos ausentes para o corte " + str(number) + ": " + ", ".join(missing))
    return video, cover


def upload_cut(service, episode_dir: Path, folder_id: str, number: int) -> dict:
    video, cover = validate_assets(episode_dir, number)

    print(f"Upload Drive: corte {number} - video")
    video_result = upload_file(service, video, folder_id)

    print(f"Upload Drive: corte {number} - capa")
    cover_result = upload_file(service, cover, folder_id)

    return {
        "video_file": video.name,
        "cover_file": cover.name,
        "video_drive_id": video_result["drive_id"],
        "cover_drive_id": cover_result["drive_id"],
        "video_url": video_result["download_url"],
        "cover_url": cover_result["download_url"],
        "video_web_view_link": video_result["web_view_link"],
        "cover_web_view_link": cover_result["web_view_link"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Sobe videos e capas do Alem da Emocao para o Google Drive e gera drive_urls.json."
    )
    parser.add_argument("episode", help="Episodio ou pasta externa, ex: EP02 ou C:\\...\\EP2")
    parser.add_argument("--cut", type=int, action="append", help="Corte especifico. Pode repetir.")
    parser.add_argument("--credentials", default=str(DEFAULT_CREDENTIALS), help="Arquivo OAuth client JSON.")
    parser.add_argument("--token", default=str(DEFAULT_TOKEN), help="Arquivo local do token OAuth.")
    parser.add_argument(
        "--auth",
        choices=("auto", "oauth", "adc"),
        default="auto",
        help="Modo de autenticacao. auto usa OAuth JSON se existir; senao usa gcloud ADC.",
    )
    parser.add_argument("--folder-id", help="ID de uma pasta existente no Drive.")
    parser.add_argument("--folder-name", help="Nome da pasta a criar/usar no Drive.")
    parser.add_argument("--parent-folder-id", help="ID da pasta mae no Drive.")
    parser.add_argument("--out", help="Arquivo JSON de saida. Padrao: drive_urls.json na pasta do episodio.")
    parser.add_argument("--overwrite", action="store_true", help="Faz upload novamente mesmo se o corte ja estiver mapeado.")
    parser.add_argument("--dry-run", action="store_true", help="Valida arquivos locais sem enviar ao Drive.")
    args = parser.parse_args()

    try:
        episode_id, episode_dir = resolve_episode_dir(args.episode)
        out_path = Path(args.out) if args.out else episode_dir / "drive_urls.json"
        cuts = args.cut or discover_cuts(episode_dir)
        if not cuts:
            raise RuntimeError(f"Nenhum video no padrao 'corte N.mp4' encontrado em: {episode_dir}")

        existing = load_existing_map(out_path)
        pending = []
        for number in cuts:
            validate_assets(episode_dir, number)
            if not args.overwrite and str(number) in existing:
                print(f"Drive: corte {number} ja mapeado, pulando. Use --overwrite para reenviar.")
                continue
            pending.append(number)

        if args.dry_run:
            print(json.dumps({
                "status": "dry-run",
                "episode": episode_id,
                "episode_dir": str(episode_dir),
                "cuts": cuts,
                "pending_upload": pending,
                "out": str(out_path),
            }, ensure_ascii=False, indent=2))
            return 0

        if pending:
            service = build_drive_service(Path(args.credentials), Path(args.token), args.auth)
            folder_id = args.folder_id
            if not folder_id:
                folder_name = args.folder_name or f"Alem da Emocao {episode_id}"
                folder_id = find_or_create_folder(service, folder_name, args.parent_folder_id)

            existing["_meta"] = {
                "episode": episode_id,
                "episode_dir": str(episode_dir),
                "drive_folder_id": folder_id,
            }
            for number in pending:
                existing[str(number)] = upload_cut(service, episode_dir, folder_id, number)

        save_map(out_path, existing)
        print(f"Mapa de URLs salvo em: {out_path}")
        return 0
    except RuntimeError as error:
        print(f"ERRO: {error}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
