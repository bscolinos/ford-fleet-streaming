FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY telemetry_consumer.py .

CMD ["python", "-u", "telemetry_consumer.py"]

