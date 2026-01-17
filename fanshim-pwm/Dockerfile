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

# Copy rootfs
COPY rootfs /
```
# Make run script executable
RUN chmod +x /etc/s6-overlay/s6-rc.d/fanshim/run


**3. Create `rootfs/etc/s6-overlay/s6-rc.d/fanshim/type` with just this text:**
```
longrun