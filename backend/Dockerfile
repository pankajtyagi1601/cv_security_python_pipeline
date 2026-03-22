FROM python:3.10-slim

# Only runtime dependencies (no build tools needed anymore)
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

# Upgrade pip (important for wheel detection)
RUN pip install --upgrade pip

# Install prebuilt dlib (NO compilation)
RUN pip install --no-cache-dir --only-binary=:all: dlib-bin==19.24.2.post1

# Install remaining dependencies
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "main.py"]