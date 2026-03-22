FROM python:3.10-slim

# Install runtime dependencies only (no build tools)
RUN apt-get update && apt-get install -y \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Upgrade pip
RUN pip install --upgrade pip

# Install prebuilt dlib (no compilation)
RUN pip install --no-cache-dir --only-binary=:all: dlib-bin==19.24.2.post1

# Install face-recognition WITHOUT pulling dlib again
RUN pip install --no-cache-dir --no-deps face-recognition==1.3.0

# Install remaining dependencies
RUN pip install --no-cache-dir \
    opencv-python-headless \
    numpy \
    pymongo \
    python-dotenv \
    cloudinary \
    redis \
    requests \
    flask \
    flask-cors \
    waitress \
    certifi \
    Pillow

COPY . .

CMD ["python", "main.py"]