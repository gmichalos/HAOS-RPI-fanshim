ARG BUILD_FROM=ghcr.io/home-assistant/raspberrypi4-64-homeassistant:stable
FROM $BUILD_FROM

# Install needed packages
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
      build-essential git libgpiod2 libgpiod-dev python3-dev ca-certificates && \
    rm -rf /var/lib/apt/lists/*

# Install Python libs
RUN pip3 install --no-cache-dir rpi-fanshim psutil

# Create data folder
WORKDIR /data

# Copy files
COPY run.sh /run.sh
COPY ha_fanshim_pwm.py /data/ha_fanshim_pwm.py

RUN chmod a+x /run.sh

CMD [ "/run.sh" ]
