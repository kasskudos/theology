import argparse
import csv
import json
import re
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
EPISODES_DIR = BASE_DIR / "episodios"
TEMPLATES_DIR = BASE_DIR / "templates"
DRIVE_UPLOAD_SCRIPT = BASE_DIR / "drive_upload.py"
META_PUBLISH_SCRIPT = BASE_DIR / "meta_publish.py"
DEFAULT_GOOGLE_CREDENTIALS = BASE_DIR / "google_client_secret.json"
DEFAULT_EXTERNAL_ROOT = Path.home() / "Documents" / "Além da Emoção"
EXPECTED_WIDTH = 1080
EXPECTED_HEIGHT = 1350


TIMESTAMP_RE = re.compile(r"^\s*(?P<ts>(?:\d+s|\d+:\d{2}))\s+(?P<text>.*)$")
CUT_RE = re.compile(r"^\s*Corte\s+(?P<number>\d+)\s*$", re.IGNORECASE)
EPISODE_RE = re.compile(r"\bEP\s*0*(?P<number>\d+)\b", re.IGNORECASE)
VIDEO_RE = re.compile(r"^corte (?P<number>\d+)\.mp4$", re.IGNORECASE)


@dataclass
class TranscriptLine:
    timestamp: str
    seconds: int
    text: str


@dataclass
class Cut:
    number: int
    start_timestamp: str
    end_timestamp: str
    start_seconds: int
    end_seconds: int


@dataclass
class Episode:
    title: str
    series: str
    episode_raw: str
    episode_number: int
    episode_normalized: str
    youtube_url: str
    transcript: list[TranscriptLine]
    cuts: list[Cut]


def read_text(path: Path) -> str:
    for encoding in ("utf-8-sig", "utf-8", "cp1252"):
        try:
            return path.read_text(encoding=encoding)
        except UnicodeDecodeError:
            continue
    return path.read_text(encoding="utf-8", errors="replace")


def parse_timestamp(value: str) -> int:
    value = value.strip()
    if value.endswith("s"):
        return int(value[:-1])
    minutes, seconds = value.split(":", 1)
    return int(minutes) * 60 + int(seconds)


def normalize_episode_number(number: int) -> str:
    return f"EP{number:02d}"


def episode_folder_name(number: int) -> str:
    return f"EP{number}"


def clean_transcript_text(text: str) -> str:
    text = text.replace(">> ", "")
    text = text.replace(">>", "")
    return re.sub(r"\s+", " ", text).strip()


def parse_header(header_line: str) -> tuple[str, str, str, int, str]:
    parts = [part.strip() for part in header_line.split(" - ")]
    if len(parts) < 3:
        raise ValueError(
            "A primeira linha deve seguir o formato: Louvor - Alem da Emocao - EP2"
        )

    title = parts[0]
    series = parts[1]
    episode_raw = parts[-1]
    match = EPISODE_RE.search(episode_raw)
    if not match:
        raise ValueError("Nao encontrei o episodio na primeira linha, exemplo esperado: EP2")

    episode_number = int(match.group("number"))
    return title, series, episode_raw, episode_number, normalize_episode_number(episode_number)


def parse_transcript_lines(lines: list[str]) -> list[TranscriptLine]:
    transcript: list[TranscriptLine] = []
    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.lower() == "time\tsubtitle":
            continue

        match = TIMESTAMP_RE.match(line)
        if not match:
            continue

        timestamp = match.group("ts")
        transcript.append(
            TranscriptLine(
                timestamp=timestamp,
                seconds=parse_timestamp(timestamp),
                text=match.group("text").strip(),
            )
        )

    return transcript


