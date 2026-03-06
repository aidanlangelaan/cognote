# Cognote

**Turn meetings into knowledge.**

Cognote is a combination of *cognition* — understanding and processing information — and *note* — capturing knowledge. Together they describe the core idea: turning spoken conversations into structured information that can be revisited, analyzed, and queried later.

The flow is simple:

**Audio → Transcript → Structured files → Later analysis by AI agents**

Meetings are temporary. Cognote makes them persistent.

---

Press `Ctrl+C` to stop — Cognote saves the audio, transcribes it on your machine, and writes a structured session folder you (or an AI agent) can read back later.

No cloud. No accounts. Everything stays on your device.

---

## Requirements

- Python 3.10+
- A working microphone
- (Optional) NVIDIA GPU with CUDA drivers for faster transcription

---

## Installation

```bash
git clone https://github.com/your-username/cognote.git
cd cognote
pip install -e .
```

For GPU acceleration (NVIDIA only):

```bash
pip install -e ".[cuda]"
```

---

## Quick start

```bash
cognote record --title "Team standup"
```

Press `Ctrl+C` to stop recording. Cognote will transcribe the audio and save everything to an output folder.

---

## Configuration

On first run, `cognote.yaml` is created in the directory you ran the command from. Edit it to change defaults:

```yaml
audio_format: wav
compute_type: int8
device: cpu
include_timestamps: true
model_size: base
output_root: /path/to/your/output
session_slug_max_length: 50
transcript_language_mode: auto
```

### Options

| Key | Values | Description |
|-----|--------|-------------|
| `model_size` | `tiny` `base` `small` `medium` `large-v2` `large-v3` | Whisper model. Larger = more accurate, slower, more VRAM. |
| `device` | `cpu` `cuda` | Use `cuda` for GPU acceleration (NVIDIA only). |
| `compute_type` | `int8` (cpu) · `float16` `int8_float16` `int8` (cuda) | Quantization. `float16` gives the best quality on GPU. |
| `transcript_language_mode` | `auto` `nl` `en` | Language hint for Whisper. Explicit language improves accuracy. |
| `include_timestamps` | `true` `false` | Include segment timestamps in the transcript. |
| `output_root` | any path | Root folder for session output. |

You can also override the language for a single session:

```bash
cognote record --title "Vergadering" --language nl
```

### Model recommendations

| Hardware | Recommended settings |
|----------|----------------------|
| Any CPU | `model_size: base`, `device: cpu`, `compute_type: int8` |
| GPU, 4 GB VRAM | `model_size: medium`, `device: cuda`, `compute_type: int8_float16` |
| GPU, 8 GB VRAM | `model_size: large-v3`, `device: cuda`, `compute_type: float16` |

Models are downloaded once from Hugging Face on first use and cached locally. An internet connection is only needed for that initial download.

---

## Output

Each session is saved to:

```
<output_root>/
  YYYY/MM/DD/YYYY-MM-DD_HH-mm_<slug>/
    audio.wav
    transcript.md
    metadata.yaml
```

`transcript.md` contains timestamped segments in the detected language. `metadata.yaml` contains session info (title, start/end time, language).

---

## Commands

```
cognote record --title "..." [--language nl|en|auto]
```

---

## License

This project is licensed under the [Polyform Noncommercial License 1.0.0](https://polyformproject.org/licenses/noncommercial/1.0.0/).
Commercial use is not permitted without explicit permission.

For commercial licensing, please contact: aidan@langelaan.pro
