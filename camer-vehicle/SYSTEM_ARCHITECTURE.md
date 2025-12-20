# System Architecture - How Everything Connects

## Overview Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    YOUR COMPUTER / RASPBERRY PI             │
│                                                             │
│  ┌──────────────┐         ┌─────────────────┐             │
│  │ config.yaml  │────────>│   main.py       │             │
│  │              │  read   │  (Python)       │             │
│  │ max_speed:220│  by     │                 │             │
│  │ port: USB0   │         │ 1. Read config  │             │
│  │ threshold:60 │         │ 2. Open camera  │             │
│  └──────────────┘         │ 3. Detect line  │             │
│                           │ 4. Calculate    │             │
│  ┌──────────────┐         │    steering     │             │
│  │   Camera     │────────>│ 5. Send command │             │
│  │   (USB)      │  video  │                 │             │
│  └──────────────┘         └─────────┬───────┘             │
│                                     │                      │
│                                     │ Serial/USB           │
│                                     │ Commands:            │
│                                     │ "F:220\n"            │
│                                     │ "L:15:220\n"         │
│                                     │ "S\n"                │
└─────────────────────────────────────┼──────────────────────┘
                                      │
                                      │ USB Cable
                                      ↓
┌─────────────────────────────────────────────────────────────┐
│                      ARDUINO BOARD                          │
│                                                             │
│  ┌────────────────────────────────────────┐                │
│  │  camera_vehicle.ino (C++ code)         │                │
│  │                                        │                │
│  │  1. Wait for serial command            │                │
│  │  2. Parse command (F, L, R, S)         │                │
│  │  3. Control motor pins                 │                │
│  │  4. Set PWM speed                      │                │
│  └───────────────┬────────────────────────┘                │
│                  │                                          │
│                  │ Digital signals (pins 2,3,4,5)          │
│                  │ PWM signals (pins 9,10)                 │
└──────────────────┼──────────────────────────────────────────┘
                   │
                   ↓
┌─────────────────────────────────────────────────────────────┐
│                    MOTOR DRIVER (L298N)                     │
│                                                             │
│  Receives:                                                  │
│  - Direction signals from pins 2,3,4,5                     │
│  - Speed (PWM) from pins 9,10                              │
│  - Power from battery (6-12V)                              │
│                                                             │
│  Outputs: HIGH CURRENT to motors                           │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ↓
                    ┌───────────────┐
                    │  LEFT  RIGHT  │
                    │  MOTOR MOTOR  │
                    │   🔄    🔄    │
                    └───────────────┘
```

## How config.yaml Affects Arduino

### Step-by-Step Flow:

**Step 1: Python reads config.yaml**
```python
# main.py does this:
with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)

# Gets these values:
max_speed = config['arduino']['max_speed']  # 220
port = config['arduino']['port']            # "/dev/ttyUSB0"
```

**Step 2: Python connects to Arduino**
```python
# Opens serial connection to Arduino
arduino = serial.Serial(port, 9600)  # Uses port from config!
```

**Step 3: Python sends commands with speed from config**
```python
# When Python wants to go forward:
command = f"F:{max_speed}\n"  # Creates "F:220\n"
arduino.write(command.encode())  # Sends via USB to Arduino
```

**Step 4: Arduino receives and executes**
```cpp
// Arduino reads: "F:220\n"
// Parses it:
//   Command: F (forward)
//   Speed: 220
// Then:
analogWrite(LEFT_ENABLE, 220);   // Set motor speed
analogWrite(RIGHT_ENABLE, 220);
digitalWrite(LEFT_MOTOR_F, HIGH); // Go forward
```

## Example: What Happens When You Change config.yaml

### If you change max_speed: 220 → 255

**Before (speed 220):**
```
Camera sees line → Python calculates → Sends "F:220" → Arduino runs motors at 220
```

**After (speed 255):**
```
Camera sees line → Python calculates → Sends "F:255" → Arduino runs motors at 255 (FASTER!)
```

The Arduino code doesn't change - it just receives different numbers!

## What Each Setting Does

### config.yaml Settings:

```yaml
camera:
  device_id: 0       # Which camera to use
  width: 640         # Camera resolution
  height: 480
  fps: 30           # Frames per second

