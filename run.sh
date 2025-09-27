#!/usr/bin/env bash
set -e

# Ensure config folder exists
mkdir -p /config/fanshim

# Wait until GPIO port is available
i=0
while [ ! -e /dev/gpiomem ] && [ $i -lt 30 ]; do
  echo "Waiting for /dev/gpiomem..."
  sleep 1
  i=$((i+1))
done

if [ ! -e /dev/gpiomem ]; then
  echo "/dev/gpiomem not found: the addon needs access to the Pi GPIO (run on Pi or ensure device mapping)."
  exit 1
fi

exec python3 /data/ha_fanshim_pwm.py
