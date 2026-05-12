# app/transliteration.py
# Indic transliteration pipeline — Tamil script to Romanized text

import os
import sys
import logging

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from indic_transliteration import sanscript
from indic_transliteration.sanscript import transliterate

from models.model_config import TRANSLITERATION_CONFIG
from app.utils import save_transliteration

logger = logging.getLogger(__name__)


class TransliterationPipeline:
    """
    Transliteration pipeline using the indic-transliteration library.
    Converts Tamil script → Romanized text (Harvard-Kyoto scheme).

    Note: This is transliteration (script conversion), NOT translation.
    The meaning stays the same — only the writing system changes.

    Example:
        Input  : நான் சாப்பிட்டேன்
        Output : naan saappittaen
    """

    def __init__(self):
        self.src_script = TRANSLITERATION_CONFIG["src_script"]
        self.tgt_script = TRANSLITERATION_CONFIG["tgt_script"]
        logger.info(
            f"TransliterationPipeline initialized — "
            f"{self.src_script} → {self.tgt_script}"
        )

    def transliterate(self, text: str) -> str:
        """
        Transliterate Tamil script text to Romanized form.
        Returns romanized string.
        """
        if not text or not text.strip():
            logger.warning("Empty text received for transliteration")
            return ""

        logger.info(f"Transliterating: {text[:60]}...")

        try:
            result = transliterate(
                text,
                sanscript.TAMIL,
                sanscript.HK        # Harvard-Kyoto romanization
            )
            logger.info(f"Transliteration result: {result[:60]}...")
            return result.strip()

        except Exception as e:
            logger.error(f"Transliteration failed: {e}")
            return text             # return original if transliteration fails

    def transliterate_and_save(self, text: str) -> tuple:
        """
        Transliterate text and save to outputs/transliterations/.
        Returns (transliterated_text, saved_filepath).
        """
        transliterated = self.transliterate(text)
        saved_path = save_transliteration(transliterated)
        return transliterated, saved_path

    def get_scheme_info(self) -> dict:
        """
        Return info about the transliteration scheme being used.
        Useful for displaying in the UI.
        """
        return {
            "source_script": "Tamil (Unicode)",
            "target_scheme": "Harvard-Kyoto (HK) Romanization",
            "library":       "indic-transliteration",
            "example_input": "நான் சாப்பிட்டேன்",
            "example_output": "naan saappittaen",
        }