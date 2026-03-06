from pathlib import Path
from typing import Any

import yaml

CONFIG_FILENAME = "cognote.yaml"

DEFAULTS: dict[str, Any] = {
    "output_root": str(Path.cwd() / "Cognote"),
    "audio_format": "wav",
    "transcript_language_mode": "auto",
    "include_timestamps": True,
    "session_slug_max_length": 50,
    # Transcription model settings.
    # model_size: tiny | base | small | medium | large-v2 | large-v3
    # device:     cpu  | cuda
    # compute_type:
    #   cpu  -> int8
    #   cuda -> float16 (best quality) | int8_float16 (less VRAM) | int8
    "model_size": "base",
    "device": "cpu",
    "compute_type": "int8",
}


def load() -> dict[str, Any]:
    """Load config from cognote.yaml in the working directory.

    Returns merged config (file values override defaults).
    Does not auto-generate the file here; that is done by ensure_exists().
    """
    path = Path(CONFIG_FILENAME)
    if not path.exists():
        return dict(DEFAULTS)

    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}

    return {**DEFAULTS, **data}


def ensure_exists() -> bool:
    """Write cognote.yaml with defaults if it does not exist.

    Returns True if the file was created, False if it already existed.
    """
    path = Path(CONFIG_FILENAME)
    if path.exists():
        return False

    with path.open("w", encoding="utf-8") as f:
        yaml.dump(DEFAULTS, f, default_flow_style=False, allow_unicode=True)

    return True
