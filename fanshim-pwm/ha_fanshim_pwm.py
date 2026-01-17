#!/usr/bin/env python3
import json
import time
import sys
import pigpio

PIN_FAN = 18  # GPIO18

def main():
    # Load config
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
    
    print(f"Starting FanSHIM PWM Control (pigpio)")
    print(f"Temperature range: {TEMP_LOW}°C - {TEMP_HIGH}°C")
    print(f"PWM range: {PWM_MIN}% - {PWM_MAX}%")
    print(f"Check interval: {SLEEP_TIME}s")
    sys.stdout.flush()
    
    # Connect to pigpio daemon
    print("Connecting to pigpio daemon...")
    pi = pigpio.pi()
    
    if not pi.connected:
        print("ERROR: Failed to connect to pigpio daemon!")
        sys.exit(1)
    
    print("Connected! Initializing PWM...")
    pi.set_PWM_frequency(PIN_FAN, 25000)  # 25kHz
    pi.set_PWM_range(PIN_FAN, 100)  # 0-100 range
    
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
            pi.set_PWM_dutycycle(PIN_FAN, int(duty))
            
            print(f"Temp: {temp:.1f}°C | PWM: {duty:.0f}%")
            sys.stdout.flush()
            time.sleep(SLEEP_TIME)
            
    except KeyboardInterrupt:
        print("Received interrupt signal, shutting down...")
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        print("Cleaning up...")
        pi.set_PWM_dutycycle(PIN_FAN, 0)
        pi.stop()
        print("Shutdown complete")

if __name__ == "__main__":
    main()
