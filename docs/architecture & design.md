# Cognote – MVP design and scope

## Goal

A small, local-first CLI tool that can:

- start a meeting recording
- stop the recording
- convert the recording to text
- store all resulting files in a clear folder structure

Primary outcome: after a session, there is a local folder containing the audio, transcript, and minimal metadata in a format that other agents can read later.

---

## MVP scope

### In scope

- Start a recording from the terminal
- Stop the recording from the terminal
- Convert the recording to text after stopping
- Save the transcript as a Markdown file
- Store all files locally in a logical folder structure:
  - year
  - month
  - day
  - session folder
- Support multiple separate sessions on the same day
- Use English as the leading language for code, CLI commands, file names, folder names, metadata keys, and internal tool behavior
- Use Dutch date-time formatting in stored metadata and visible timestamps where dates/times are shown inside files, unless a file reference includes a filename that itself contains an ISO-style date/time value
- Keep everything fully local and offline-capable
- Ensure the generated files can be read later by external agents such as ChatGPT, Claude, Ollama, or similar tools

### Explicitly out of scope for MVP

- Database
- Indexed search
- Built-in Q&A
- Summaries
- Decision extraction
- Action extraction
- PII masking
- Cloud dependencies

### After MVP

- Automatic transcript summary
- Extract decisions, action items, and follow-up questions
- PII masking

---

## CLI design (MVP only)

Keep it minimal to avoid confusion during implementation.

### Commands

- `cognote record --title "..."` Starts a new recording session. Press Ctrl+C to stop, which automatically generates the transcript and writes all output files.

That is enough for the MVP. `cognote stop` was considered but removed in favour of Ctrl+C: it keeps the workflow to a single terminal and a single command, which is simpler and less error-prone.

### Minimal workflow

1. Run `cognote record --title "Weekly Sync"`
2. Speak during the meeting
3. Press Ctrl+C
4. Cognote stops the recording, transcribes locally, and creates the session folder and output files automatically

---

## Folder structure

```text
Cognote/
  2026/
    03/
      06/
        2026-03-06_09-30_weekly-sync/
          audio.wav
          transcript.md
          metadata.yaml
```

### Rules

- Use one session folder per recording
- Multiple sessions on the same day are supported by using the start time in the folder name
- Keep names predictable and readable
- The root folder and file names stay in English
- Dates and times shown inside file contents use Dutch formatting where relevant
- If a file content references another file whose name contains an ISO-style date/time value, that filename should be preserved as-is

### Session folder naming

Recommended pattern: `YYYY-MM-DD_HH-mm_<slug>`

Example: `2026-03-06_14-05_architecture-review`

---

## Configuration

A small config file is useful even in the MVP, as long as it stays minimal.

Recommended file: `cognote.yaml`

### Why it is worth having in the MVP

- avoids hardcoded output locations
- makes the tool reusable across machines
- keeps CLI commands simple
- leaves room for later local-only extensions without changing the basic workflow

### Recommended MVP settings

```yaml
output_root: "D:/Cognote"
audio_format: "wav"
transcript_language_mode: "auto"
include_timestamps: true
session_slug_max_length: 50
model_size: "base"
device: "cpu"
compute_type: "int8"
```

For a machine with an NVIDIA GPU (recommended for better quality and speed):

```yaml
model_size: "large-v3"
device: "cuda"
compute_type: "float16"
```

### Meaning

- `output_root` Root folder where all session folders are written.

- `audio_format` Output format for the local recording. Keep this limited to one supported format in the MVP if needed.

- `transcript_language_mode` How transcription language should be handled:

  - `auto`
  - `nl`
  - `en`

  `auto` is likely the best default because meetings may be Dutch, English, or mixed.

- `include_timestamps` Controls whether timestamps are included in the transcript. For this use case this should normally remain `true`.

- `session_slug_max_length` Maximum length of the generated session slug derived from the meeting title. Prevents extremely long folder names when titles are long.

