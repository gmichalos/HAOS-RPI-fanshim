ARG BUILD_FROM
FROM $BUILD_FROM

# Install packages
RUN apk add --no-cache \
    python3 \
    py3-pip \
    gcc \
    musl-dev \
    python3-dev \
    libgpiod \
    libgpiod-dev \
    py3-psutil

# Install Python packages
RUN pip3 install --break-system-packages --no-cache-dir \
    RPi.GPIO \
    gpiod

# Copy Python script
COPY ha_fanshim_pwm.py /app/ha_fanshim_pwm.py

# Copy and setup run script
COPY run.sh /run.sh
RUN chmod +x /run.sh
