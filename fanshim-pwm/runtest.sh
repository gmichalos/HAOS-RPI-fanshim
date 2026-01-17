#!/usr/bin/with-contenv bashio

bashio::log.info "Starting FanSHIM PWM..."

# Wait for GPIO
while [ ! -e /dev/gpiomem ]; do
  bashio::log.info "Waiting for /dev/gpiomem..."
  sleep 1
done

bashio::log.info "GPIO available, starting service"

# Run with exec
exec python3 /data/ha_fanshim_pwm.py
