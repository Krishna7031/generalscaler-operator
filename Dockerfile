FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade -r requirements.txt
COPY generalscaler/ ./generalscaler/
COPY deploy/ ./deploy
COPY controller.py .
ENV KOPF_LOG_LEVEL=INFO
CMD ["python", "controller.py"]

