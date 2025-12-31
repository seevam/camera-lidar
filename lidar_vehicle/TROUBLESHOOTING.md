# RPLiDAR Robot Troubleshooting Guide

## Critical Fix Applied

### The Problem
Your original code was **missing the RPLiDAR motor control pin**. The RPLiDAR won't spin without a PWM signal to its motor control wire.

### The Solution
Added these critical lines:
```cpp
#define RPLIDAR_MOTOR 3        // PWM pin to control LiDAR motor
pinMode(RPLIDAR_MOTOR, OUTPUT);
analogWrite(RPLIDAR_MOTOR, 255);  // Full speed
```

---

## RPLiDAR Wiring (CRITICAL!)

Your RPLiDAR A1/A2 should be connected as follows:

### RPLiDAR to Arduino Mega:
| RPLiDAR Wire | Color (typical) | Arduino Mega Pin | Purpose |
|--------------|-----------------|------------------|---------|
| GND          | Black           | GND              | Ground |
| 5V           | Red             | 5V               | Power (needs 2A!) |
| TX           | White           | RX1 (Pin 19)     | Data from LiDAR |
| RX           | Green           | TX1 (Pin 18)     | Data to LiDAR |
| MOTOR        | Orange/Yellow   | **Pin 3** (PWM)  | **Motor control** |

### **⚠️ MOST COMMON MISTAKE:**
The **MOTOR control wire (orange/yellow) must be connected to a PWM pin (Pin 3)** and driven HIGH to make the LiDAR spin!

---

## Motor Driver Wiring

Based on your code, your motor driver connections are:

### Arduino to Motor Driver:
| Function        | Arduino Pin | Motor Driver Pin |
|-----------------|-------------|------------------|
| Right Motor PWM | 9 (ENA)     | ENA              |
| Right Motor Dir | 7 (IN1)     | IN1              |
| Right Motor Dir | 8 (IN2)     | IN2              |
| Left Motor PWM  | 10 (ENB)    | ENB              |
| Left Motor Dir  | 5 (IN3)     | IN3              |
| Left Motor Dir  | 6 (IN4)     | IN4              |

### Motor Driver to Motors:
- OUT1 & OUT2 → Right Motor
- OUT3 & OUT4 → Left Motor

---

## Diagnostic Steps

### 1. Upload the Fixed Code
Upload `lidar_fixed.ino` to your Arduino Mega.

### 2. Open Serial Monitor
- Set baud rate to **115200**
- You should see startup messages

### 3. Check for These Messages:

#### ✅ Good - System Starting:
```
========================================
RPLiDAR OBSTACLE AVOIDANCE - STARTING
========================================

1. Motor pins configured
2. Motors stopped
3. Serial1 initialized at 115200 baud
4. LiDAR interface initialized
5. LiDAR motor started (PWM=255)
   >> MOTOR SHOULD BE SPINNING NOW <<
6. Scan mode started
```

#### ✅ Good - LiDAR Working:
```
*** LiDAR DATA DETECTED - SYSTEM ACTIVE ***

Rotation #1 | Valid points: 360 | F: 1250mm, L: 890mm, R: 1340mm
```

#### ❌ Bad - No Data:
```
WARNING: No LiDAR data received!
Check connections:
  - RX1 (pin 19) -> LiDAR TX (white)
  - TX1 (pin 18) -> LiDAR RX (green)
  - Pin 3 -> LiDAR MOTOR (orange/yellow)
  - 5V -> LiDAR 5V (red)
  - GND -> LiDAR GND (black)
```

---

## Common Problems & Solutions

### Problem 1: LiDAR Motor Not Spinning
**Symptoms:** No rotation, no data

**Checks:**
1. ✅ Is the orange/yellow MOTOR wire connected to Arduino Pin 3?
2. ✅ Is Pin 3 a PWM-capable pin? (Yes, it is)
3. ✅ Is the LiDAR getting 5V power with at least 2A?
4. ✅ Check the code has:
   ```cpp
   pinMode(RPLIDAR_MOTOR, OUTPUT);
   analogWrite(RPLIDAR_MOTOR, 255);
   ```

**Solution:** Connect MOTOR wire to Pin 3 and verify it's driven HIGH.

---

### Problem 2: No Serial Data
**Symptoms:** "WARNING: No LiDAR data received!"

**Checks:**
1. ✅ TX1/RX1 connections correct?
   - LiDAR TX (white) → Arduino RX1 (Pin 19)
   - LiDAR RX (green) → Arduino TX1 (Pin 18)
2. ✅ Baud rate is 115200 in code and Serial Monitor
3. ✅ LiDAR is powered (LED should be on)

**Solution:** Double-check UART connections. Try swapping TX/RX if still no data.

---

### Problem 3: Motors Not Working
**Symptoms:** LiDAR works but vehicle doesn't move