def parse_cuts(lines: list[str]) -> list[Cut]:
    cuts: list[Cut] = []
    current_number: int | None = None
    current_time_lines: list[TranscriptLine] = []

    def flush_current() -> None:
        nonlocal current_number, current_time_lines
        if current_number is None:
            return
        if len(current_time_lines) < 2:
            raise ValueError(f"Corte {current_number} precisa ter ao menos inicio e fim.")

        start = current_time_lines[0]
        end = current_time_lines[-1]
        if end.seconds < start.seconds:
            raise ValueError(f"Corte {current_number} tem fim antes do inicio.")

        cuts.append(
            Cut(
                number=current_number,
                start_timestamp=start.timestamp,
                end_timestamp=end.timestamp,
                start_seconds=start.seconds,
                end_seconds=end.seconds,
            )
        )
        current_number = None
        current_time_lines = []

    for line in lines:
        cut_match = CUT_RE.match(line)
        if cut_match:
            flush_current()
            current_number = int(cut_match.group("number"))
            current_time_lines = []
            continue

        if current_number is None:
            continue

        timestamp_match = TIMESTAMP_RE.match(line)
        if timestamp_match:
            timestamp = timestamp_match.group("ts")
            current_time_lines.append(
                TranscriptLine(
                    timestamp=timestamp,
                    seconds=parse_timestamp(timestamp),
                    text=timestamp_match.group("text").strip(),
                )
            )

    flush_current()
    return cuts


def parse_episode(path: Path) -> Episode:
    content = read_text(path)
    lines = content.splitlines()
    useful_lines = [line for line in lines if line.strip()]
    if not useful_lines:
        raise ValueError(f"Arquivo vazio: {path}")

    title, series, episode_raw, episode_number, episode_normalized = parse_header(useful_lines[0])
    youtube_url = ""

    first_cut_index = None
    for index, line in enumerate(lines):
        if line.lower().startswith("youtube:"):
            youtube_url = line.split(":", 1)[1].strip()
        if CUT_RE.match(line):
            first_cut_index = index
            break

    if first_cut_index is None:
        raise ValueError("Nao encontrei a lista de cortes. Esperado: Corte 1")

    transcript_lines = parse_transcript_lines(lines[:first_cut_index])
    cuts = parse_cuts(lines[first_cut_index:])

    if not transcript_lines:
        raise ValueError("Nao encontrei linhas de transcricao com timestamp.")
    if not cuts:
        raise ValueError("Nao encontrei cortes validos.")

    return Episode(
        title=title,
        series=series,
        episode_raw=episode_raw,
        episode_number=episode_number,
        episode_normalized=episode_normalized,
        youtube_url=youtube_url,
        transcript=transcript_lines,
        cuts=cuts,
    )


def resolve_episode_file(value: str) -> Path:
    candidate = Path(value)
    if candidate.exists():
        return candidate

    match = EPISODE_RE.search(value)
    if not match:
        raise ValueError("Informe um episodio como EP02 ou um caminho de arquivo.")

    normalized = normalize_episode_number(int(match.group("number")))
    return EPISODES_DIR / f"{normalized}.txt"


def external_episode_dir(episode: Episode, external_root: Path) -> Path:
    return external_root / episode_folder_name(episode.episode_number)


def cut_video_path(output_dir: Path, number: int) -> Path:
    return output_dir / f"corte {number}.mp4"


def transcript_output_path(output_dir: Path, number: int) -> Path:
    return output_dir / f"transcricao_corte_{number:02d}.txt"


def editorial_package_path(output_dir: Path, number: int) -> Path:
    return output_dir / f"pacote_editorial_{number:02d}.txt"


def caption_output_path(output_dir: Path, number: int) -> Path:
    return output_dir / f"legenda_{number:02d}.txt"


def pinned_comment_output_path(output_dir: Path, number: int) -> Path:
    return output_dir / f"comentario_fixado_{number:02d}.txt"


def poll_output_path(output_dir: Path, number: int) -> Path:
    return output_dir / f"enquete_{number:02d}.txt"


def cover_text_output_path(output_dir: Path, number: int) -> Path:
    return output_dir / f"texto_capa_{number:02d}.txt"


def cover_prompt_output_path(output_dir: Path, number: int) -> Path:
    return output_dir / f"prompt_capa_{number:02d}.txt"


