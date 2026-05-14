# tests/test_pipeline.py
# Unit tests for ASR and Transliteration pipelines

import os
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.buffer_manager import BufferManager
from app.transliteration import TransliterationPipeline
from app.utils import (
    get_timestamp,
    validate_audio_file,
    format_output,
    ensure_dirs,
    split_audio,
    cleanup_chunks,
)


class TestBufferManager(unittest.TestCase):
    """Tests for the queue-based buffer system"""

    def setUp(self):
        self.buffer = BufferManager(max_queue_size=5)

    def test_add_chunk(self):
        result = self.buffer.add_chunk("chunk_1")
        self.assertTrue(result)
        self.assertEqual(self.buffer.size(), 1)

    def test_get_chunk(self):
        self.buffer.add_chunk("chunk_1")
        chunk = self.buffer.get_chunk(timeout=1.0)
        self.assertEqual(chunk, "chunk_1")

    def test_queue_full(self):
        for i in range(5):
            self.buffer.add_chunk(f"chunk_{i}")
        # 6th chunk should fail — queue is full
        result = self.buffer.add_chunk("chunk_overflow")
        self.assertFalse(result)

    def test_queue_empty(self):
        self.assertTrue(self.buffer.is_empty())

    def test_clear(self):
        self.buffer.add_chunk("chunk_1")
        self.buffer.add_chunk("chunk_2")
        self.buffer.clear()
        self.assertTrue(self.buffer.is_empty())

    def test_process_all(self):
        self.buffer.add_chunk("hello")
        self.buffer.add_chunk("world")
        results = self.buffer.process_all(lambda x: x.upper())
        self.assertEqual(results, ["HELLO", "WORLD"])


class TestTransliterationPipeline(unittest.TestCase):
    """Tests for the transliteration pipeline"""

    def setUp(self):
        self.pipeline = TransliterationPipeline()

    def test_transliterate_basic(self):
        result = self.pipeline.transliterate("தமிழ்")
        self.assertIsInstance(result, str)
        self.assertGreater(len(result), 0)

    def test_transliterate_empty(self):
        result = self.pipeline.transliterate("")
        self.assertEqual(result, "")

    def test_transliterate_sentence(self):
        result = self.pipeline.transliterate("நான் சாப்பிட்டேன்")
        self.assertIsInstance(result, str)
        self.assertGreater(len(result), 0)
        # Result should be ASCII (romanized)
        self.assertTrue(result.isascii())

    def test_scheme_info(self):
        info = self.pipeline.get_scheme_info()
        self.assertIn("source_script", info)
        self.assertIn("target_scheme", info)
        self.assertIn("example_input", info)
        self.assertIn("example_output", info)


class TestUtils(unittest.TestCase):
    """Tests for utility functions"""

    def test_get_timestamp(self):
        ts = get_timestamp()
        self.assertIsInstance(ts, str)
        self.assertEqual(len(ts), 15)  # YYYYmmdd_HHMMSS

    def test_validate_audio_file_missing(self):
        result = validate_audio_file("nonexistent.wav")
        self.assertFalse(result)

    def test_validate_audio_file_valid(self):
        # Use the sample wav we generated
        sample = "sample_inputs/sample.wav"
        if os.path.exists(sample):
            result = validate_audio_file(sample)
            self.assertTrue(result)

    def test_format_output(self):
        output = format_output("நான்", "naan")
        self.assertIn("transcript", output)
        self.assertIn("transliteration", output)
        self.assertIn("timestamp", output)
        self.assertEqual(output["transcript"], "நான்")
        self.assertEqual(output["transliteration"], "naan")

    def test_ensure_dirs(self):
        ensure_dirs()
        self.assertTrue(os.path.exists("outputs/transcripts"))
        self.assertTrue(os.path.exists("outputs/transliterations"))


