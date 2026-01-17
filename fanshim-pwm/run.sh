#!/usr/bin/with-contenv bashio
set -e

bashio::log.info "Starting FanSHIM PWM..."

# Wait for GPIO
while [ ! -e /dev/gpiomem ]; do
  bashio::log.info "Waiting for /dev/gpiomem..."
  sleep 1
done

bashio::log.info "GPIO available"

# Use exec to replace shell with python process
exec python3 /app/ha_fanshim_pwm.py
