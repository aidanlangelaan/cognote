import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

import click

from cognote import config, writer
from cognote.recorder import Recorder
from cognote.transcriber import transcribe


class _Group(click.Group):
    """Click Group that routes all error output through stdout.

    Click's default error handler writes to stderr via the Windows console API,
    which raises OSError (Windows error 6) in PowerShell. By catching ClickException
    before Click's own handler runs we can print the message safely via click.echo.
    """

    def main(self, *args, **kwargs) -> None:
        kwargs["standalone_mode"] = False
        try:
            super().main(*args, **kwargs)
        except click.UsageError as e:
            click.echo(f"Error: {e.format_message()}")
            click.echo("Try 'cognote --help' for a list of available commands.")
            sys.exit(2)
        except click.ClickException as e:
            click.echo(f"Error: {e.format_message()}")
            sys.exit(e.exit_code)
        except click.Abort:
            click.echo("Aborted.")
            sys.exit(1)
        except SystemExit:
            raise


@click.group(cls=_Group, invoke_without_command=True)
@click.pass_context
def main(ctx: click.Context) -> None:
    """Cognote – local meeting recorder and transcriber."""
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


@main.command(context_settings={"help_option_names": ["--help"]})
@click.option("--title", default=None, help="Title of the recording session.")
@click.option(
    "--language", default=None,
    help="Language of the recording: nl, en, or auto. Overrides cognote.yaml for this session.",
)
def record(title: str | None, language: str | None) -> None:
    """Start a new recording session. Press Ctrl+C to stop and generate the transcript."""
    if not title:
        click.echo("Error: --title is required.")
        click.echo("Usage:  cognote record --title \"Meeting name\"")
        sys.exit(1)

    cfg = config.load()
    created = config.ensure_exists()
    if created:
        click.echo("No cognote.yaml found — created one with defaults in the current directory.")

    language_mode = language if language is not None else cfg["transcript_language_mode"]

    start = datetime.now()

    try:
        session_path = writer.build_session_path(
            cfg["output_root"],
            start,
            title,
            cfg["session_slug_max_length"],
        )
    except FileExistsError:
        click.echo("Error: a session folder for this title and time already exists.")
        sys.exit(1)

    audio_path = session_path / "audio.wav"

    recorder = Recorder(audio_path)
    recorder.start()

    click.echo(f"Recording: {title}")
    click.echo(f"Output folder: {session_path}")
    click.echo("Press Ctrl+C to stop and generate the transcript.")

    try:
        while True:
            time.sleep(0.5)
    except KeyboardInterrupt:
        pass

    click.echo("\nStopping recording...")
    recorder.stop()

    end = datetime.now()

    click.echo("Transcribing... (this may take a moment on first run)")
    click.echo("Please wait — do not press Ctrl+C again or the transcript will be lost.")

    try:
        segments, detected_language = transcribe(
            audio_path,
            language_mode,
            model_size=cfg["model_size"],
            device=cfg["device"],
            compute_type=cfg["compute_type"],
        )

        transcript_path = writer.write_transcript(
            session_path=session_path,
            title=title,
            start=start,
            end=end,
            language=detected_language,
            segments=segments,
            include_timestamps=cfg["include_timestamps"],
        )

        metadata_path = writer.write_metadata(
            session_path=session_path,
            title=title,
            start=start,
            end=end,
            language=detected_language,
        )
    except KeyboardInterrupt:
        click.echo("\nTranscription interrupted. The audio file was saved but no transcript was generated.")
        click.echo(f"Audio file: {audio_path}")
        sys.exit(1)

    click.echo(f"\nDone. Session saved to: {session_path}")
    click.echo(f"  {audio_path.name}")
    click.echo(f"  {transcript_path.name}")
    click.echo(f"  {metadata_path.name}")


@main.command(name="transcribe", context_settings={"help_option_names": ["--help"]})
@click.argument("audio_file", type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.option("--title", default=None, help="Title for the transcript. Defaults to the audio filename.")
@click.option(
    "--language", default=None,
    help="Language of the recording: nl, en, or auto. Overrides cognote.yaml for this session.",
)
def transcribe_cmd(audio_file: Path, title: str | None, language: str | None) -> None:
    """Transcribe an existing audio file and write transcript.md and metadata.yaml alongside it."""
    cfg = config.load()
    config.ensure_exists()

    language_mode = language if language is not None else cfg["transcript_language_mode"]
    session_path = audio_file.parent
    resolved_title = title if title else audio_file.stem

    # Derive start time from the file's modification time; end from last segment.
    start = datetime.fromtimestamp(audio_file.stat().st_mtime)

    click.echo(f"Transcribing: {audio_file}")
    click.echo("Please wait — do not press Ctrl+C or the transcript will be lost.")

    try:
        segments, detected_language = transcribe(
            audio_file,
            language_mode,
            model_size=cfg["model_size"],
            device=cfg["device"],
            compute_type=cfg["compute_type"],
        )

        if segments:
            end = start + timedelta(seconds=segments[-1].end)
        else:
            end = start

        transcript_path = writer.write_transcript(
            session_path=session_path,
            title=resolved_title,
            start=start,
            end=end,
            language=detected_language,
            segments=segments,
            include_timestamps=cfg["include_timestamps"],
        )

        metadata_path = writer.write_metadata(
            session_path=session_path,
            title=resolved_title,
            start=start,
            end=end,
            language=detected_language,
            audio_filename=audio_file.name,
        )
    except KeyboardInterrupt:
        click.echo("\nTranscription interrupted. No transcript was generated.")
        sys.exit(1)

    click.echo(f"\nDone. Output written to: {session_path}")
    click.echo(f"  {transcript_path.name}")
    click.echo(f"  {metadata_path.name}")