def extract_cut_transcript(episode: Episode, cut: Cut) -> list[TranscriptLine]:
    return [
        line
        for line in episode.transcript
        if cut.start_seconds <= line.seconds <= cut.end_seconds
    ]


def format_cut_transcript(lines: list[TranscriptLine]) -> str:
    return "\n".join(
        f"{line.timestamp}\t{clean_transcript_text(line.text)}" for line in lines
    ).strip() + "\n"


def render_template(template: str, values: dict[str, str]) -> str:
    rendered = template
    for key, value in values.items():
        rendered = rendered.replace("{{" + key + "}}", value)
    return rendered


def parse_named_blocks(text: str) -> dict[str, str]:
    headings = [
        "TITULO_INTERNO",
        "OBJETIVO_DO_REEL",
        "TEMA_CENTRAL",
        "TEXTO_CAPA",
        "LEGENDA",
        "COMENTARIO_FIXADO",
        "ENQUETE",
        "HASHTAGS",
        "OBSERVACOES_REVISAO",
        "CONCEITO_VISUAL",
        "METAFORA_VISUAL",
        "COMPOSICAO",
        "TEXTO_CAPA_FINAL",
        "POSICAO_IDENTIFICADOR",
        "PROMPT_IMAGEM",
        "NEGATIVE_PROMPT",
    ]
    pattern = re.compile(rf"^({'|'.join(headings)}):\s*$", re.MULTILINE)
    matches = list(pattern.finditer(text))
    blocks: dict[str, str] = {}

    for index, match in enumerate(matches):
        name = match.group(1)
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        blocks[name] = text[start:end].strip()

    return blocks


def codex_available() -> bool:
    return shutil.which("codex") is not None


