#!/usr/bin/with-contenv bashio

bashio::log.info "========================================="
bashio::log.info "Starting FanSHIM PWM Add-on"
bashio::log.info "========================================="

# Run Python script
exec python3 -u /ha_fanshim_pwm.py