lane_detection:
  threshold: 60      # How to detect black line (Python uses this)
  min_confidence: 0.3 # When to trust detection (Python uses this)

arduino:
  port: "/dev/ttyUSB0"  # Where Arduino is connected
  baudrate: 9600        # Communication speed
  max_speed: 220        # Motor speed (Python sends this to Arduino)

pid:
  kp: 0.5            # Steering sensitivity (Python uses this)
  kd: 0.1            # Steering smoothness (Python uses this)
```

**Key Point:**
- config.yaml is ONLY read by Python
- Arduino receives the RESULTS (commands with numbers)
- Arduino doesn't know config.yaml exists!

## Communication Protocol

### Python → Arduino Commands:

```
Command Format      What It Means              Arduino Action
───────────────────────────────────────────────────────────────
F:220\n            Forward at speed 220        Both motors forward, PWM=220
L:15:220\n         Left turn 15°, speed 220    Left slower, right 220
R:15:220\n         Right turn 15°, speed 220   Right slower, left 220
S\n                Stop                        Both motors off
```

### Where Numbers Come From:

```
F:220 ──┬──> F = Python decides (based on line detection)
        └──> 220 = From config.yaml max_speed

L:15:220 ─┬─> L = Python decides (line is right of center)
          ├─> 15 = Python calculates (steering angle)
          └─> 220 = From config.yaml max_speed
```

## Complete Flow Example

**Scenario: Vehicle following a line**

```
1. Camera captures frame
   └─> Python (using camera settings from config.yaml)

2. Python detects line is 50 pixels right of center
   └─> Uses threshold from config.yaml

3. Python calculates: "Need to turn left 10 degrees"
   └─> Uses PID settings from config.yaml

4. Python creates command: "L:10:220"
   └─> 220 comes from max_speed in config.yaml

5. Python sends "L:10:220\n" via serial
   └─> Uses port from config.yaml

6. Arduino receives bytes: L:10:220\n

7. Arduino parses:
   - Command: L (left turn)
   - Angle: 10
   - Speed: 220

8. Arduino executes:
   leftSpeed = map(10, 0, 45, 220, 110)  // Reduce left motor
   analogWrite(LEFT_ENABLE, 110)
   analogWrite(RIGHT_ENABLE, 220)
   digitalWrite(both motors FORWARD)

9. Motors turn → Vehicle turns left

10. Repeat from step 1
```

## Why Two Separate Programs?

**Python (Computer):**
- ✓ Can use camera (needs USB, lots of processing)
- ✓ Can do complex math (line detection, PID)
- ✓ Easy to configure (config.yaml)
- ✗ Can't directly control motors (no high-current pins)

**Arduino:**
- ✓ Can control motors (PWM pins, real-time)
- ✓ Can handle high-speed commands (no lag)
- ✓ Dedicated hardware
- ✗ Can't easily process camera video
- ✗ Limited processing power

**Together:** Perfect team! 🤝

## How to Make Changes

### Want faster motors?
→ Edit config.yaml max_speed: 255
→ Restart Python (main.py)
→ Arduino automatically gets new speed values

### Want better line detection?
→ Edit config.yaml threshold: 50
→ Restart Python
→ Arduino doesn't need to change

### Want to change motor wiring?
→ Edit Arduino code (.ino file)
→ Re-upload to Arduino
→ Python doesn't need to change

## Summary

```
┌─────────────┐
│ config.yaml │ ← YOU edit this for settings
└──────┬──────┘
       ↓ read by
┌─────────────┐
│  Python     │ ← Runs on computer, uses camera
│  (main.py)  │   Reads config, sends commands
└──────┬──────┘
       ↓ sends serial commands
┌─────────────┐
│  Arduino    │ ← Runs on Arduino board
│  (.ino)     │   Receives commands, controls motors
└──────┬──────┘
       ↓ controls
┌─────────────┐
│   Motors    │ ← Move the vehicle
└─────────────┘
```

**Think of it like:**
- config.yaml = Settings file
- Python = Brain (sees, thinks, decides)
- Arduino = Muscles (receives orders, moves motors)
- USB cable = Nervous system (communication)
