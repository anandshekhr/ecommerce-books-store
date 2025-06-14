# Dockerfile

# Use an official Python runtime as a parent image
FROM python:3.9-slim

ARG BUILD_NUMBER
LABEL build_number=${BUILD_NUMBER}


# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
# Install system dependencies
# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    build-essential \
    && apt-get clean


# Install pip and setuptools
RUN pip install --upgrade pip setuptools

# Set working directory
WORKDIR /app/bookstore/

# Install dependencies
COPY src/requirements.txt /app/bookstore/
RUN pip install -r requirements.txt

# Copy the rest of the application code
COPY src/ /app/bookstore/


ENV POSTGRES_PASSWORD='Shekhar123#'
ENV POSTGRES_DB='opcua'
ENV POSTGRES_USER='postgres'
ENV POSTGRES_HOST='host.docker.internal'
ENV POSTGRES_PORT='5433'
ENV ENV='dev'
ENV SECRET_KEY = 'dj!tkv8l1o%$jhqg0(*#(n=3ka6n$y@l%=79_o6z5gxoz7+uj^'

COPY deploy/shell/entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

ENTRYPOINT ["/app/entrypoint.sh"]


