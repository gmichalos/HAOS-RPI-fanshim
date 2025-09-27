#!/usr/bin/env python3
import time
import RPi.GPIO as GPIO

PIN_FAN = 18  # PWM pin

TEMP_LOW = 45
TEMP_HIGH = 75
PWM_MIN = 20
PWM_MAX = 100
SLEEP_TIME = 5

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

try:
    while True:
        temp = get_temp()
        duty = calculate_pwm(temp)
        fan_pwm.ChangeDutyCycle(duty)
        print(f"Temp: {temp:.1f}°C | PWM: {duty:.0f}%")
        time.sleep(SLEEP_TIME)
except KeyboardInterrupt:
    pass
finally:
    fan_pwm.stop()
    GPIO.cleanup()
