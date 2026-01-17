#!/usr/bin/env python3
import json
import time
import sys
import gpiod
from gpiod.line import Direction, Value
import threading

PIN_FAN = 18

class SoftwarePWM:
    def __init__(self, line_request, pin, frequency=25000):
        self.line_request = line_request
        self.pin = pin
        self.frequency = frequency
        self.period = 1.0 / frequency
        self.duty_cycle = 0
        self.running = False
        self.thread = None
        
    def start(self, duty_cycle=0):
        self.duty_cycle = duty_cycle
        self.running = True
        self.thread = threading.Thread(target=self._pwm_loop, daemon=True)
        self.thread.start()
    
    def set_duty_cycle(self, duty_cycle):
        self.duty_cycle = max(0, min(100, duty_cycle))
    
    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join()
        self.line_request.set_value(self.pin, Value.INACTIVE)
    
    def _pwm_loop(self):
        while self.running:
            if self.duty_cycle > 0:
                on_time = self.period * (self.duty_cycle / 100.0)
                off_time = self.period - on_time
                
                if on_time > 0:
                    self.line_request.set_value(self.pin, Value.ACTIVE)
                    time.sleep(on_time)
                
                if off_time > 0 and self.running:
                    self.line_request.set_value(self.pin, Value.INACTIVE)
                    time.sleep(off_time)
            else:
                self.line_request.set_value(self.pin, Value.INACTIVE)
                time.sleep(self.period)

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
    
    print(f"Starting FanSHIM Software PWM Control")
    print(f"Temperature range: {TEMP_LOW}°C - {TEMP_HIGH}°C")
    print(f"PWM range: {PWM_MIN}% - {PWM_MAX}%")
    print(f"PWM frequency: 25kHz")
    print(f"Check interval: {SLEEP_TIME}s")
    sys.stdout.flush()
    
    # Open GPIO chip and request line
    print("Initializing GPIO...")
    chip = gpiod.Chip('/dev/gpiochip0')
    line_config = gpiod.LineSettings(direction=Direction.OUTPUT)
    line_request = chip.request_lines(
        config={PIN_FAN: line_config},
        consumer="fanshim"
    )
    
    print("GPIO initialized!")
    sys.stdout.flush()
    
    # Start software PWM
    pwm = SoftwarePWM(line_request, PIN_FAN, frequency=25000)
    pwm.start(0)
    
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
    
    print("FanSHIM Software PWM running...")
    sys.stdout.flush()
    
    try:
        while True:
            temp = get_temp()
            duty = calculate_pwm(temp)
            pwm.set_duty_cycle(duty)
            
            print(f"Temp: {temp:.1f}°C | PWM: {duty:.0f}%")
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
        pwm.stop()
        line_request.release()
        print("Shutdown complete")

if __name__ == "__main__":
    main()
