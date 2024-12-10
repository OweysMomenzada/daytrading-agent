FROM python:3.9-slim

ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y \
    bash \
    build-essential \
    libffi-dev \
    libssl-dev \
    wget \
    curl \
    chromium \
    chromium-driver \
    cmake \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir -r requirements.txt
COPY .env /app/.env

CMD ["python", "src/entrypoint.py"]