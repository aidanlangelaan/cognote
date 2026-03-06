import queue
import threading
from pathlib import Path

import sounddevice as sd
import soundfile as sf

SAMPLE_RATE = 16000   # 16 kHz – sufficient for speech, required by Whisper
CHANNELS = 1          # mono


class Recorder:
    """Records audio from the default microphone to a WAV file.

    Usage:
        recorder = Recorder(Path("audio.wav"))
        recorder.start()
        # ... time passes ...
        recorder.stop()
    """

    def __init__(self, output_path: Path) -> None:
        self._output_path = output_path
        self._queue: queue.Queue = queue.Queue()
        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None

    def start(self) -> None:
        """Start recording in a background thread."""
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        """Signal the recording to stop and wait for the file to be written."""
        self._stop_event.set()
        if self._thread:
            self._thread.join()

    def _run(self) -> None:
        with sf.SoundFile(
            self._output_path,
            mode="w",
            samplerate=SAMPLE_RATE,
            channels=CHANNELS,
            format="WAV",
            subtype="PCM_16",
        ) as audio_file:
            with sd.InputStream(
                samplerate=SAMPLE_RATE,
                channels=CHANNELS,
                callback=self._callback,
            ):
                while not self._stop_event.is_set():
                    try:
                        data = self._queue.get(timeout=0.1)
                        audio_file.write(data)
                    except queue.Empty:
                        continue

            # Drain any remaining buffered frames
            while not self._queue.empty():
                audio_file.write(self._queue.get_nowait())

    def _callback(self, indata, frames, time, status) -> None:  # noqa: ARG002
        self._queue.put(indata.copy())
