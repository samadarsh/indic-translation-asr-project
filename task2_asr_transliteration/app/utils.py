# app/utils.py
# Helper functions — file saving, formatting, logging, audio chunking

import os
import datetime
import logging
import tempfile

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)


def get_timestamp():
    """Returns current timestamp string for filenames"""
    return datetime.datetime.now().strftime("%Y%m%d_%H%M%S")


def ensure_dirs():
    """Create output directories if they don't exist"""
    dirs = [
        "outputs/transcripts",
        "outputs/transliterations",
    ]
    for d in dirs:
        os.makedirs(d, exist_ok=True)
        logger.info(f"Directory ready: {d}")


def save_transcript(text: str) -> str:
    """
    Save transcript text to outputs/transcripts/
    Returns the saved file path
    """
    ensure_dirs()
    filename = f"outputs/transcripts/transcript_{get_timestamp()}.txt"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(text)
    logger.info(f"Transcript saved: {filename}")
    return filename


def save_transliteration(text: str) -> str:
    """
    Save transliteration text to outputs/transliterations/
    Returns the saved file path
    """
    ensure_dirs()
    filename = f"outputs/transliterations/transliteration_{get_timestamp()}.txt"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(text)
    logger.info(f"Transliteration saved: {filename}")
    return filename


def format_output(transcript: str, transliteration: str) -> dict:
    """
    Format final output as a clean dictionary
    """
    return {
        "transcript":      transcript.strip(),
        "transliteration": transliteration.strip(),
        "timestamp":       get_timestamp(),
    }


def validate_audio_file(filepath: str) -> bool:
    """
    Basic validation — check file exists and has content
    """
    if not os.path.exists(filepath):
        logger.error(f"Audio file not found: {filepath}")
        return False
    if os.path.getsize(filepath) == 0:
        logger.error(f"Audio file is empty: {filepath}")
        return False
    logger.info(f"Audio file validated: {filepath}")
    return True


# ---------------------------------------------------------------------------
# Audio chunking utilities
# ---------------------------------------------------------------------------
# Used by the BufferManager pipeline to split long uploads into fixed-duration
# segments before transcription. Keeps the queue genuinely chunked (instead of
# holding a single full file path) and bounds peak memory on long audio.
#
# Design notes:
#   * For audio shorter than `chunk_seconds`, splitting is a no-op and the
#     original path is returned unchanged — avoids creating temp files when
#     they would be wasteful.
#   * Chunks are written under a uniquely-named temp directory whose name
#     contains the marker "asr_chunks_". cleanup_chunks() refuses to delete
#     anything outside that marker as a safety belt against accidentally
#     deleting user files.

_TEMP_PREFIX = "asr_chunks_"


def split_audio(audio_path: str, chunk_seconds: int = 30,
                sample_rate: int = 16000) -> list:
    """
    Split an audio file into fixed-duration chunks.

    Returns a list of file paths, in chronological order:
      * If the audio is shorter than `chunk_seconds`, returns
        `[audio_path]` unchanged (no temp files created).
      * Otherwise returns paths to N temporary WAV files (mono, 16 kHz)
        each ≤ `chunk_seconds` long.

    Raises FileNotFoundError if the input cannot be validated.
    """
    if not validate_audio_file(audio_path):
        raise FileNotFoundError(f"Cannot split — invalid audio file: {audio_path}")

    from pydub import AudioSegment

    audio = AudioSegment.from_file(audio_path)
    duration_ms = len(audio)
    chunk_ms = max(1, int(chunk_seconds * 1000))

    if duration_ms <= chunk_ms:
        logger.info(
            f"Audio is {duration_ms / 1000:.1f}s ≤ {chunk_seconds}s — "
            f"no split needed (single chunk)"
        )
        return [audio_path]

    audio = audio.set_frame_rate(sample_rate).set_channels(1)

    temp_dir = tempfile.mkdtemp(prefix=_TEMP_PREFIX)
    num_chunks = (duration_ms + chunk_ms - 1) // chunk_ms

    chunk_paths = []
    for i in range(num_chunks):
        start = i * chunk_ms
        end = min(start + chunk_ms, duration_ms)
        chunk = audio[start:end]
        chunk_path = os.path.join(temp_dir, f"chunk_{i:03d}.wav")
        chunk.export(chunk_path, format="wav")
        chunk_paths.append(chunk_path)

    logger.info(
        f"Split {duration_ms / 1000:.1f}s audio into {num_chunks} chunk(s) "
        f"of ≤{chunk_seconds}s each → {temp_dir}"
    )
    return chunk_paths


def cleanup_chunks(chunk_paths: list) -> int:
    """
    Remove temporary chunk files produced by split_audio().

    Only files whose path contains the "asr_chunks_" marker (created by
    split_audio's tempfile.mkdtemp) are eligible for deletion. Real input
    files are left untouched. Empty parent temp dirs are also removed.

    Returns the number of files actually deleted.
    """
    if not chunk_paths:
        return 0

    removed = 0
    parent_dirs = set()

    for path in chunk_paths:
        if not path or _TEMP_PREFIX not in path:
            continue
        if not os.path.exists(path):
            continue
        try:
            os.remove(path)
            removed += 1
            parent_dirs.add(os.path.dirname(path))
        except OSError as e:
            logger.warning(f"Could not remove chunk {path}: {e}")

    for d in parent_dirs:
        try:
            if os.path.isdir(d) and not os.listdir(d):
                os.rmdir(d)
        except OSError:
            pass

    if removed:
        logger.info(f"Cleaned up {removed} temporary chunk file(s)")
    return removed