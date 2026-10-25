# GTÜ Rehber arka uç imajı.
# Derleme bağlamı depo köküdür: docker build -f backend/Dockerfile .
# Alpine seçildi: llama-cpp-python'un hazır CPU wheel'leri musl için derlenmiş.
FROM python:3.11-alpine

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# llama.cpp'nin çalışma zamanı kütüphaneleri
RUN apk add --no-cache libgomp libstdc++

WORKDIR /app

# Model derleme sırasında Hugging Face'ten iner (~1,1 GB). Bu katman önbelleğe alınır.
ARG MODEL_REPO=Qwen/Qwen2.5-1.5B-Instruct-GGUF
ARG MODEL_FILE=qwen2.5-1.5b-instruct-q4_k_m.gguf
COPY backend/scripts/download_model.py /tmp/download_model.py
RUN python /tmp/download_model.py "$MODEL_REPO" "$MODEL_FILE" /models

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY data ./data
COPY backend/app ./app

# Deneyim veritabanı bu klasörde durur; docker compose burayı bir volume'a bağlar
RUN mkdir -p /app/db

ENV MODEL_PATH=/models/${MODEL_FILE} \
    DATA_DIR=/app/data \
    DB_PATH=/app/db/rehber.db

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
