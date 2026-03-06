from datetime import datetime
from pathlib import Path

import yaml

from cognote import utils
from cognote.transcriber import Segment


def build_session_path(output_root: str, start: datetime, title: str, max_slug_length: int) -> Path:
    """Build and create the full session folder path.

    Structure: <output_root>/YYYY/MM/DD/<session_folder_name>/
    """
    folder_name = utils.session_folder_name(start, title, max_slug_length)
    session_path = (
        Path(output_root)
        / start.strftime("%Y")
        / start.strftime("%m")
        / start.strftime("%d")
        / folder_name
    )
    session_path.mkdir(parents=True, exist_ok=False)
    return session_path


def write_transcript(
    session_path: Path,
    title: str,
    start: datetime,
    end: datetime,
    language: str,
    segments: list[Segment],
    include_timestamps: bool,
) -> Path:
    """Write transcript.md and return its path."""
    lines = [
        "# Session Transcript",
        "",
        f"- Title: {title}",
        f"- Date: {utils.format_dutch_date(start)}",
        f"- Start time: {utils.format_dutch_time(start)}",
        f"- End time: {utils.format_dutch_time(end)}",
        f"- Language: {language}",
        "",
        "## Transcript",
        "",
    ]

    for segment in segments:
        if include_timestamps:
            ts = utils.format_timestamp(segment.start)
            lines.append(f"[{ts}] {segment.text}")
        else:
            lines.append(segment.text)

    transcript_path = session_path / "transcript.md"
    transcript_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return transcript_path


def write_metadata(
    session_path: Path,
    title: str,
    start: datetime,
    end: datetime,
    language: str,
    audio_filename: str = "audio.wav",
    transcript_filename: str = "transcript.md",
) -> Path:
    """Write metadata.yaml and return its path."""
    metadata = {
        "title": title,
        "date": utils.format_dutch_date(start),
        "start_time": utils.format_dutch_time(start),
        "end_time": utils.format_dutch_time(end),
        "language": language,
        "session_folder": session_path.name,
        "audio_file": audio_filename,
        "transcript_file": transcript_filename,
    }

    metadata_path = session_path / "metadata.yaml"
    with metadata_path.open("w", encoding="utf-8") as f:
        yaml.dump(metadata, f, default_flow_style=False, allow_unicode=True)

    return metadata_path
