ARG BUILD_FROM
FROM $BUILD_FROM

# Install build dependencies
RUN apk add --no-cache \
    python3 \
    py3-pip \
    gcc \
    musl-dev \
    python3-dev \
    libgpiod \
    libgpiod-dev \
    py3-psutil \
    make \
    git

# Build and install pigpio from source
RUN cd /tmp && \
    git clone https://github.com/joan2937/pigpio.git && \
    cd pigpio && \
    make && \
    make install && \
    cd .. && \
    rm -rf pigpio

# Install Python pigpio library
RUN pip3 install --break-system-packages --no-cache-dir pigpio

# Copy Python script
COPY ha_fanshim_pwm.py /app/ha_fanshim_pwm.py

# Create s6-overlay service structure
RUN mkdir -p /etc/s6-overlay/s6-rc.d/fanshim && \
    mkdir -p /etc/s6-overlay/s6-rc.d/user/contents.d

# Create type file
RUN echo "longrun" > /etc/s6-overlay/s6-rc.d/fanshim/type

# Create run script that starts pigpiod daemon first
RUN echo '#!/bin/sh' > /etc/s6-overlay/s6-rc.d/fanshim/run && \
    echo 'echo "Starting FanSHIM PWM"' >> /etc/s6-overlay/s6-rc.d/fanshim/run && \
    echo 'pigpiod' >> /etc/s6-overlay/s6-rc.d/fanshim/run && \
    echo 'sleep 1' >> /etc/s6-overlay/s6-rc.d/fanshim/run && \
    echo 'exec python3 -u /app/ha_fanshim_pwm.py' >> /etc/s6-overlay/s6-rc.d/fanshim/run && \
    chmod +x /etc/s6-overlay/s6-rc.d/fanshim/run

# Link service to user bundle
RUN touch /etc/s6-overlay/s6-rc.d/user/contents.d/fanshim
