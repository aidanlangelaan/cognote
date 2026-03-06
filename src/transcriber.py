import os
import sys
from dataclasses import dataclass
from pathlib import Path

# Suppress huggingface_hub noise: symlinks warning on Windows and
# unauthenticated-request warning (no token needed for public Whisper models).
os.environ.setdefault("HF_HUB_DISABLE_SYMLINKS_WARNING", "1")
os.environ.setdefault("HF_HUB_VERBOSITY", "error")

# On Windows, NVIDIA pip packages install their DLLs under site-packages/nvidia/*/bin/.
# ctranslate2 uses LoadLibrary which respects PATH but not os.add_dll_directory(),
# so prepend all nvidia DLL directories to PATH before importing faster_whisper.
if sys.platform == "win32":
    import site
    _dll_paths = []
    for _site in site.getsitepackages():
        _nvidia = Path(_site) / "nvidia"
        if _nvidia.exists():
            for _dll_dir in _nvidia.glob("*/bin"):
                if _dll_dir.is_dir():
                    _dll_paths.append(str(_dll_dir))
    if _dll_paths:
        os.environ["PATH"] = ";".join(_dll_paths) + ";" + os.environ.get("PATH", "")

from faster_whisper import WhisperModel

@dataclass
class Segment:
    start: float   # seconds from start of recording
    end: float
    text: str


def transcribe(
    audio_path: Path,
    language_mode: str,
    model_size: str = "base",
    device: str = "cpu",
    compute_type: str = "int8",
) -> tuple[list[Segment], str]:
    """Transcribe the audio file and return segments plus detected language.

    Args:
        audio_path:    Path to the WAV file.
        language_mode: "auto", "nl", or "en".
        model_size:    Whisper model size (tiny/base/small/medium/large-v2/large-v3).
        device:        "cpu" or "cuda".
        compute_type:  "int8" (cpu), "float16" or "int8_float16" (cuda).

    Returns:
        Tuple of (segments, detected_language).
        detected_language is the ISO 639-1 code returned by Whisper (e.g. "nl", "en").
    """
    language = None if language_mode == "auto" else language_mode

    model = WhisperModel(model_size, device=device, compute_type=compute_type)
    raw_segments, info = model.transcribe(str(audio_path), language=language)

    segments = [
        Segment(start=s.start, end=s.end, text=s.text.strip())
        for s in raw_segments
    ]

    return segments, info.language
