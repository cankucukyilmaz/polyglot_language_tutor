FROM python:3.11-slim

# Install system tools required for audio processing and downloading
RUN apt-get update && apt-get install -y ffmpeg curl unzip && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy your source code
COPY ./src /app/src

EXPOSE 8000

# Start the web server
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]