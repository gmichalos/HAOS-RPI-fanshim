#!/usr/bin/env python3
import json
import time
import sys
import pigpio
import paho.mqtt.client as mqtt

PIN_FAN = 18

class FanController:
    def __init__(self, pi, options):
        self.pi = pi
        self.options = options
        self.manual_speed = None
        self.manual_control = options.get("manual_control", False)
        self.last_auto_speed = 0
        self.fan_active = False
        
        # MQTT setup
        self.mqtt_client = mqtt.Client()
        self.mqtt_client.on_connect = self.on_mqtt_connect
        self.mqtt_client.on_message = self.on_mqtt_message
        
        try:
            self.mqtt_client.connect("core-mosquitto", 1883, 60)
            self.mqtt_client.loop_start()
            print("Connected to MQTT broker")
        except Exception as e:
            print(f"MQTT connection failed: {e}")
            print("Manual control will not be available")
    
    def on_mqtt_connect(self, client, userdata, flags, rc):
        print("MQTT connected!")
        
        # Publish discovery config for Home Assistant
        config = {
            "name": "FanSHIM Speed",
            "unique_id": "fanshim_speed",
            "command_topic": "fanshim/speed/set",
            "state_topic": "fanshim/speed/state",
            "min": 0,
            "max": 100,
            "mode": "slider",
            "unit_of_measurement": "%",
            "icon": "mdi:fan"
        }
        client.publish("homeassistant/number/fanshim/speed/config", 
                      json.dumps(config), retain=True)
        
        # Subscribe to commands
        client.subscribe("fanshim/speed/set")
        
        # Publish mode switch
        mode_config = {
            "name": "FanSHIM Manual Control",
            "unique_id": "fanshim_manual",
            "command_topic": "fanshim/manual/set",
            "state_topic": "fanshim/manual/state",
            "payload_on": "ON",
            "payload_off": "OFF",
            "icon": "mdi:cog"
        }
        client.publish("homeassistant/switch/fanshim/manual/config",
                      json.dumps(mode_config), retain=True)
        
        client.subscribe("fanshim/manual/set")
        
        # Publish initial states
        client.publish("fanshim/manual/state", "ON" if self.manual_control else "OFF")
    
    def on_mqtt_message(self, client, userdata, msg):
        if msg.topic == "fanshim/speed/set":
            try:
                self.manual_speed = int(float(msg.payload.decode()))
                print(f"Manual speed set to: {self.manual_speed}%")
            except:
                pass
        elif msg.topic == "fanshim/manual/set":
            self.manual_control = msg.payload.decode() == "ON"
            print(f"Manual control: {self.manual_control}")
            client.publish("fanshim/manual/state", 
                          "ON" if self.manual_control else "OFF")
    
    def publish_state(self, speed):
        try:
            self.mqtt_client.publish("fanshim/speed/state", int(speed))
        except:
            pass
    
    def get_speed(self, auto_speed):
        if self.manual_control and self.manual_speed is not None:
            return self.manual_speed
        self.last_auto_speed = auto_speed
        return auto_speed

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
    
    print(f"Starting FanSHIM Hardware PWM Control")
    print(f"Temperature range: {TEMP_MIN}°C - {TEMP_MAX}°C")
    print(f"Hysteresis: {HYSTERESIS}°C")
    print(f"PWM range: {PWM_MIN}% - {PWM_MAX}%")
    print(f"PWM frequency: {PWM_FREQ}Hz")
    sys.stdout.flush()
    
    # Connect to pigpiod
    print("Connecting to pigpiod...")
    pi = pigpio.pi('localhost', 8888)
    
    if not pi.connected:
        print("ERROR: Failed to connect to pigpiod!")
        sys.exit(1)
    
    print("Connected to pigpiod!")
    pi.set_PWM_frequency(PIN_FAN, PWM_FREQ)
    pi.set_PWM_range(PIN_FAN, 100)
    
    # Initialize controller with MQTT
    controller = FanController(pi, options)
    
    # State tracking for hysteresis
    fan_on = False
    
    def get_temp():
        with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
            return int(f.read()) / 1000
    
    def calculate_auto_speed(temp):
        nonlocal fan_on
        
        # Hysteresis logic: 
        # Turn ON when temp >= TEMP_MIN
        # Turn OFF when temp <= (TEMP_MIN - HYSTERESIS)
        # This prevents rapid on/off cycling
        
        turn_on_temp = TEMP_MIN
        turn_off_temp = TEMP_MIN - HYSTERESIS
        
        if not fan_on:
            # Fan is OFF - check if we should turn it ON
            if temp < turn_on_temp:
                return 0  # Stay off
            else:
                fan_on = True  # Turn on
        
        if fan_on:
            # Fan is ON - check if we should turn it OFF
            if temp <= turn_off_temp:
                fan_on = False
                return 0  # Turn off
            
            # Fan stays on - calculate speed
            if temp >= TEMP_MAX:
                return PWM_MAX
            else:
                # Linear interpolation between TEMP_MIN and TEMP_MAX
                slope = (PWM_MAX - PWM_MIN) / (TEMP_MAX - TEMP_MIN)
                speed = PWM_MIN + slope * (temp - TEMP_MIN)
                return max(PWM_MIN, min(PWM_MAX, speed))
        
        return 0
    
    print("FanSHIM running with hysteresis control...")
    sys.stdout.flush()
    
    try:
        while True:
            temp = get_temp()
            auto_speed = calculate_auto_speed(temp)
            actual_speed = controller.get_speed(auto_speed)
            
            pi.set_PWM_dutycycle(PIN_FAN, int(actual_speed))
            controller.publish_state(actual_speed)
            
            mode = "MANUAL" if controller.manual_control else "AUTO"
            status = "ON" if fan_on else "OFF"
            print(f"Temp: {temp:.1f}°C | Mode: {mode} | Fan: {status} | Speed: {actual_speed:.0f}%")
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
