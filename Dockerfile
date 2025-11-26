# Use official Python runtime as base image
FROM python:3.11-slim

# Set working directory in container
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Copy operator source code
COPY generalscaler/ ./generalscaler/
COPY deploy/ ./deploy

# Copy entrypoint script or main controller
COPY controller.py .

# Set environment variables to control Kopf logging
ENV KOPF_LOG_LEVEL=INFO

# Run the operator controller when container starts
CMD ["python", "controller.py"]

