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
    libgpiod-dev

# Install Python dependencies
RUN pip3 install --no-cache-dir \
    RPi.GPIO \
    gpiod \
    psutil

# Copy run script
COPY run.sh /
RUN chmod a+x /run.sh

# Run
CMD [ "/run.sh" ]
