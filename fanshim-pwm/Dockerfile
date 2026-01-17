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

# Create s6-overlay service structure
RUN mkdir -p /etc/s6-overlay/s6-rc.d/fanshim && \
    mkdir -p /etc/s6-overlay/s6-rc.d/user/contents.d

# Create type file
RUN echo "longrun" > /etc/s6-overlay/s6-rc.d/fanshim/type

# Copy run script
COPY rootfs/etc/s6-overlay/s6-rc.d/fanshim/run /etc/s6-overlay/s6-rc.d/fanshim/run
RUN chmod +x /etc/s6-overlay/s6-rc.d/fanshim/run

# Link service to user bundle
RUN touch /etc/s6-overlay/s6-rc.d/user/contents.d/fanshim
