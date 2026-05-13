# app/interface.py
# Gradio UI definition for the ASR + Transliteration system

import os
import sys
import logging

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import gradio as gr

from app.asr_pipeline import ASRPipeline
from app.transliteration import TransliterationPipeline
from app.utils import format_output, ensure_dirs
from models.model_config import APP_CONFIG

logger = logging.getLogger(__name__)

# Initialize pipelines once at startup
asr   = ASRPipeline()
trans = TransliterationPipeline()


def process_audio(audio_path: str) -> tuple:
    """
    Main processing function called by Gradio.
    Takes audio file path, returns (transcript, transliteration).
    """
    if audio_path is None:
        return "⚠️ Please upload an audio file.", ""

    try:
        logger.info(f"Processing audio: {audio_path}")

        # Step 1 — Load model if not already loaded
        asr.load_model()

        # Step 2 — Transcribe via buffer pipeline
        transcript, transcript_path = asr.transcribe_and_save(audio_path)

        if not transcript:
            return "⚠️ Could not transcribe audio. Please try again.", ""

        # Step 3 — Transliterate transcript
        transliteration, translit_path = trans.transliterate_and_save(transcript)

        # Step 4 — Format and log output
        output = format_output(transcript, transliteration)
        logger.info(f"Processing complete: {output}")

        return transcript, transliteration

    except FileNotFoundError as e:
        logger.error(f"File error: {e}")
        return f"❌ File error: {str(e)}", ""

    except Exception as e:
        logger.error(f"Processing failed: {e}")
        return f"❌ Error: {str(e)}", ""


def build_interface() -> gr.Blocks:
    ensure_dirs()

    with gr.Blocks(
        title="Tamil ASR + Transliteration System",
        theme=gr.themes.Soft(primary_hue="violet", secondary_hue="purple"),
    ) as demo:

        gr.Markdown(
            """
            # 🎙️ Tamil ASR + Transliteration System
            Upload a Tamil audio file to get the **transcript** and **romanized transliteration**.
            ---
            """
        )

        with gr.Row():
            with gr.Column(scale=2):
                audio_input = gr.Audio(
                    label="📂 Upload Tamil Audio",
                    type="filepath",
                    sources=["upload", "microphone"],
                )

                gr.Examples(
                    examples=[["sample_inputs/sample.wav"]],
                    inputs=audio_input,
                    label="Try with sample audio",
                )

                submit_btn = gr.Button(
                    "🚀 Transcribe & Transliterate",
                    variant="primary",
                    size="lg",
                )

            with gr.Column(scale=3):
                transcript_output = gr.Textbox(
                    label="📝 Tamil Transcript",
                    placeholder="Tamil transcript will appear here...",
                    lines=8,
                    interactive=False,
                )
                transliteration_output = gr.Textbox(
                    label="🔤 Romanized Tamil (ASCII)",
                    placeholder="Romanized text will appear here...",
                    lines=8,
                    interactive=False,
                )

        gr.Markdown("---")

        with gr.Accordion("ℹ️ About Transliteration", open=False):
            gr.Markdown(
                """
                **Transliteration** converts Tamil script to Romanized form.
                It does **not** translate the meaning — only the writing system changes.

                | Input (Tamil Script) | Output (Romanized ASCII) |
                |---|---|
                | நான் சாப்பிட்டேன் | naan saappittaen |
                | தமிழ் மொழி | tamiL moLi |
                | செயற்கை நுண்ணறிவு | seyaRkai nuNNaRivu |
                | நான் ஒரு மென்பொருள் பொறியாளர் | naan oru menporuL poRiyaaLar |

                **Scheme:** Tamil-Aware Latin (ASCII) Romanization — long vowels doubled
                (`aa`, `ii`, `uu`, `oo`), retroflex consonants capitalized
                (`N`, `L`, `R`).
                """
            )

        gr.Markdown(
            """
            ---
            🔗 [GitHub Repository](https://github.com/samadarsh/indic-translation-asr-project)
            &nbsp;·&nbsp; Powered by `openai/whisper-medium` and a custom Tamil-aware grapheme romanizer.
            """
        )

        submit_btn.click(
            fn=process_audio,
            inputs=[audio_input],
            outputs=[transcript_output, transliteration_output],
        )

    return demo