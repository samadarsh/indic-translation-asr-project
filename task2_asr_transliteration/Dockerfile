FROM python:3.10-slim

WORKDIR /app

# Install system dependencies (ffmpeg is usually required for audio processing with Whisper)
RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copy everything from current folder into /app
COPY . .

# Expose Gradio port
EXPOSE 7860

# Run the app
CMD ["python", "app/main.py"]