def run_codex(prompt: str, output_dir: Path, stem: str, args: argparse.Namespace) -> str:
    if not codex_available():
        raise RuntimeError("Codex CLI nao encontrado no PATH.")

    output_file = output_dir / f"{stem}.raw.txt"
    command = [
        "codex",
        "exec",
        "--cd",
        str(BASE_DIR),
        "--sandbox",
        "read-only",
        "--ephemeral",
        "--output-last-message",
        str(output_file),
    ]
    if args.codex_model:
        command.extend(["--model", args.codex_model])
    command.append("-")

    if args.dry_run:
        print(f"dry-run codex: {output_file}")
        return ""

    result = subprocess.run(
        command,
        input=prompt,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if result.returncode != 0:
        raise RuntimeError(
            "Codex CLI falhou.\n"
            f"Comando: {' '.join(command)}\n"
            f"STDOUT:\n{result.stdout}\n"
            f"STDERR:\n{result.stderr}"
        )
    if not output_file.exists():
        raise RuntimeError(f"Codex CLI nao gerou o arquivo esperado: {output_file}")

    return read_text(output_file)


def run_python_step(command: list[str], dry_run: bool) -> None:
    if dry_run:
        print("dry-run comando: " + " ".join(command))
        return

    result = subprocess.run(command, text=True, encoding="utf-8", errors="replace")
    if result.returncode != 0:
        raise RuntimeError(
            "Etapa externa falhou.\n"
            f"Comando: {' '.join(command)}\n"
            f"Codigo: {result.returncode}"
        )


def run_drive_upload_step(output_dir: Path, selected_cuts: list[Cut], args: argparse.Namespace) -> None:
    if args.skip_drive_upload:
        print("skip Drive: desativado por --skip-drive-upload")
        return

    credentials = Path(args.google_credentials)
    auto_mode = not args.upload_drive
    if auto_mode and not credentials.exists():
        print(f"skip Drive: credencial ainda nao encontrada em {credentials}")
        return
    if args.upload_drive and not credentials.exists() and not args.dry_run:
        raise RuntimeError(f"Credencial do Google Drive nao encontrada: {credentials}")

    command = [
        "py",
        str(DRIVE_UPLOAD_SCRIPT),
        str(output_dir),
        "--credentials",
        str(credentials),
    ]
    if args.google_token:
        command.extend(["--token", args.google_token])
    if args.drive_folder_id:
        command.extend(["--folder-id", args.drive_folder_id])
    if args.drive_folder_name:
        command.extend(["--folder-name", args.drive_folder_name])
    if args.drive_parent_folder_id:
        command.extend(["--parent-folder-id", args.drive_parent_folder_id])
    if args.overwrite:
        command.append("--overwrite")
    if args.dry_run:
        command.append("--dry-run")
    for cut in selected_cuts:
        command.extend(["--cut", str(cut.number)])

    print("Drive: preparando upload de videos e capas")
    run_python_step(command, dry_run=False)


def run_meta_publish_step(output_dir: Path, selected_cuts: list[Cut], args: argparse.Namespace) -> None:
    if not args.publish_meta:
        return

    command = [
        "py",
        str(META_PUBLISH_SCRIPT),
        str(output_dir),
    ]
    if args.meta_env_file:
        command.extend(["--env-file", args.meta_env_file])
    if args.asset_urls:
        command.extend(["--asset-urls", args.asset_urls])
    elif (output_dir / "drive_urls.json").exists():
        command.extend(["--asset-urls", str(output_dir / "drive_urls.json")])
    if args.dry_run or args.meta_dry_run:
        command.append("--dry-run")
    if args.meta_out:
        command.extend(["--out", args.meta_out])
    for cut in selected_cuts:
        command.extend(["--cut", str(cut.number)])

    print("Meta: preparando publicacao")
    run_python_step(command, dry_run=False)


def ffprobe_dimensions(path: Path) -> tuple[int, int] | None:
    if shutil.which("ffprobe") is None:
        return None

    command = [
        "ffprobe",
        "-v",
        "error",
        "-select_streams",
        "v:0",
        "-show_entries",
        "stream=width,height",
        "-of",
        "json",
        str(path),
    ]
    result = subprocess.run(command, capture_output=True, text=True, encoding="utf-8")
    if result.returncode != 0:
        return None

    data = json.loads(result.stdout)
    streams = data.get("streams") or []
    if not streams:
        return None

    stream = streams[0]
    return int(stream["width"]), int(stream["height"])


def list_numbered_videos(output_dir: Path) -> set[int]:
    if not output_dir.exists():
        return set()

    numbers = set()
    for item in output_dir.iterdir():
        match = VIDEO_RE.match(item.name)
        if match:
            numbers.add(int(match.group("number")))
    return numbers


def write_file(path: Path, content: str, overwrite: bool, dry_run: bool) -> str:
    if path.exists() and not overwrite:
        return "skip"
    if dry_run:
        return "dry-run"
    path.write_text(content, encoding="utf-8")
    return "write"


def write_required(path: Path, content: str, overwrite: bool, dry_run: bool) -> str:
    status = write_file(path, content, overwrite=overwrite, dry_run=dry_run)
    if status == "skip":
        print(f"skip: {path}")
    else:
        print(f"{status}: {path}")
    return status


def write_schedule(
    path: Path,
    episode: Episode,
    output_dir: Path,
    start_date: date,
    overwrite: bool,
    dry_run: bool,
) -> str:
    if path.exists() and not overwrite:
        return "skip"
    if dry_run:
        return "dry-run"

    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "numero_corte",
                "data",
                "horario",
                "video",
                "transcricao",
                "legenda",
                "comentario_fixado",
                "enquete",
                "prompt_capa",
                "capa",
                "status",
                "observacoes",
            ],
        )
        writer.writeheader()
        for index, cut in enumerate(episode.cuts):
            scheduled_at = datetime.combine(start_date + timedelta(days=index), time(12, 0))
            number = cut.number
            writer.writerow(
                {
                    "numero_corte": number,
                    "data": scheduled_at.date().isoformat(),
                    "horario": scheduled_at.strftime("%H:%M"),
                    "video": str(cut_video_path(output_dir, number)),
                    "transcricao": str(transcript_output_path(output_dir, number)),
                    "legenda": str(output_dir / f"legenda_{number:02d}.txt"),
                    "comentario_fixado": str(output_dir / f"comentario_fixado_{number:02d}.txt"),
                    "enquete": str(output_dir / f"enquete_{number:02d}.txt"),
                    "prompt_capa": str(output_dir / f"prompt_capa_{number:02d}.txt"),
                    "capa": str(output_dir / f"capa_{number:02d}.png"),
                    "status": "pendente",
                    "observacoes": "",
                }
            )
    return "write"


