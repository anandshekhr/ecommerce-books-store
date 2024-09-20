# Dockerfile

# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Create a non-root user
RUN groupadd -r celery && useradd -r -g celery celery

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
# Install system dependencies
RUN apt-get update \
    && apt-get install -y build-essential openssl\
    && apt-get clean

# Install pip and setuptools
RUN pip install --upgrade pip setuptools

# Set working directory
WORKDIR /app/vams/book-store/

# Install dependencies
COPY src/requirements.txt /app/vams/book-store/
RUN pip install -r requirements.txt
RUN pip install --index-url https://phonepe.mycloudrepo.io/public/repositories/phonepe-pg-sdk-python --extra-index-url https://pypi.org/simple phonepe_sdk==1.1.0


# Copy the rest of the application code
COPY src/ /app/vams/book-store/

# Change ownership of the application directory
RUN chown -R celery:celery /app/vams/book-store
# Switch to the non-root user
USER celery
