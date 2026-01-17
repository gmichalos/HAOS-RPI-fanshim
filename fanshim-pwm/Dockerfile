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
COPY ha_fanshim_pwm.py /ha_fanshim_pwm.py
RUN chmod a+x /ha_fanshim_pwm.py

# Copy run script as the service
COPY run.sh /etc/services.d/fanshim/run
RUN chmod a+x /etc/services.d/fanshim/run
