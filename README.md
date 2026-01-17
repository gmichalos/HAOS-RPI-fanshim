# FanSHIM PWM Add-on for Home Assistant

Home Assistant add-on to control the [Pimoroni FanSHIM](https://shop.pimoroni.com/products/fan-shim) with hardware PWM on Raspberry Pi.

## Features

- 🌡️ **Automatic temperature-based fan control**
- ⚙️ **Hardware PWM support** via pigpio daemon
- 🔄 **Hysteresis control** prevents rapid on/off cycling
- 📊 **Configurable temperature thresholds and fan speeds**
- 🎛️ **Adjustable PWM frequency** to eliminate fan noise
- 📝 **Real-time logging** of temperature and fan status

## Prerequisites

1. **Raspberry Pi4** running Home Assistant OS
2. **Pimoroni FanSHIM** installed on GPIO header
3. **pigpio add-on** installed and running

### Installing pigpio Add-on

The pigpio add-on provides hardware PWM support which is essential for smooth fan control.

1. Go to **Settings → Add-ons → Add-on Store**
2. Click **⋮ (three dots)** → **Repositories**
3. Add repository: `https://github.com/Poeschl-HomeAssistant-Addons/repository`
4. Find and install **pigpio** add-on
5. Start the pigpio add-on
6. Enable **Start on boot** for pigpio
7. ✅ Verify it shows as **Started** before proceeding

## Installation

1. Go to **Settings → Add-ons → Add-on Store**
2. Click **⋮ (three dots)** → **Repositories**
3. Add this repository: `https://github.com/gmichalos/HAOS-RPI-fanshim`
4. Find **FanSHIM PWM** in the add-on store
5. Click **Install**
6. Wait for installation to complete
7. Configure the add-on (see Quick Start below)
8. Click **Start**
9. Enable **Start on boot**

## Quick Start - Testing Your FanSHIM

Before configuring automatic control, test that your FanSHIM is working:

### Step 1: Test Fan Operation

Use these settings to run the fan at 100% constantly:
```yaml
temp_min: 0           # Always above this
temp_max: 100         # Never reaches this
pwm_min: 100          # Always 100%
pwm_max: 100          # Always 100%
check_interval: 5
pwm_frequency: 25000
hysteresis: 5
```

**Expected behavior:**
- Fan should start immediately at full speed
- You should hear the fan running
- Check logs: should show `Fan: ON | PWM: 100%`

✅ **If fan works:** Continue to Step 2  
❌ **If fan doesn't work:** See Troubleshooting section

### Step 2: Find Your Optimal PWM Range

Test different minimum speeds to find the lowest speed that works without clicking:

**Test A - Standard Range (20-100%):**
```yaml
temp_min: 30          # Low threshold for testing
temp_max: 60
pwm_min: 20           # Try this first
pwm_max: 100
check_interval: 5
pwm_frequency: 25000
hysteresis: 5
```

**If you hear clicking at low speeds:**

**Test B - Higher Minimum (40-100%):**
```yaml
temp_min: 30
temp_max: 60
pwm_min: 40           # Increased minimum
pwm_max: 100
check_interval: 5
pwm_frequency: 25000
hysteresis: 5
```

**If still clicking:**

**Test C - Higher Frequency (20-100% at 50kHz):**
```yaml
temp_min: 30
temp_max: 60
pwm_min: 20
pwm_max: 100
check_interval: 5
pwm_frequency: 50000  # Increased frequency
hysteresis: 5
```

### Step 3: Set Your Production Values

Once you know what works, use realistic temperature thresholds:
```yaml
temp_min: 45          # Fan starts at 45°C
temp_max: 65          # Fan maxes out at 65°C
pwm_min: 30           # Use your tested minimum
pwm_max: 100
check_interval: 5
pwm_frequency: 25000  # Use your tested frequency
hysteresis: 5
```

## Configuration

### Configuration Options

| Option | Description | Recommended | Range |
|--------|-------------|-------------|-------|
| `temp_min` | Fan turns ON at this temperature | 45°C | 35-55°C |
| `temp_max` | Fan reaches maximum speed | 65°C | 55-75°C |
| `pwm_min` | Minimum fan speed when ON | 30% | 20-50% |
| `pwm_max` | Maximum fan speed | 100% | 80-100% |
| `check_interval` | Temperature check frequency | 5s | 2-10s |
| `pwm_frequency` | PWM frequency (affects noise) | 25000Hz | 20000-50000Hz |
| `hysteresis` | Temperature gap for on/off | 5°C | 3-10°C |

### How Hysteresis Works

Hysteresis prevents the fan from rapidly turning on and off when temperature hovers at the threshold.

**Example with `temp_min: 45` and `hysteresis: 5`:**
```
Temperature rises to 45°C  →  Fan turns ON at pwm_min (30%)
Temperature rises to 50°C  →  Fan increases to ~47%
Temperature rises to 65°C  →  Fan runs at pwm_max (100%)
Temperature drops to 55°C  →  Fan decreases to ~63%
Temperature drops to 45°C  →  Fan still ON at 30%
Temperature drops to 40°C  →  Fan turns OFF
Temperature rises to 45°C  →  Fan turns ON again
```

The 5°C gap (40°C off, 45°C on) prevents constant cycling.

## Recommended Configurations

### For Pimoroni FanSHIM - Standard (Recommended)

Best balance of cooling and noise:
```yaml
temp_min: 45
temp_max: 65
pwm_min: 30
pwm_max: 100
check_interval: 5
pwm_frequency: 100
hysteresis: 5
```

**Behavior:**
- Silent until 45°C
- Gentle ramp-up from 30% to 100%
- Won't cycle on/off rapidly

### For Pimoroni FanSHIM - Aggressive Cooling

For heavy workloads (gaming, encoding, etc.):
```yaml
temp_min: 40
temp_max: 60
pwm_min: 40
pwm_max: 100
check_interval: 3
pwm_frequency: 100
hysteresis: 3
```

**Behavior:**
- Starts cooling earlier (40°C)
- Faster response time
- Reaches max speed at lower temp

### For Pimoroni FanSHIM - Silent Operation

Maximum quiet, minimal fan cycling:
```yaml
temp_min: 50
temp_max: 70
pwm_min: 100
pwm_max: 100
check_interval: 5
pwm_frequency: 100
hysteresis: 10
```

**Behavior:**
- Only runs when really needed (50°C)
- Always runs at full speed (no PWM noise)
- Large gap prevents cycling (40°C off, 50°C on)

### For Other/Larger Fans

If you replaced the original FanSHIM fan:
```yaml
temp_min: 45
temp_max: 65
pwm_min: 100          # Many fans click below 100%
pwm_max: 100
check_interval: 5
pwm_frequency: 25000
hysteresis: 8
```

## Understanding PWM Frequency

The PWM frequency affects fan operation and noise:

| Frequency | Use Case | Noise Level |
|-----------|----------|-------------|
| 20000 Hz | May cause audible whine | ⚠️ Possible buzzing |
| 25000 Hz | **Recommended for FanSHIM** | ✅ Silent |
| 50000 Hz | If 25kHz still makes noise | ✅ Guaranteed silent |
| 100000 Hz | Excessive, not needed | ✅ Silent but unnecessary |

**Start with 25000 Hz.** Only increase if you hear noise.

## Troubleshooting

### Fan doesn't start at all

**Check:**
1. ✅ pigpio add-on is **installed** and **running**
2. ✅ FanSHIM is properly seated on GPIO pins
3. ✅ Fan orientation: should blow DOWN toward CPU
4. ✅ Check add-on logs for error messages

**Test:** Set `temp_min: 0` and `pwm_min: 100` to force fan on

### Error: "Failed to connect to pigpiod"
```
ERROR: Failed to connect to pigpiod!
Make sure the 'pigpio' add-on is installed and running
```

**Solution:**
1. Go to **Settings → Add-ons**
2. Find **pigpio** add-on
3. Click **Start** if it's stopped
4. Restart **FanSHIM PWM** add-on

### Fan makes clicking/buzzing noise

This is common with PWM at low speeds.

**Solution A - Increase minimum speed:**
```yaml
pwm_min: 50  # or higher until clicking stops
```

**Solution B - Increase frequency:**
```yaml
pwm_frequency: 50000  # Try 50kHz instead of 25kHz
```

**Solution C - Run at full speed only:**
```yaml
pwm_min: 100
pwm_max: 100
```

### Fan cycles on/off too often

**Example logs:**
```
Temp: 44.8°C | Fan: ON  | PWM: 30%
Temp: 43.2°C | Fan: OFF | PWM: 0%
Temp: 45.1°C | Fan: ON  | PWM: 30%
Temp: 43.8°C | Fan: OFF | PWM: 0%
```

**Solution - Increase hysteresis:**
```yaml
hysteresis: 10  # Bigger gap = less cycling
```

With `hysteresis: 10`:
- Fan ON at 45°C
- Fan OFF at 35°C
- 10°C gap prevents cycling

### Fan doesn't turn off

**Check configuration:**
- Temperature must drop below `temp_min - hysteresis`
- Example: `temp_min: 45`, `hysteresis: 5` → fan turns off at 40°C

**Check logs:**
```
Temp: 42.0°C | Fan: ON | PWM: 30%  ← Still above 40°C
Temp: 39.5°C | Fan: OFF | PWM: 0%  ← Below 40°C, turns off
```

### Settings don't update

**Solution:**
1. **Stop** the add-on
2. Change configuration values
3. Click **Save**
4. **Start** the add-on
5. Check logs to verify new values loaded

## Fan Orientation

⚠️ **IMPORTANT:** Install the FanSHIM correctly!

**Correct installation:**
```
     [FAN - blowing DOWN ↓]
     [==== GPIO Header ====]
     [===== Raspberry Pi =====]
            [CPU chip]
```

- Fan should blow **DOWN** toward the Raspberry Pi CPU
- Air flows from the label/sticker side → through to open grille
- If you have a heatsink, fan pushes air through it
- **Wrong orientation = poor cooling!**

**How to tell airflow direction:**
- Side with **label/sticker** = intake (air goes IN here)
- Side with **open grille** = exhaust (air comes OUT here)
- Center motor hub side usually exhausts air

## Monitoring

### View Logs

**Settings → Add-ons → FanSHIM PWM → Log tab**

Example healthy operation:
```
Starting FanSHIM Hardware PWM Control (via pigpiod)
Temperature range: 45°C - 65°C
Hysteresis: 5°C
PWM range: 30% - 100%
PWM frequency: 25000Hz
Connected to pigpiod!
FanSHIM Hardware PWM running...
Temp: 42.3°C | Fan: OFF | PWM: 0%
Temp: 46.1°C | Fan: ON | PWM: 32%
Temp: 52.8°C | Fan: ON | PWM: 56%
Temp: 41.2°C | Fan: OFF | PWM: 0%
```

### Check CPU Temperature

SSH into Home Assistant and run:
```bash
cat /sys/class/thermal/thermal_zone0/temp
```

Divide result by 1000 for temperature in °C.

Example: `45800` = 45.8°C

## Technical Details

| Spec | Value |
|------|-------|
| **GPIO Pin** | 18 (BCM numbering) |
| **PWM Method** | Hardware PWM via pigpio |
| **Fan Voltage** | 5V DC |
| **Fan Current** | ~200-400mA at full speed |
| **PWM Range** | 0-100 (duty cycle %) |
| **Frequency Range** | 1-500kHz (recommend 20-50kHz) |
| **Temperature Source** | `/sys/class/thermal/thermal_zone0/temp` |
| **Update Interval** | Configurable (default 5s) |

## FAQ

**Q: Will this work on Raspberry Pi 3?**  
A: Possibly but only tested on Pi4

**Q: Can I use this without the pigpio add-on?**  
A: No, the pigpio daemon is required for hardware PWM.

**Q: Why hardware PWM instead of software PWM?**  
A: Hardware PWM is much smoother and eliminates clicking/buzzing noises.

**Q: Can I control the fan manually?**  
A: Not in this version. It's fully automatic based on temperature.

**Q: Will this work with other fans?**  
A: It should work with any 5V fan connected to GPIO 18, but PWM behavior may vary.

**Q: Does this affect my Raspberry Pi warranty?**  
A: No, the FanSHIM is a standard GPIO accessory.

**Q: How much does the fan reduce temperature?**  
A: Typically 10-20°C reduction under load, depending on ambient temperature and workload.

## Credits

- Forked from [melvinmajor/HA-RPI-fanshim](https://github.com/melvinmajor/HA-RPI-fanshim)
- Based on [Pimoroni FanSHIM](https://github.com/pimoroni/fanshim-python)
- Uses [pigpio library](https://abyz.me.uk/rpi/pigpio/) by Joan @ AByz

## License

MIT License - See LICENSE file for details

## Support

- **Issues:** [GitHub Issues](https://github.com/gmichalos/HAOS-RPI-fanshim/issues)
- **Discussions:** [GitHub Discussions](https://github.com/gmichalos/HAOS-RPI-fanshim/discussions)
- **Pimoroni Support:** [Pimoroni Forums](https://forums.pimoroni.com/)

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history.

---

**Made with ❤️ for the Home Assistant community**