- `model_size` Which Whisper model to use for transcription. Larger models are slower to download and use more memory, but produce significantly better results — especially for Dutch.

  | Value | Download size | Quality | Notes |
  |---|---|---|---|
  | `tiny` | ~75 MB | Poor | Not recommended |
  | `base` | ~140 MB | Decent | Default; fine for English, struggles with Dutch |
  | `small` | ~460 MB | Good | Recommended minimum for Dutch |
  | `medium` | ~1.5 GB | Very good | Good balance on modern CPUs |
  | `large-v2` | ~3 GB | Excellent | Previous best model |
  | `large-v3` | ~3 GB | Excellent | Current best model; recommended with GPU |

  Models are downloaded once on first use and cached in `~/.cache/huggingface/hub/`.

- `device` Where to run the transcription model.

  | Value | When to use |
  |---|---|
  | `cpu` | Default; works on all machines including macOS |
  | `cuda` | NVIDIA GPU only; requires `pip install -e ".[cuda]"` |

- `compute_type` Numerical precision used during transcription. Affects speed and VRAM usage.

  | Value | Device | Notes |
  |---|---|---|
  | `int8` | cpu, cuda | Default; lowest memory use, slightly lower quality |
  | `float16` | cuda only | Best quality on GPU; recommended with `device: cuda` |
  | `int8_float16` | cuda only | Quantized GPU mode; good quality with less VRAM than `float16` |

### Explicitly not needed yet

Do not over-design the config for the MVP. These can wait until later:

- microphone selection
- speaker diarization options
- summary options
- PII masking rules
- profile support

## Stored files

For the MVP, keep only the files that are truly needed.

### 1) Audio file

`audio.wav`

- Original local recording
- Kept as the source of truth

### 2) Transcript file

`transcript.md`

- Human-readable Markdown transcript
- This is the main file that agents can use later

Recommended structure:

```md
# Session Transcript

- Title: Architecture Review
- Date: 06-03-2026
- Start time: 14:05
- End time: 14:52
- Language: nl | en | mixed

## Transcript

[14:05:12] Speaker 1: ...
[14:05:28] Speaker 2: ...
```

### 3) Metadata file

`metadata.yaml`

- Minimal metadata only
- Used so tools and agents do not need to infer basic session properties from the transcript

Recommended fields:

```yaml
title: "Architecture Review"
date: "06-03-2026"
start_time: "14:05"
end_time: "14:52"
language: "nl | en | mixed"
session_folder: "2026-03-06_14-05_architecture-review"
audio_file: "audio.wav"
transcript_file: "transcript.md"
```

---

## Language handling

The tool itself is English-led in its implementation and structure:

- code uses English naming
- CLI commands use English naming
- file names use English naming
- metadata keys use English naming

The meeting content itself can be:

- Dutch
- English
- mixed language

That means the transcript must preserve the spoken language as-is. The tool should not assume English-only meeting content.

## Agent usage

The MVP does not answer questions itself. It prepares local files that other agents can read.

Requirements for agent-friendly output:

- predictable folder structure
- predictable file names
- Markdown transcript as the main readable source
- minimal YAML metadata for context
- timestamps in the transcript so answers can later be traced back

If an agent can read files from disk, it should be able to work with the generated session folder.

---

## Local-first and offline

This is a hard MVP rule.

### Requirements

- Recording must work locally
- Transcription must work locally
- File generation must work locally
- The tool must function without internet access

### Consequence

Choose only components that can run on the machine itself. No required cloud API calls.

---

## Design principles

- Keep it simple
- Prefer fewer commands over a flexible but confusing CLI
- Prefer plain files over infrastructure
- Prefer readable output over smart output
- Make the generated files easy for both humans and agents to inspect

---

## Non-MVP items intentionally removed

The following ideas are valid, but removed from the MVP document to keep the build focused:

- search index
- sqlite
- vector store
- built-in ask command
- summaries
- action extraction
- decision extraction
- PII masking
- cloud fallback

---

## Configuration rules

- If `cognote.yaml` exists, use it
- If it does not exist, fall back to sensible defaults
- The CLI should stay usable without requiring manual config first
- Config should remain local and file-based

## Minimal architecture

For the MVP, the flow is only this:

1. Start recording
2. Stop recording
3. Save audio locally
4. Transcribe locally
5. Write transcript Markdown
6. Write minimal metadata

Nothing more is required for version 1.

---

## MVP quality rules

- Every recording creates exactly one session folder
- No existing session data is overwritten silently
- Transcript output must be readable as plain Markdown
- Transcript should contain timestamps
- The tool must support multiple sessions on the same day
- The tool must work fully offline

---

## Privacy

For the MVP, privacy is handled by locality:

- files remain on the local machine
- no mandatory external services
- no cloud dependency

PII masking is explicitly postponed until after the MVP.

---

## Implementation choices

These decisions were made in consultation with the Product Owner.

### Language and runtime

Python 3.10+. Chosen for ecosystem fit (audio libraries, Whisper integration) and maintainability.

### CLI framework

`click` — cleaner than argparse for commands with named options.

### Audio recording

`sounddevice` + `soundfile` — cross-platform, captures from the default system microphone, no system-level install required beyond pip packages.

### Transcription engine

`faster-whisper` — a local reimplementation of OpenAI Whisper using CTranslate2. Faster than the original, same accuracy, supports Dutch/English/auto language detection, fully offline after model download.

**One-time internet requirement:** On the first transcription, `faster-whisper` downloads the Whisper model (~140 MB for the `base` model) from Hugging Face and caches it locally (`~/.cache/huggingface/hub/`). No account or token is required. All subsequent use is fully offline. This is an accepted deviation from the strict offline rule — it is a one-time setup cost, not an ongoing dependency.

### Speaker diarization

**Not included in MVP.**

The leading diarization library (`pyannote.audio`) requires a Hugging Face account token to download models, which conflicts with the local-first, no-cloud-dependency constraint and adds significant setup complexity. The transcript will contain no speaker labels.

### Session state

All session state lives within the single `cognote record` process. Ctrl+C triggers a clean shutdown: the recorder stops, audio is fully written, transcription runs, and output files are saved — all in the same process. No cross-process IPC or lockfiles are needed.

### Configuration file location

`cognote.yaml` is read from the current working directory when the command is run. If it does not exist on the first run of `cognote record`, it is generated automatically with sensible defaults.

### Installation

Packaged via `pyproject.toml` with a `cognote` entry point. During development, install locally with `pip install -e .`.

### Distribution

Distributed via **GitHub Releases** as pre-built standalone executables. No PyPI until the tool has been validated in real use.

**Per release:**
- Windows: `cognote.exe`
- macOS: `cognote-macos`
- Linux: `cognote-linux`

Built with **PyInstaller** via a **GitHub Actions** workflow triggered on version tag push (e.g. `v1.0.0`). Each platform is built in a matrix job and the executables are attached to the GitHub Release automatically.

**macOS note:** The binary will be unsigned (no Apple Developer account). Users must right-click > Open the first time to bypass Gatekeeper. This is a known and acceptable limitation.

---

## MVP definitions

### Done means

After stopping a recording, Cognote produces a folder like this:

```text
Cognote/
  2026/
    03/
      06/
        2026-03-06_14-05_architecture-review/
          audio.wav
          transcript.md
          metadata.yaml
```

And:

- the transcript is generated locally
- the transcript is stored as Markdown
- the output can be read later by other agents
- the tool supports multiple sessions per day
- the tool works without internet

---

## Post-MVP ideas

Once the MVP works, the next logical steps are:

1. Generate a structured summary from the transcript
2. Extract decisions, action items, and open questions
3. Add PII masking

