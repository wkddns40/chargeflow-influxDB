FROM python:3.12-slim

WORKDIR /app
COPY backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY grafana_proxy ./grafana_proxy

EXPOSE 8080
CMD ["uvicorn", "grafana_proxy.app:app", "--host", "0.0.0.0", "--port", "8080"]
