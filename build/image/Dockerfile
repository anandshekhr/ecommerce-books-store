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


ENV POSTGRES_PASSWORD='Shekhar123#'
ENV POSTGRES_DB='vams-opcua-1'
ENV POSTGRES_USER='postgres'
ENV POSTGRES_HOST='host.docker.internal'
ENV POSTGRES_PORT='5432'

# Email related
ENV EMAIL_HOST_USER="vamscentral@hotmail.com"
ENV EMAIL_HOST_PASSWORD="1$Onemanarmy$2023"
ENV SECRET_KEY='0!i02oj+08$brhdkw-v=gr^*)an++d+1nc4uq)&&iw#v2nn@3r'
ENV DEBUG=True
ENV DATABASE_URL='ashekhar-3091.postgres.pythonanywhere-services.com'
ENV DATABASE_NAME='ekart_vamsmechatronica'
ENV DATABASE_USERNAME='admin_vams'
ENV PASSWORD='Shekhar123#'
ENV DATABASE_PORT='13091'
ENV DJANGO_ALLOWED_HOSTS="127.0.0.1,www.vamscentral.com,*"
ENV DJANGO_ADMIN_URL=""
ENV DJANGO_ACCOUNT_ALLOW_REGISTRATION=True
ENV APP_DOMAIN="https://cliphert.com"
ENV SETTINGS_CONFIG_FILE="local"
ENV AUTH_USER_MODEL="user.CustomUser"
ENV ADMIN_SITE_HEADER="VAMS Central"
ENV ADMIN_INDEX_TITLE="VAMS Central"
ENV ADMIN_SITE_TITLE="VAMS"
ENV ACCOUNT_AUTHENTICATION_METHOD='mobileno'
ENV ACCOUNT_USERNAME_REQUIRED=False
ENV ACCOUNT_EMAIL_REQUIRED=False
ENV ACCOUNT_UNIQUE_EMAIL=False
ENV ACCOUNT_EMAIL_VERIFICATION='none'
ENV INSTAMOJO_API_KEY='test_6c999f6bdcbf869b5f5ca51d5c5'
ENV INSTAMOJO_AUTH_TOKEN='test_b34ce3800aadbafa0d4b6e3a830'
ENV INSTAMOJO_API_SALT='ca21cee242b94c49bd4a721643e1eb62'
ENV PAYMENT_SUCCESS_REDIRECT_URL='https://www.vamscentral.com/cart/paymentstatusupdate/'
ENV INSTAMOJO_SEND_PAYMENT_RECEIVED_SMS=False
ENV INSTAMOJO_SEND_PAYMENT_RECEIVED_EMAIL=False
ENV INSTAMOJO_TEST_ENDPOINT=

ENV RAZORPAY_API_KEY='rzp_test_6GPqfE53Z0xwk8'
ENV RAZORPAY_API_KEY_SECRET='9aP3x9ZJwQPp5mn4fCZvqNk4'
ENV SENDER_PHONE_NUMBER=447860099299
ENV INFOBIP_API_KEY='022f7521e0b1e549dda39b22d8ba602a-e8761ae7-2b16-4374-9a64-0664a6eeec32'
ENV INFOBIP_BASE_URL='2vmy9l.api.infobip.com'
ENV PHONEPE_MERCHANT_ID='PGTESTPAYUAT'
ENV PHONEPE_SALT_KEY='099eb0cd-02cf-4e2a-8aca-3e6c6aff0399'
ENV PHONEPE_USER_ID='M11IAE6S0K0S'


ENV API_VERSION="v1"