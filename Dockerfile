FROM python:3.11-slim

RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser

WORKDIR /app

RUN apt-get update && \
    apt-get --no-install-recommends install -y git && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src

COPY sa-recommender-system.json ./sa-recommender-system.json

RUN chown -R appuser:appgroup /app  # Change ownership of the app directory to the non-root user

USER appuser  # Set the non-root user for running the application

EXPOSE 9092

ENV GOOGLE_APPLICATION_CREDENTIALS="sa-recommender-system.json"

CMD ["python", "src/main.py"]