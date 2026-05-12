# app/asr_pipeline.py
# Whisper-based ASR pipeline for Tamil audio transcription

import os
import sys
import logging
import torch
import whisper

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.model_config import ASR_CONFIG, BUFFER_CONFIG
from app.buffer_manager import BufferManager
from app.utils import validate_audio_file, save_transcript

logger = logging.getLogger(__name__)


class ASRPipeline:
    """
    Whisper-based ASR pipeline.
    Loads the model once and reuses it for all transcriptions.
    Uses BufferManager for chunked audio processing.
    """

    def __init__(self):
        self.model_id  = ASR_CONFIG["model_id"]
        self.language  = ASR_CONFIG["language"]
        self.task      = ASR_CONFIG["task"]
        self.device    = ASR_CONFIG["device"]
        self.model     = None
        self.buffer    = BufferManager(
            max_queue_size=BUFFER_CONFIG["max_queue_size"]
        )
        logger.info(f"ASRPipeline initialized — model: {self.model_id}")

    def load_model(self):
        """
        Load Whisper model from HuggingFace.
        Called once at startup.
        """
        if self.model is not None:
            logger.info("Model already loaded — skipping")
            return

        logger.info(f"Loading Whisper model: {self.model_id}...")
        
        # whisper-medium → "medium" for openai/whisper library
        model_size = self.model_id.replace("openai/whisper-", "")
        self.model = whisper.load_model(model_size, device=self.device)
        
        logger.info(f"✅ Whisper model loaded on {self.device}")

    def transcribe(self, audio_path: str) -> str:
        """
        Transcribe a single audio file.
        Returns the Tamil transcript as a string.
        """
        if self.model is None:
            self.load_model()

        if not validate_audio_file(audio_path):
            raise FileNotFoundError(f"Invalid audio file: {audio_path}")

        logger.info(f"Transcribing: {audio_path}")

        result = self.model.transcribe(
            audio_path,
            language=self.language,
            task=self.task,
            fp16=False,  # fp16=False for CPU compatibility
        )

        transcript = result["text"].strip()
        logger.info(f"Transcript: {transcript[:80]}...")
        return transcript

    def transcribe_with_buffer(self, audio_path: str) -> str:
        """
        Transcribe using the buffer queue system.
        Adds audio to buffer, processes it, returns transcript.
        """
        if not validate_audio_file(audio_path):
            raise FileNotFoundError(f"Invalid audio file: {audio_path}")

        # Add to buffer queue
        added = self.buffer.add_chunk(audio_path)
        if not added:
            logger.warning("Buffer full — processing directly")
            return self.transcribe(audio_path)

        # Process from buffer
        results = self.buffer.process_all(self.transcribe)

        if not results:
            logger.warning("No results from buffer — transcribing directly")
            return self.transcribe(audio_path)

        # Join all chunk transcripts
        full_transcript = " ".join(results)
        logger.info(f"Buffer transcription complete: {len(results)} chunks")
        return full_transcript

    def transcribe_and_save(self, audio_path: str) -> tuple:
        """
        Transcribe audio and save transcript to outputs/transcripts/.
        Returns (transcript, saved_filepath).
        """
        transcript = self.transcribe_with_buffer(audio_path)
        saved_path = save_transcript(transcript)
        return transcript, saved_path