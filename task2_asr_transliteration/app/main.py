# app/main.py
# Entry point — starts the ASR + Transliteration Gradio app

import os
import sys
import logging

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.interface import build_interface
from app.utils import ensure_dirs
from models.model_config import APP_CONFIG

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)


def main():
    logger.info("=" * 50)
    logger.info("  Tamil ASR + Transliteration System")
    logger.info("  Model  : openai/whisper-medium")
    logger.info("  Script : Tamil → Harvard-Kyoto Romanization")
    logger.info("=" * 50)

    # Ensure output directories exist
    ensure_dirs()

    # Build Gradio interface
    logger.info("Building Gradio interface...")
    demo = build_interface()

    # Launch app
    logger.info(
        f"Launching app on "
        f"http://{APP_CONFIG['host']}:{APP_CONFIG['port']}"
    )

    demo.launch(
        server_name=APP_CONFIG["host"],
        server_port=APP_CONFIG["port"],
        share=APP_CONFIG["share"],
    )


if __name__ == "__main__":
    main()