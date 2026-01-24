# Use official Python image
FROM python:3.10-slim

# Create non-root user
RUN groupadd -r celery && useradd -r -g celery celery

# Environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies (IMPORTANT for mysqlclient)
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    pkg-config \
    default-libmysqlclient-dev \
    libssl-dev \
    libffi-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip tools
RUN pip install --upgrade pip setuptools wheel

# Set working directory
WORKDIR /app/vams/book-store/

# Install Python dependencies first (better caching)
COPY src/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ .

# Change ownership
RUN chown -R celery:celery /app/vams/book-store

# Switch to non-root user
USER celery
