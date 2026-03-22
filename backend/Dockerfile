FROM python:3.10-slim

# Install only runtime dependencies (no build tools)
RUN apt-get update && apt-get install -y \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .

RUN pip install --upgrade pip

# Install dlib binary (no compilation)
RUN pip install --no-cache-dir dlib-bin==19.24.2.post1

# Install face-recognition WITHOUT triggering dlib build
RUN pip install --no-cache-dir --no-deps face-recognition==1.3.0

# Install remaining dependencies (including missing ones)
RUN pip install --no-cache-dir \
    face-recognition-models==0.3.0 \
    Pillow \
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
    certifi

COPY . .

EXPOSE 10000

CMD ["python", "main.py"]