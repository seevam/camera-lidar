# Camera Vehicle Troubleshooting Guide

## Vehicle Not Moving - Quick Diagnosis

### Step 1: Run System Diagnostic

```bash
cd /home/user/camera-lidar/camer-vehicle/test
python3 test_system_diagnostic.py
```

This will automatically test:
- Camera connection
- Arduino connection
- Serial communication
- Motor commands

### Step 2: Check Arduino Code Upload

**Verify Arduino code is uploaded:**

1. Open Arduino IDE
2. Open `/home/user/camera-lidar/camer-vehicle/arduino/camera_vehicle_enhanced.ino`
3. Select correct board and port
4. Upload to Arduino
5. Open Serial Monitor (115200 or 9600 baud)
6. You should see: "Camera Vehicle Ready!" or "CAMERA VEHICLE - ENHANCED VERSION"

**If you see nothing in Serial Monitor:**
- Code not uploaded correctly
- Wrong baud rate selected
- Wrong board selected

### Step 3: Test Arduino Independently

**Using Serial Monitor:**

1. Open Arduino Serial Monitor
2. Set baud rate to 9600
3. Type these commands and press Enter:

```
HELP          → Should show help menu (enhanced version)
STATUS        → Should show system status
F:150         → Motors should move forward
S             → Motors should stop
TEST          → Run diagnostic test (motors will move)
```

**If motors don't move:**
- Check wiring (see below)
- Check power supply
- Check motor driver

### Step 4: Check Wiring

**Arduino to Motor Driver (L298N or similar):**

```
Arduino Pin  →  Motor Driver
---------------------------------
Pin 2        →  IN1 (Left Forward)
Pin 3        →  IN2 (Left Backward)
Pin 4        →  IN3 (Right Forward)
Pin 5        →  IN4 (Right Backward)
Pin 9        →  ENA (Left Enable) - Must be PWM pin
Pin 10       →  ENB (Right Enable) - Must be PWM pin
GND          →  GND
```

**Motor Driver to Motors:**
```
OUT1, OUT2  →  Left Motor
OUT3, OUT4  →  Right Motor
```

**Power:**
```
Motor Driver +12V → Battery/Power Supply (6-12V)
Motor Driver GND  → Power Supply GND AND Arduino GND (common ground!)
Arduino 5V        → Do NOT connect to motor power
```

### Step 5: Check Python Configuration

**Verify Arduino port in config.yaml:**

```bash
# Find Arduino port
ls /dev/ttyUSB* /dev/ttyACM*    # Linux
# or
ls /dev/cu.*                    # Mac
```

**Edit config.yaml:**
```yaml
arduino:
  port: "/dev/ttyUSB0"    # Change to your actual port
  baudrate: 9600
  max_speed: 150
```

### Step 6: Test Python to Arduino Communication

```bash
cd /home/user/camera-lidar/camer-vehicle/src
python3
```

```python
import serial
import time

# Change port to match your Arduino
ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)
time.sleep(2)  # Wait for Arduino reset

# Send forward command
ser.write(b'F:150\n')
time.sleep(2)

# Send stop command
ser.write(b'S\n')

# Close
ser.close()
```

**If this works:** Python can talk to Arduino, problem is elsewhere
**If this fails:** Serial port issue, check port and permissions

### Step 7: Check Camera Line Detection

The vehicle won't move if it can't detect the line!

```bash
cd /home/user/camera-lidar/camer-vehicle/src
python3 main.py
```

**Watch the debug window:**
- Green line should appear on detected line
- Blue line shows center
- Console shows: "Frame X: Error=Y, Steering=Z"

**If no line detected:**
- Adjust `threshold` in config.yaml (try 40-100)
- Ensure good contrast (black line on white surface)
- Check lighting conditions
- Use test_camera_lighting.py to see what camera sees

## Common Issues & Solutions

### Issue: "Permission denied" on /dev/ttyUSB0

**Solution:**
```bash
# Add user to dialout group
sudo usermod -a -G dialout $USER

# Or run with sudo (not recommended)
sudo python3 main.py
```

### Issue: Motors move but vehicle doesn't follow line

**Causes:**
1. **Line not detected**
   - Run: `python3 test/test_camera_lighting.py`
   - Adjust threshold in config.yaml

2. **PID tuning wrong**
   - Try these values in config.yaml:
   ```yaml
   pid:
     kp: 1.0   # Increase for faster response
     ki: 0.0   # Keep at 0 initially
     kd: 0.2   # Increase to reduce oscillation
   ```

3. **Camera angle wrong**
   - Camera should point down at ~30-45° angle
   - Should see line in bottom 40% of frame

### Issue: Vehicle only moves briefly then stops

**Causes:**
1. **Line lost** - Confidence too low
   - Lower `min_confidence` in config.yaml
   - Improve lighting
   - Adjust threshold

2. **Command timeout** (enhanced Arduino)
   - Commands must be sent regularly
   - Check main.py is running continuously

### Issue: "Camera failed to open"

**Solutions:**
```bash
# Check available cameras
ls /dev/video*

# Try different camera ID in config.yaml
camera:
  device_id: 0  # Try 1, 2, etc.
```

### Issue: Motors spin in wrong direction

**Solutions:**
1. Swap motor wires at motor driver
2. Or swap pins in Arduino code:
   ```cpp
   // Swap MOTOR_F and MOTOR_B pins
   #define LEFT_MOTOR_F 3   // Was 2
   #define LEFT_MOTOR_B 2   // Was 3
   ```

### Issue: One motor doesn't work

**Check:**
1. Wiring to that motor
2. Motor driver channel
3. PWM signal on enable pin (pins 9, 10)
4. Motor itself (swap with working motor to test)

## Diagnostic Checklist

- [ ] Arduino code uploaded successfully
- [ ] Serial monitor shows startup message
- [ ] Motors respond to serial commands (F:150, S, etc.)
- [ ] Camera opens and shows video
- [ ] Line visible in camera view
- [ ] Correct Arduino port in config.yaml
- [ ] User in dialout group (Linux)
- [ ] Motor driver has power
- [ ] All grounds connected together
- [ ] PWM pins used for enable (9, 10)
- [ ] Debug mode enabled in config.yaml

## Getting Help

If still not working:

1. Run diagnostic: `python3 test/test_system_diagnostic.py`
2. Note which tests fail
3. Check wiring diagram
4. Verify power supply voltage (6-12V for motors)
5. Test each component individually

## Quick Test Commands

```bash
# Test camera only
python3 test/test_camera_lighting.py

# Test system components
python3 test/test_system_diagnostic.py

# Test lane detection
python3 test/test_lane_detection.py

# Run full system with debug
python3 src/main.py  # (with debug: true in config.yaml)
```
