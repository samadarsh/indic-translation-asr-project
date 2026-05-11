import gradio as gr
from asr_pipeline import process_audio
from transliteration import transliterate_text

def transcribe_and_transliterate(audio_file):
    if audio_file is None:
        return "No audio provided.", ""
    
    # Placeholder logic
    # In reality, you'd push this to the BufferManager, process via Whisper,
    # and then run the transcript through the Indic-Transliteration engine.
    
    # 1. Transcript (Dummy)
    transcript = "This is a placeholder transcript for the uploaded audio."
    
    # 2. Transliteration (Dummy)
    transliteration = "திஸ் இஸ் அ ப்ளேஸ்ஹோல்டர் ட்ரான்ஸ்கிரிப்ட்"
    
    return transcript, transliteration

def create_ui():
    with gr.Blocks(title="Indic ASR & Transliteration") as interface:
        gr.Markdown("# 🎙️ ASR & Transliteration System")
        gr.Markdown("Upload an audio file or record from your microphone to get the English transcript and Tamil transliteration.")
        
        with gr.Row():
            with gr.Column():
                audio_input = gr.Audio(type="filepath", label="Audio Input")
                submit_btn = gr.Button("Transcribe", variant="primary")
                
            with gr.Column():
                transcript_output = gr.Textbox(label="English Transcript", lines=4)
                transliteration_output = gr.Textbox(label="Tamil Transliteration", lines=4)
                
        submit_btn.click(
            fn=transcribe_and_transliterate,
            inputs=audio_input,
            outputs=[transcript_output, transliteration_output]
        )
        
    return interface

if __name__ == "__main__":
    app = create_ui()
    # Gradio needs server_name="0.0.0.0" to be accessible outside the Docker container
    app.launch(server_name="0.0.0.0", server_port=7860)
