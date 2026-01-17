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

# Copy files
COPY ha_fanshim_pwm.py /ha_fanshim_pwm.py
COPY run.sh /etc/s6-overlay/s6-rc.d/fanshim/run
RUN chmod +x /etc/s6-overlay/s6-rc.d/fanshim/run

# Create service type file
RUN mkdir -p /etc/s6-overlay/s6-rc.d/fanshim && \
    echo "longrun" > /etc/s6-overlay/s6-rc.d/fanshim/type && \
    mkdir -p /etc/s6-overlay/s6-rc.d/user/contents.d && \
    touch /etc/s6-overlay/s6-rc.d/user/contents.d/fanshim
