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
from app.utils import (
    validate_audio_file,
    save_transcript,
    split_audio,
    cleanup_chunks,
)

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
        Transcribe an audio file using a real chunked buffer pipeline with
        bounded batching.

        Flow:
          1. Split the audio into fixed-duration chunks (≤ chunk_duration s).
          2. Process chunks in bounded batches: fill the BufferManager queue
             up to max_queue_size, drain it through Whisper, then load the
             next batch. This bounds peak queue size while guaranteeing every
             chunk is transcribed regardless of total audio length.
          3. Concatenate the per-chunk transcripts into a single string.
          4. Clean up temporary chunk files in a finally block.

        Defensive fallbacks (in order of preference):
          - If splitting fails for any reason, transcribe the original file.
          - If buffer processing yields no results, transcribe the original
            file in one shot.
        """
        if not validate_audio_file(audio_path):
            raise FileNotFoundError(f"Invalid audio file: {audio_path}")

        chunk_seconds = BUFFER_CONFIG.get("chunk_duration", 30)
        sample_rate   = BUFFER_CONFIG.get("sample_rate", 16000)

        try:
            chunk_paths = split_audio(
                audio_path,
                chunk_seconds=chunk_seconds,
                sample_rate=sample_rate,
            )
        except Exception as e:
            logger.warning(
                f"Audio split failed ({e}) — falling back to direct transcription"
            )
            return self.transcribe(audio_path)

        is_temp_split = bool(chunk_paths) and chunk_paths[0] != audio_path
        total_chunks  = len(chunk_paths)
        max_q         = self.buffer.max_queue_size or max(total_chunks, 1)
        num_batches   = (total_chunks + max_q - 1) // max_q  # ceiling div

        if num_batches > 1:
            logger.info(
                f"Audio yielded {total_chunks} chunks; processing in "
                f"{num_batches} batches of up to {max_q}"
            )

        results = []
        try:
            self.buffer.clear()

            i = 0
            batch_idx = 0
            while i < total_chunks:
                batch_idx += 1
                enqueued_in_batch = 0
                while i < total_chunks:
                    if self.buffer.add_chunk(chunk_paths[i]):
                        enqueued_in_batch += 1
                        i += 1
                    else:
                        break  # queue full — drain before continuing

                if enqueued_in_batch == 0:
                    logger.warning(
                        "Could not enqueue any chunks in this batch — "
                        "aborting batch loop"
                    )
                    break

                log_prefix = (
                    f"Batch {batch_idx}/{num_batches}: "
                    if num_batches > 1 else ""
                )
                logger.info(
                    f"{log_prefix}processing {enqueued_in_batch} "
                    f"chunk(s) from buffer..."
                )
                batch_results = self.buffer.process_all(self.transcribe)
                results.extend(batch_results)
        finally:
            if is_temp_split:
                cleanup_chunks(chunk_paths)

        if not results:
            logger.warning("No results from buffer — falling back to direct transcription")
            return self.transcribe(audio_path)

        full_transcript = " ".join(r for r in results if r).strip()
        logger.info(
            f"Buffer transcription complete: {len(results)} chunk(s) joined "
            f"({len(full_transcript)} chars)"
        )
        return full_transcript

    def transcribe_and_save(self, audio_path: str) -> tuple:
        """
        Transcribe audio and save transcript to outputs/transcripts/.
        Returns (transcript, saved_filepath).
        """
        transcript = self.transcribe_with_buffer(audio_path)
        saved_path = save_transcript(transcript)
        return transcript, saved_path