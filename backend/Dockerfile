FROM python:3.11-slim

# fasttextのビルドに必要なツールをインストール
RUN apt-get update && apt-get install -y --no-install-recommends\
    build-essential \
    g++ \
    libpq-dev \
    python3-dev \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 必要なライブラリをインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# アプリソースコピー
COPY . .
