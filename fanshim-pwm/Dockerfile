ARG BUILD_FROM=ghcr.io/home-assistant/aarch64-base-python:latest
FROM $BUILD_FROM

# Install packages
RUN apk add --no-cache \
    libgpiod \
    libgpiod-dev \
    gcc \
    musl-dev

# Install Python packages
RUN pip3 install --no-cache-dir \
    RPi.GPIO \
    gpiod \
    psutil

# Copy files
COPY ha_fanshim_pwm.py /app/ha_fanshim_pwm.py
COPY run.sh /run.sh
RUN chmod +x /run.sh
