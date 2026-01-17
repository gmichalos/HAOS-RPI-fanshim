#!/usr/bin/env python3
import json
import time
import sys
import pigpio

PIN_FAN = 18

def main():
    try:
        with open("/data/options.json") as f:
            options = json.load(f)
    except FileNotFoundError:
        print("ERROR: /data/options.json not found!")
        sys.exit(1)
    
    TEMP_MIN = options.get("temp_min", 45)
    TEMP_MAX = options.get("temp_max", 75)
    PWM_MIN = options.get("pwm_min", 20)
    PWM_MAX = options.get("pwm_max", 100)
    SLEEP_TIME = options.get("check_interval", 5)
    PWM_FREQ = options.get("pwm_frequency", 25000)
    HYSTERESIS = options.get("hysteresis", 5)
    
    print(f"Starting FanSHIM Hardware PWM Control (via pigpiod)")
    print(f"Temperature range: {TEMP_MIN}°C - {TEMP_MAX}°C")
    print(f"Hysteresis: {HYSTERESIS}°C")
    print(f"PWM range: {PWM_MIN}% - {PWM_MAX}%")
    print(f"PWM frequency: {PWM_FREQ}Hz")
    print(f"Check interval: {SLEEP_TIME}s")
    sys.stdout.flush()
    
    # Connect to pigpiod daemon
    print("Connecting to pigpiod daemon...")
    pi = pigpio.pi('localhost', 8888)
    
    if not pi.connected:
        print("ERROR: Failed to connect to pigpiod!")
        print("Make sure the 'pigpio' add-on is installed and running")
        sys.exit(1)
    
    print("Connected to pigpiod!")
    
    # Configure PWM
    pi.set_PWM_frequency(PIN_FAN, PWM_FREQ)
    pi.set_PWM_range(PIN_FAN, 100)
    
    # State tracking for hysteresis
    fan_on = False
    
    def get_temp():
        with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
            return int(f.read()) / 1000
    
    def calculate_pwm(temp):
        nonlocal fan_on
        
        # Hysteresis logic:
        # Turn ON when temp >= TEMP_MIN
        # Turn OFF when temp <= (TEMP_MIN - HYSTERESIS)
        
        turn_on_temp = TEMP_MIN
        turn_off_temp = TEMP_MIN - HYSTERESIS
        
        if not fan_on:
            # Fan is OFF - check if should turn ON
            if temp < turn_on_temp:
                return 0
            else:
                fan_on = True
        
        if fan_on:
            # Fan is ON - check if should turn OFF
            if temp <= turn_off_temp:
                fan_on = False
                return 0
            
            # Calculate speed based on temperature
            if temp >= TEMP_MAX:
                return PWM_MAX
            else:
                slope = (PWM_MAX - PWM_MIN) / (TEMP_MAX - TEMP_MIN)
                speed = PWM_MIN + slope * (temp - TEMP_MIN)
                return max(PWM_MIN, min(PWM_MAX, speed))
        
        return 0
    
    print("FanSHIM Hardware PWM running...")
    sys.stdout.flush()
    
    try:
        while True:
            temp = get_temp()
            duty = calculate_pwm(temp)
            pi.set_PWM_dutycycle(PIN_FAN, int(duty))
            
            status = "ON" if fan_on else "OFF"
            print(f"Temp: {temp:.1f}°C | Fan: {status} | PWM: {duty:.0f}%")
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
        pi.set_PWM_dutycycle(PIN_FAN, 0)
        pi.stop()
        print("Shutdown complete")

if __name__ == "__main__":
    main()
