#!/usr/bin/env python3
import os
import json
import time
import sys
import RPi.GPIO as GPIO

PIN_FAN = 18  # PWM pin

def main():
    # Load config from config.json
    try:
        with open("/data/options.json") as f:
            options = json.load(f)
    except FileNotFoundError:
        print("ERROR: /data/options.json not found!")
        sys.exit(1)
    
    TEMP_LOW = options.get("temp_min", 45)
    TEMP_HIGH = options.get("temp_max", 75)
    PWM_MIN = options.get("pwm_min", 20)
    PWM_MAX = options.get("pwm_max", 100)
    SLEEP_TIME = options.get("check_interval", 5)
    
    print(f"Starting FanSHIM PWM Control")
    print(f"Temperature range: {TEMP_LOW}°C - {TEMP_HIGH}°C")
    print(f"PWM range: {PWM_MIN}% - {PWM_MAX}%")
    print(f"Check interval: {SLEEP_TIME}s")
    
    # Wait for GPIO to be available
    max_wait = 30
    for i in range(max_wait):
        if os.path.exists("/dev/gpiomem"):
            break
        print(f"Waiting for /dev/gpiomem... ({i+1}/{max_wait})")
        time.sleep(1)
    
    if not os.path.exists("/dev/gpiomem"):
        print("ERROR: /dev/gpiomem not found after waiting!")
        sys.exit(1)
    
    print("GPIO available, initializing...")
    
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(PIN_FAN, GPIO.OUT)
    fan_pwm = GPIO.PWM(PIN_FAN, 25000)
    fan_pwm.start(0)
    
    def get_temp():
        with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
            return int(f.read()) / 1000
    
    def calculate_pwm(temp):
        if temp < TEMP_LOW:
            return 0
        elif temp > TEMP_HIGH:
            return PWM_MAX
        else:
            slope = (PWM_MAX - PWM_MIN) / (TEMP_HIGH - TEMP_LOW)
            return PWM_MIN + slope * (temp - TEMP_LOW)
    
    print("FanSHIM PWM running...")
    sys.stdout.flush()
    
    try:
        while True:
            temp = get_temp()
            duty = calculate_pwm(temp)
            fan_pwm.ChangeDutyCycle(duty)
            print(f"Temp: {temp:.1f}°C | PWM: {duty:.0f}%")
            sys.stdout.flush()
            time.sleep(SLEEP_TIME)
    except KeyboardInterrupt:
        print("Received interrupt signal, shutting down...")
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)
    finally:
        print("Cleaning up GPIO...")
        fan_pwm.stop()
        GPIO.cleanup()
        print("Shutdown complete")

if __name__ == "__main__":
    main()
