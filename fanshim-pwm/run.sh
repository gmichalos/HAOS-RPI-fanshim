#!/usr/bin/with-contenv bashio

bashio::log.info "Starting FanSHIM PWM service"
exec python3 /ha_fanshim_pwm.py
