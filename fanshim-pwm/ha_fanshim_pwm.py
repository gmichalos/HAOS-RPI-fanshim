#!/usr/bin/env python3
import json
import time
import sys
from fanshim import FanShim

def main():
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
    
    print(f"Starting FanSHIM Control (Pimoroni Library with PWM)")
    print(f"Temperature range: {TEMP_LOW}°C - {TEMP_HIGH}°C")
    print(f"PWM range: {PWM_MIN}% - {PWM_MAX}%")
    print(f"Check interval: {SLEEP_TIME}s")
    sys.stdout.flush()
    
    # Initialize FanShim
    print("Initializing FanShim...")
    fanshim = FanShim()
    
    def get_temp():
        with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
            return int(f.read()) / 1000
    
    def calculate_speed(temp):
        if temp < TEMP_LOW:
            return 0
        elif temp > TEMP_HIGH:
            return PWM_MAX
        else:
            slope = (PWM_MAX - PWM_MIN) / (TEMP_HIGH - TEMP_LOW)
            return int(PWM_MIN + slope * (temp - TEMP_LOW))
    
    print("FanSHIM running with PWM control...")
    sys.stdout.flush()
    
    try:
        while True:
            temp = get_temp()
            speed_percent = calculate_speed(temp)
            
            # Convert percentage to 0-255 range for PWM
            pwm_value = int((speed_percent / 100.0) * 255)
            
            if pwm_value > 0:
                fanshim.set_fan(True)
                # Set PWM speed (0-255)
                fanshim.fanshim.set_fan_pwm(pwm_value)
                print(f"Temp: {temp:.1f}°C | PWM: {speed_percent}% ({pwm_value}/255)")
            else:
                fanshim.set_fan(False)
                print(f"Temp: {temp:.1f}°C | Fan: OFF")
            
            sys.stdout.flush()
            time.sleep(SLEEP_TIME)
            
    except KeyboardInterrupt:
        print("Shutting down...")
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        print("Cleaning up...")
        fanshim.set_fan(False)
        print("Shutdown complete")

if __name__ == "__main__":
    main()
