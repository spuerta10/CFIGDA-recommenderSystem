FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && \
    apt-get install -y git && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src

COPY sa-recommender-system.json ./sa-recommender-system.json

EXPOSE 9092

ENV GOOGLE_APPLICATION_CREDENTIALS="sa-recommender-system.json"

CMD ["python", "src/main.py"]