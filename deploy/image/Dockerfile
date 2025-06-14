# Dockerfile

# Use an official Python runtime as a parent image
FROM python:3.9-slim

ARG BUILD_NUMBER
LABEL build_number=${BUILD_NUMBER}


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

CMD [ "python" ,"manage.py runserver 8000"]

