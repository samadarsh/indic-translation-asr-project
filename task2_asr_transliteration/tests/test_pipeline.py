# tests/test_pipeline.py
# Unit tests for ASR and Transliteration pipelines

import os
import sys
import unittest

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.buffer_manager import BufferManager
from app.transliteration import TransliterationPipeline
from app.utils import (
    get_timestamp,
    validate_audio_file,
    format_output,
    ensure_dirs,
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


if __name__ == "__main__":
    unittest.main(verbosity=2)