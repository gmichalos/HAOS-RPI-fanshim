#!/usr/bin/env python3
import os
import json
import time
import sys

PIN_FAN = 18  # GPIO18 = PWM0
PWM_CHIP = 0
PWM_CHANNEL = 0

class HardwarePWM:
    def __init__(self, chip, channel):
        self.chip = chip
        self.channel = channel
        self.pwm_path = f"/sys/class/pwm/pwmchip{chip}/pwm{channel}"
        self.export_path = f"/sys/class/pwm/pwmchip{chip}/export"
        self.unexport_path = f"/sys/class/pwm/pwmchip{chip}/unexport"
        
        # Export PWM channel if not already exported
        if not os.path.exists(self.pwm_path):
            try:
                with open(self.export_path, 'w') as f:
                    f.write(str(channel))
                time.sleep(0.1)
            except:
                pass
    
    def set_frequency(self, freq_hz):
        """Set PWM frequency in Hz"""
        period_ns = int(1000000000 / freq_hz)
        with open(f"{self.pwm_path}/period", 'w') as f:
            f.write(str(period_ns))
        self.period_ns = period_ns
    
    def set_duty_cycle(self, percent):
        """Set duty cycle as percentage (0-100)"""
        duty_ns = int(self.period_ns * (percent / 100))
        with open(f"{self.pwm_path}/duty_cycle", 'w') as f:
            f.write(str(duty_ns))
    
    def enable(self):
        """Enable PWM output"""
        with open(f"{self.pwm_path}/enable", 'w') as f:
            f.write('1')
    
    def disable(self):
        """Disable PWM output"""
        with open(f"{self.pwm_path}/enable", 'w') as f:
            f.write('0')
    
    def cleanup(self):
        """Cleanup PWM"""
        try:
            self.disable()
            with open(self.unexport_path, 'w') as f:
                f.write(str(self.channel))
        except:
            pass

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
    
    print(f"Starting FanSHIM Hardware PWM Control")
    print(f"Temperature range: {TEMP_LOW}°C - {TEMP_HIGH}°C")
    print(f"PWM range: {PWM_MIN}% - {PWM_MAX}%")
    print(f"Check interval: {SLEEP_TIME}s")
    sys.stdout.flush()
    
    # Initialize hardware PWM
    print("Initializing hardware PWM...")
    pwm = HardwarePWM(PWM_CHIP, PWM_CHANNEL)
    pwm.set_frequency(25000)  # 25kHz
    pwm.enable()
    
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
    
    print("FanSHIM Hardware PWM running...")
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
        print("Received interrupt signal, shutting down...")
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        print("Cleaning up PWM...")
        pwm.cleanup()
        print("Shutdown complete")

if __name__ == "__main__":
    main()
