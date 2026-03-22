FROM python:3.10-slim

# System dependencies required to compile dlib
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    libopenblas-dev \
    liblapack-dev \
    libx11-dev \
    pkg-config \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements first — Docker layer caching means
# requirements only reinstall if this file changes
COPY requirements.txt .

# Install cmake first — dlib needs it
RUN pip install --no-cache-dir cmake

# Install dlib separately with limited CPU parallelism
# DLIB_USE_CUDA=0 — no GPU needed
# --no-cache-dir — saves memory during build
RUN DLIB_USE_CUDA=0 pip install --no-cache-dir dlib==19.24.6

# Install everything else
RUN pip install --no-cache-dir -r requirements.txt

# Copy all backend files
COPY . .

CMD ["python", "main.py"]
