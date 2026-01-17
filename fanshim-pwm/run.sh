#!/bin/bash
set -e

echo "Starting FanSHIM PWM..."

# Wait for GPIO
while [ ! -e /dev/gpiomem ]; do
  echo "Waiting for /dev/gpiomem..."
  sleep 1
done

echo "GPIO available, starting service"
python3 /app/ha_fanshim_pwm.py