def cut_values(
    episode: Episode,
    cut: Cut,
    total_cuts: int,
    transcript_text: str,
    extra: dict[str, str] | None = None,
) -> dict[str, str]:
    values = {
        "louvor": episode.title,
        "serie": episode.series,
        "episodio_normalizado": episode.episode_normalized,
        "numero_corte": str(cut.number),
        "total_cortes": str(total_cuts),
        "inicio_corte": cut.start_timestamp,
        "fim_corte": cut.end_timestamp,
        "youtube_url": episode.youtube_url or "(nao informado)",
        "transcricao_corte": transcript_text.strip(),
    }
    if extra:
        values.update(extra)
    return values


def generate_legend_package(
    episode: Episode,
    cut: Cut,
    output_dir: Path,
    total_cuts: int,
    overwrite: bool,
    dry_run: bool,
    args: argparse.Namespace,
) -> None:
    package_path = editorial_package_path(output_dir, cut.number)
    caption_path = caption_output_path(output_dir, cut.number)
    comment_path = pinned_comment_output_path(output_dir, cut.number)
    poll_path = poll_output_path(output_dir, cut.number)
    cover_text_path = cover_text_output_path(output_dir, cut.number)

    if package_path.exists() and not overwrite:
        print(f"skip codex legenda: {package_path}")
        return

    transcript_path = transcript_output_path(output_dir, cut.number)
    if not transcript_path.exists():
        raise RuntimeError(f"Transcricao do corte nao encontrada: {transcript_path}")

    template = read_text(TEMPLATES_DIR / "prompt-legenda.md")
    transcript_text = read_text(transcript_path)
    prompt = render_template(template, cut_values(episode, cut, total_cuts, transcript_text))

    response = run_codex(prompt, output_dir, f"codex_legenda_{cut.number:02d}", args)
    if dry_run:
        return

    blocks = parse_named_blocks(response)
    write_required(package_path, response.strip() + "\n", overwrite=True, dry_run=False)

    caption = blocks.get("LEGENDA", "").strip()
    hashtags = blocks.get("HASHTAGS", "").strip()
    if hashtags:
        caption = f"{caption}\n\n{hashtags}".strip()

    write_required(caption_path, caption + "\n", overwrite=True, dry_run=False)
    write_required(
        comment_path,
        blocks.get("COMENTARIO_FIXADO", "").strip() + "\n",
        overwrite=True,
        dry_run=False,
    )
    write_required(
        poll_path,
        blocks.get("ENQUETE", "").strip() + "\n",
        overwrite=True,
        dry_run=False,
    )
    write_required(
        cover_text_path,
        blocks.get("TEXTO_CAPA", "").strip() + "\n",
        overwrite=True,
        dry_run=False,
    )


