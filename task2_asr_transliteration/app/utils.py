# app/utils.py
# Helper functions — file saving, formatting, logging

import os
import datetime
import logging

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