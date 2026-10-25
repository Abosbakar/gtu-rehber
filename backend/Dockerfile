# GTÜ Rehber arka uç imajı.
# Derleme bağlamı depo köküdür: docker build -f backend/Dockerfile .
# Alpine seçildi: llama-cpp-python'un hazır CPU wheel'leri musl için derlenmiş.
FROM python:3.11-alpine

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/app ./app

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
