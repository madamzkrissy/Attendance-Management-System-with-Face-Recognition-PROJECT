FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system packages required to build dlib, OpenCV and other native deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    cmake \
    git \
    wget \
    ffmpeg \
    libgtk-3-dev \
    libboost-all-dev \
    libatlas-base-dev \
    libopenblas-dev \
    liblapack-dev \
    libjpeg-dev \
    libpng-dev \
    libsm6 \
    libxrender1 \
    pkg-config \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python deps. Copy only requirements first to leverage Docker cache.
COPY requirements.txt /app/requirements.txt

RUN pip install --upgrade pip setuptools wheel \
    && pip install --no-cache-dir -r /app/requirements.txt

# Copy project
COPY . /app

ENV PORT=5000

EXPOSE 5000

# Use gunicorn (Procfile and requirements.txt already configured for production)
CMD ["gunicorn", "app:app", "--workers", "3", "--threads", "2", "--bind", "0.0.0.0:5000"]
