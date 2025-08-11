# Use Python slim image as base
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies including FFmpeg
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY chroma-vue.py .
COPY README.md .

# Create a directory for input/output files
RUN mkdir -p /videos

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Create a non-root user for security
RUN useradd -m -u 1000 chromauser && \
    chown -R chromauser:chromauser /app /videos
USER chromauser

# Set the default command
ENTRYPOINT ["python", "chroma-vue.py"]
CMD ["--help"]