def generate_cover_prompt(
    episode: Episode,
    cut: Cut,
    output_dir: Path,
    total_cuts: int,
    overwrite: bool,
    dry_run: bool,
    args: argparse.Namespace,
) -> None:
    destination = cover_prompt_output_path(output_dir, cut.number)
    if destination.exists() and not overwrite:
        print(f"skip codex capa: {destination}")
        return

    transcript_path = transcript_output_path(output_dir, cut.number)
    caption_path = caption_output_path(output_dir, cut.number)
    cover_text_path = cover_text_output_path(output_dir, cut.number)
    if not transcript_path.exists():
        raise RuntimeError(f"Transcricao do corte nao encontrada: {transcript_path}")
    if not caption_path.exists() and not dry_run:
        raise RuntimeError(f"Legenda do corte nao encontrada: {caption_path}")

    template = read_text(TEMPLATES_DIR / "prompt-capa.md")
    caption_text = read_text(caption_path).strip() if caption_path.exists() else "(legenda gerada na etapa anterior)"
    cover_text = read_text(cover_text_path).strip() if cover_text_path.exists() else "(texto de capa gerado na etapa anterior)"
    prompt = render_template(
        template,
        cut_values(
            episode,
            cut,
            total_cuts,
            read_text(transcript_path),
            {
                "legenda": caption_text,
                "texto_capa_sugerido": cover_text,
            },
        ),
    )

    response = run_codex(prompt, output_dir, f"codex_capa_{cut.number:02d}", args)
    if dry_run:
        return

    write_required(destination, response.strip() + "\n", overwrite=True, dry_run=False)


