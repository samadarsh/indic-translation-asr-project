# Dockerfile
# ASR + Transliteration System — containerized deployment

FROM python:3.10

# Set working directory
WORKDIR /app

# Install system dependencies
# ffmpeg required for audio processing by whisper
# curl required for docker-compose healthcheck
RUN apt-get update && apt-get install -y \
    ffmpeg \
    git \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better Docker layer caching
# If requirements don't change, this layer is reused
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy entire app
COPY . .

# Create output directories
RUN mkdir -p outputs/transcripts outputs/transliterations

# Expose Gradio port
EXPOSE 7860

# Entry point
CMD ["python", "app/main.py"]