class TestAudioSplitting(unittest.TestCase):
    """Tests for the audio chunking / cleanup utilities."""

    def test_split_audio_short_file_returns_single_chunk(self):
        """Audio shorter than chunk_seconds should pass through unchanged."""
        sample = "sample_inputs/sample.wav"
        if not os.path.exists(sample):
            self.skipTest("sample_inputs/sample.wav not available")
        chunks = split_audio(sample, chunk_seconds=30)
        self.assertEqual(
            len(chunks), 1,
            "A short file should produce exactly one chunk"
        )
        self.assertEqual(
            chunks[0], sample,
            "Short audio should return the original path (no temp files)"
        )

    def test_split_audio_long_file_returns_multiple_chunks(self):
        """A synthesized 65s tone should split into three ≤30s chunks."""
        from pydub.generators import Sine

        tone = Sine(440).to_audio_segment(duration=65_000)
        tmp_in = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
        tmp_in.close()
        try:
            tone.export(tmp_in.name, format="wav")
            chunks = split_audio(tmp_in.name, chunk_seconds=30)
            try:
                self.assertEqual(
                    len(chunks), 3,
                    "65s @ 30s/chunk should yield 3 chunks"
                )
                for c in chunks:
                    self.assertTrue(
                        os.path.exists(c),
                        f"Chunk file should exist on disk: {c}"
                    )
                    self.assertIn(
                        "asr_chunks_", c,
                        "Chunks should live under an asr_chunks_* temp dir"
                    )
            finally:
                removed = cleanup_chunks(chunks)
                self.assertEqual(
                    removed, 3,
                    "cleanup_chunks should delete every temp chunk file"
                )
                for c in chunks:
                    self.assertFalse(
                        os.path.exists(c),
                        f"Chunk should be deleted after cleanup: {c}"
                    )
        finally:
            if os.path.exists(tmp_in.name):
                os.unlink(tmp_in.name)

    def test_cleanup_chunks_handles_empty_list(self):
        self.assertEqual(cleanup_chunks([]), 0)

    def test_cleanup_chunks_refuses_non_temp_files(self):
        """cleanup_chunks must NOT delete files outside asr_chunks_* dirs."""
        sample = "sample_inputs/sample.wav"
        if not os.path.exists(sample):
            self.skipTest("sample_inputs/sample.wav not available")
        removed = cleanup_chunks([sample])
        self.assertEqual(
            removed, 0,
            "cleanup_chunks should refuse paths missing the asr_chunks_ marker"
        )
        self.assertTrue(
            os.path.exists(sample),
            "Real input file must not be deleted by cleanup_chunks"
        )


class TestChunkBatching(unittest.TestCase):
    """
    Verify that when the chunk count exceeds the buffer's maxsize, every
    chunk is still transcribed via bounded batching (none are silently
    dropped). This regression-guards the bounded-batch loop in
    ASRPipeline.transcribe_with_buffer().
    """

    def test_batching_processes_all_chunks_when_count_exceeds_maxsize(self):
        """With a 3-slot queue and 7 chunks, all 7 must be transcribed."""
        from app.asr_pipeline import ASRPipeline

        with tempfile.TemporaryDirectory(prefix="asr_chunks_test_") as d:
            chunk_paths = []
            for i in range(7):
                path = os.path.join(d, f"chunk_{i:03d}.wav")
                with open(path, "wb") as f:
                    f.write(b"fake")
                chunk_paths.append(path)

            pipeline = ASRPipeline()
            pipeline.buffer = BufferManager(max_queue_size=3)
            pipeline.model = "stub"  # bypass lazy model loading

            calls = []

            def fake_transcribe(p: str) -> str:
                calls.append(p)
                return f"T({os.path.basename(p)})"

            pipeline.transcribe = fake_transcribe  # type: ignore[assignment]

            with patch("app.asr_pipeline.split_audio", return_value=chunk_paths), \
                 patch("app.asr_pipeline.validate_audio_file", return_value=True), \
                 patch("app.asr_pipeline.cleanup_chunks", return_value=0):
                result = pipeline.transcribe_with_buffer("/fake/audio.wav")

            self.assertEqual(
                len(calls), 7,
                "Every one of 7 chunks must be transcribed even with a "
                "3-slot queue (no silent truncation)"
            )
            for i in range(7):
                self.assertIn(
                    f"chunk_{i:03d}.wav", result,
                    f"Chunk {i} missing from joined transcript"
                )


if __name__ == "__main__":
    unittest.main(verbosity=2)