def run(args: argparse.Namespace) -> int:
    episode_file = resolve_episode_file(args.episode)
    if not episode_file.exists():
        print(f"ERRO: arquivo do episodio nao encontrado: {episode_file}")
        return 1

    episode = parse_episode(episode_file)
    external_root = Path(args.external_root)
    output_dir = external_episode_dir(episode, external_root)

    print(f"Episodio: {episode.title} - {episode.episode_normalized}")
    print(f"Arquivo: {episode_file}")
    print(f"Pasta externa: {output_dir}")
    print(f"Cortes no TXT: {len(episode.cuts)}")

    if not output_dir.exists():
        print(f"ERRO: pasta externa nao encontrada: {output_dir}")
        return 1

    cut_numbers = {cut.number for cut in episode.cuts}
    video_numbers = list_numbered_videos(output_dir)
    missing_videos = sorted(cut_numbers - video_numbers)
    extra_videos = sorted(video_numbers - cut_numbers)

    for number in missing_videos:
        print(f"AVISO: video esperado nao encontrado: {cut_video_path(output_dir, number)}")
    for number in extra_videos:
        print(f"AVISO: video extra sem corte no TXT: {cut_video_path(output_dir, number)}")

    selected_cuts = [
        cut for cut in episode.cuts if not args.only_cut or cut.number in set(args.only_cut)
    ]
    if not selected_cuts:
        print("ERRO: nenhum corte selecionado.")
        return 1

    for cut in selected_cuts:
        extracted = extract_cut_transcript(episode, cut)
        if not extracted:
            print(f"AVISO: Corte {cut.number} nao extraiu nenhuma linha.")
            continue

        video = cut_video_path(output_dir, cut.number)
        if video.exists():
            dimensions = ffprobe_dimensions(video)
            if dimensions and dimensions != (EXPECTED_WIDTH, EXPECTED_HEIGHT):
                width, height = dimensions
                print(
                    "AVISO: "
                    f"{video.name} esta em {width}x{height}, esperado "
                    f"{EXPECTED_WIDTH}x{EXPECTED_HEIGHT}."
                )

        destination = transcript_output_path(output_dir, cut.number)
        status = write_file(
            destination,
            format_cut_transcript(extracted),
            overwrite=args.overwrite,
            dry_run=args.dry_run,
        )
        print(f"{status}: {destination}")

    schedule_path = output_dir / "agendamento.csv"
    start_date = date.fromisoformat(args.start_date) if args.start_date else date.today()
    schedule_status = write_schedule(
        schedule_path,
        episode,
        output_dir,
        start_date,
        overwrite=args.overwrite,
        dry_run=args.dry_run,
    )
    print(f"{schedule_status}: {schedule_path}")

    run_legends = not args.skip_legends
    run_cover_prompts = not args.skip_cover_prompts

    try:
        if run_legends:
            for cut in selected_cuts:
                print(f"Codex legenda: corte {cut.number}")
                generate_legend_package(
                    episode,
                    cut,
                    output_dir,
                    len(episode.cuts),
                    overwrite=args.overwrite,
                    dry_run=args.dry_run,
                    args=args,
                )

        if run_cover_prompts:
            for cut in selected_cuts:
                print(f"Codex capa: corte {cut.number}")
                generate_cover_prompt(
                    episode,
                    cut,
                    output_dir,
                    len(episode.cuts),
                    overwrite=args.overwrite,
                    dry_run=args.dry_run,
                    args=args,
                )
    except RuntimeError as error:
        print(f"ERRO: {error}")
        return 1

    try:
        run_drive_upload_step(output_dir, selected_cuts, args)
        run_meta_publish_step(output_dir, selected_cuts, args)
    except RuntimeError as error:
        print(f"ERRO: {error}")
        return 1

    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Pipeline do Alem da Emocao: extrai cortes, gera legendas e prompts de capa."
    )
    parser.add_argument(
        "episode",
        help="Episodio normalizado, exemplo EP02, ou caminho para um arquivo TXT.",
    )
    parser.add_argument(
        "--external-root",
        default=str(DEFAULT_EXTERNAL_ROOT),
        help="Pasta raiz externa dos videos.",
    )
    parser.add_argument(
        "--start-date",
        help="Data do primeiro post no formato YYYY-MM-DD. Padrao: hoje.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Sobrescreve arquivos ja existentes.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Mostra o que seria feito sem escrever arquivos.",
    )
    parser.add_argument(
        "--only-cut",
        type=int,
        action="append",
        help="Processa apenas um corte especifico. Opcional para testes. Pode repetir.",
    )
    parser.add_argument(
        "--skip-legends",
        action="store_true",
        help="Nao chama Codex CLI para gerar legendas e comentarios.",
    )
    parser.add_argument(
        "--skip-cover-prompts",
        action="store_true",
        help="Nao chama Codex CLI para gerar prompts de capa.",
    )
    parser.add_argument(
        "--codex-model",
        help="Modelo opcional para passar ao Codex CLI.",
    )
    parser.add_argument(
        "--upload-drive",
        action="store_true",
        help="Forca upload para Google Drive. Por padrao, roda automaticamente se houver credencial.",
    )
    parser.add_argument(
        "--skip-drive-upload",
        action="store_true",
        help="Nao tenta subir videos/capas para o Google Drive.",
    )
    parser.add_argument(
        "--google-credentials",
        default=str(DEFAULT_GOOGLE_CREDENTIALS),
        help="Arquivo OAuth client do Google Drive.",
    )
    parser.add_argument(
        "--google-token",
        help="Arquivo local do token OAuth do Google Drive.",
    )
    parser.add_argument(
        "--drive-folder-id",
        help="ID de uma pasta existente no Google Drive.",
    )
    parser.add_argument(
        "--drive-folder-name",
        help="Nome da pasta a criar/usar no Google Drive.",
    )
    parser.add_argument(
        "--drive-parent-folder-id",
        help="ID da pasta mae no Google Drive.",
    )
    parser.add_argument(
        "--publish-meta",
        action="store_true",
        help="Publica no Instagram ao final usando meta_publish.py.",
    )
    parser.add_argument(
        "--meta-dry-run",
        action="store_true",
        help="Monta payloads da Meta sem publicar, mesmo quando o pipeline nao estiver em --dry-run.",
    )
    parser.add_argument(
        "--meta-env-file",
        help="Arquivo .env.meta com credenciais da Meta.",
    )
    parser.add_argument(
        "--asset-urls",
        help="Mapa JSON de URLs publicas. Padrao: drive_urls.json na pasta do episodio.",
    )
    parser.add_argument(
        "--meta-out",
        help="Arquivo JSONL para salvar resultados da publicacao Meta.",
    )
    return parser


if __name__ == "__main__":
    raise SystemExit(run(build_parser().parse_args()))
