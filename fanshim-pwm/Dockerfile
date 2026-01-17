ARG BUILD_FROM
FROM $BUILD_FROM

# Install needed packages
RUN apk add --no-cache \
    python3 \
    py3-pip \
    gcc \
    musl-dev \
    python3-dev \
    linux-headers \
    git \
    libgpiod \
    libgpiod-dev \
    py3-psutil

# Install Python dependencies with break-system-packages flag
RUN pip3 install --break-system-packages --no-cache-dir \
    RPi.GPIO \
    gpiod

# Copy run script
COPY run.sh /
RUN chmod a+x /run.sh

# Run
CMD [ "/run.sh" ]