**Checks:**
1. ✅ Motor driver is powered (separate battery/power source)
2. ✅ Motor driver GND is connected to Arduino GND (common ground!)
3. ✅ Correct pins defined in code
4. ✅ Motor power switch is ON

**Test Motors Manually:**
Add this to your code temporarily:
```cpp
void testMotors() {
  Serial.println("Testing RIGHT motor forward...");
  digitalWrite(IN1, HIGH);
  digitalWrite(IN2, LOW);
  analogWrite(ENA, 150);
  delay(2000);

  Serial.println("Testing LEFT motor forward...");
  digitalWrite(IN3, HIGH);
  digitalWrite(IN4, LOW);
  analogWrite(ENB, 150);
  delay(2000);

  stopMotors();
}
```

---

### Problem 4: Vehicle Turns Wrong Direction
**Symptoms:** Turns left instead of right

**Solution:** Swap motor wires or modify the `turnRight()` function:
```cpp
void turnRight() {
  // Try this if it turns the wrong way:
  digitalWrite(IN1, HIGH);  // Changed
  digitalWrite(IN2, LOW);   // Changed
  analogWrite(ENA, TURN_SPEED);

  digitalWrite(IN3, LOW);   // Changed
  digitalWrite(IN4, HIGH);  // Changed
  analogWrite(ENB, TURN_SPEED);
}
```

---

### Problem 5: Poor Obstacle Detection
**Symptoms:** Crashes into walls or doesn't turn

**Adjustments:**
```cpp
#define MIN_DISTANCE 500   // Increase to detect farther
#define BASE_SPEED 100     // Reduce for more control
#define TURN_SPEED 100     // Reduce for gentler turns
```

---

## Power Requirements

### Critical Power Specifications:
1. **RPLiDAR:** 5V, up to 2A (especially during motor startup)
2. **Arduino Mega:** 7-12V via barrel jack OR 5V via USB
3. **Motors:** Depends on your motors (typically 3-12V, 1-2A each)

### Recommended Power Setup:
- **Option 1:** Single 7.4V LiPo battery
  - Battery → Motor Driver (7.4V input)
  - Motor Driver 5V output → Arduino 5V pin
  - Arduino 5V pin → RPLiDAR 5V

- **Option 2:** Separate power sources
  - Power bank (5V, 2A+) → Arduino VIN and RPLiDAR
  - Battery pack (7-12V) → Motor Driver only
  - **IMPORTANT:** Connect all GNDs together!

---

## Testing Procedure

### Step 1: Test LiDAR Only
1. Upload code
2. Open Serial Monitor (115200 baud)
3. Watch for "LiDAR motor started" message
4. **Listen for motor spinning sound**
5. Wait for "LiDAR DATA DETECTED" message
6. Check distance readings in diagnostics

### Step 2: Test Motors Only
1. Comment out obstacle avoidance
2. Call `moveForward()` directly
3. Verify both motors spin correctly
4. Test `turnRight()` and `turnLeft()`

### Step 3: Full System Test
1. Uncomment all code
2. Place robot in open area
3. Place obstacle in front
4. Verify it detects and turns

---

## Hardware Checklist

Before asking for help, verify:

- [ ] RPLiDAR motor wire connected to Pin 3
- [ ] RPLiDAR TX → Arduino RX1 (Pin 19)
- [ ] RPLiDAR RX → Arduino TX1 (Pin 18)
- [ ] RPLiDAR 5V and GND connected
- [ ] Motor driver IN1-IN4 connected to correct pins
- [ ] Motor driver ENA, ENB connected to PWM pins
- [ ] All GNDs connected together (common ground)
- [ ] Separate power for motors (not USB power!)
- [ ] LiDAR spinning when powered
- [ ] Serial Monitor shows data reception
- [ ] Motors respond to forward/turn commands

---

## Advanced Debugging

### Enable Verbose Diagnostics:
Modify the code to print every single point:
```cpp
if (quality > 0 && distance > 0) {
  Serial.print("Angle: ");
  Serial.print(angle);
  Serial.print("° Distance: ");
  Serial.print(distance);
  Serial.print("mm Quality: ");
  Serial.println(quality);
}
```

### Test LiDAR Communication:
```cpp
void testLidarHealth() {
  rplidar_response_device_health_t health;
  if (IS_OK(lidar.getHealth(health))) {
    Serial.print("LiDAR Health: ");
    Serial.println(health.status == 0 ? "GOOD" : "WARNING");
  } else {
    Serial.println("Cannot get health - check connections!");
  }
}
```

---

## Next Steps

1. **Upload `lidar_fixed.ino`** to your Arduino Mega
2. **Open Serial Monitor** at 115200 baud
3. **Verify LiDAR motor is spinning** (you should hear it)
4. **Watch for diagnostic messages** showing distance readings
5. **Test in open space** first before confined areas

If you still have issues after trying these steps, report:
- Exact messages from Serial Monitor
- Photo of your wiring connections
- Which step in the checklist failed

Good luck! 🚗
