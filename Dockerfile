FROM python:3.11-slim

# Install system tools required for audio processing and downloading
RUN apt-get update && apt-get install -y ffmpeg curl unzip && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all application files (including src/, scripts/, and start.sh)
COPY . .

# Make the startup script executable
RUN chmod +x start.sh

EXPOSE 8000

# Run the startup script (which downloads models, then starts Uvicorn)
CMD ["./start.sh"]