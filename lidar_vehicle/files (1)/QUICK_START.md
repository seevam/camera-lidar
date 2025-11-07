# LiDAR Vehicle - Quick Start Guide

## Overview
This guide will help you get your LiDAR-based autonomous vehicle up and running in **4 simple steps**.

---

## Step 1: Hardware Assembly (30 minutes)

### What You Need
- [ ] Arduino Mega 2560 or ESP32
- [ ] RPLiDAR A1/A2 or Ydlidar X4
- [ ] L298N Motor Driver
- [ ] 2x DC Motors (with chassis)
- [ ] 7.4V - 12V Battery
- [ ] Jumper wires
- [ ] USB cable

### Wiring Diagram

```
┌─────────────────┐
│   ARDUINO MEGA  │
│                 │
│  RX1 ←──── TX   │──┐
│  TX1 ────→ RX   │  │   ┌──────────┐
│                 │  └───│  LIDAR   │
│  Pin 12 ──PWM───│──────│  Motor   │
│                 │      └──────────┘
│  Pin 5 ────→ IN1│──┐
│  Pin 6 ────→ IN2│  │   ┌──────────┐
│  Pin 3 ──PWM→ENA│  ├───│ L298N    │
│  Pin 9 ────→ IN3│  │   │  Motor   │
│  Pin 10 ───→ IN4│  │   │  Driver  │
│  Pin 11 ─PWM→ENB│──┘   └──────────┘
│                 │           │
│  5V  ────────────│───────────┼─────→ Logic Power
│  GND ────────────│───────────┴─────→ Ground
└─────────────────┘

Battery (7.4V - 12V) ───→ Motor Driver Power
                     └──→ Motors
```

### Connection Checklist
- [ ] LiDAR TX → Arduino RX1 (Pin 19)
- [ ] LiDAR RX → Arduino TX1 (Pin 18)
- [ ] LiDAR Motor → Arduino Pin 12
- [ ] LiDAR VCC → 5V
- [ ] LiDAR GND → GND
- [ ] Motor driver connected to pins 3, 5, 6, 9, 10, 11
- [ ] Battery connected to motor driver
- [ ] All grounds connected together

---

## Step 2: Software Setup (15 minutes)

### Arduino IDE

1. **Install Arduino IDE**
   - Download: https://www.arduino.cc/en/software
   - Install for your operating system

2. **Install Libraries**
   ```
   Arduino IDE → Tools → Manage Libraries
   
   Search and Install:
   - RPLidar (by RoboPeak)
   ```

3. **Upload Test Code**
   - Open `test_calibration.ino`
   - Select Board: Tools → Board → Arduino Mega 2560
   - Select Port: Tools → Port → COM3 (or /dev/ttyUSB0)
   - Click Upload ⬆
   - Open Serial Monitor (115200 baud)

4. **Run Hardware Tests**
   ```
   Press '1' - Test motors (each motor should spin)
   Press '2' - Test LiDAR (should see distance readings)
   Press '3' - Calibrate balance (vehicle drives straight)
   Press '4' - Test full system
   ```

### Python Setup

1. **Install Python** (3.7 or higher)
   - Windows: https://www.python.org/downloads/
   - Linux: `sudo apt install python3 python3-pip`
   - Mac: `brew install python3`

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Test Connection**
   ```bash
   python lidar_data_collector.py --mode manual
   ```

---

## Step 3: First Test Run (10 minutes)

### Prepare Test Environment

1. **Create Test Track**
   - Width: 50-100 cm
   - Length: 2-3 meters
   - Use walls or barriers for LiDAR to follow
   - Place 5-10 small obstacles

2. **Set Lighting**
   - **Bright**: Natural daylight or bright lamps
   - **Medium**: Normal office lighting
   - **Low**: Dim lights (but not complete darkness)

### Run First Trial

1. **Position Vehicle**
   - Place at start of track
   - Ensure clear path ahead
   - Verify LiDAR is spinning

2. **Start Test**
   ```bash
   python lidar_data_collector.py --mode manual
   
   # In the prompt:
   start bright
   
   # Let it run for 2 minutes
   # It will automatically stop and save data
   ```

3. **Check Results**
   - Data saved in `data/raw/lidar_bright_TIMESTAMP.csv`
   - Review serial output for any errors
   - Note collision count

---

## Step 4: Full Testing & Analysis (45 minutes)

### Run All Conditions

**Option A: Automated (Recommended)**
```bash
python lidar_data_collector.py --mode auto --duration 120
```
This will automatically run bright, medium, and low light tests.

**Option B: Manual**
```bash
python lidar_data_collector.py --mode manual

# Run each condition:
start bright   # Wait 2 minutes
start medium   # Wait 2 minutes  
start low      # Wait 2 minutes
quit
```

### Analyze Results

```bash
python analyze_performance.py
```

This generates:
- `data/analysis/comparison_table.csv` - Metrics table
- `data/analysis/performance_comparison.png` - Graphs
- `data/analysis/analysis_report.txt` - Full report
- `data/analysis/results.json` - Raw data

### Interpret Results

**Key Metrics to Check:**

1. **CPS (Composite Performance Score)**
   - Lower is better
   - <20 = Excellent
   - 20-40 = Good
   - 40-60 = Fair
   - >60 = Needs improvement

2. **Collisions**
   - 0-2 = Excellent
   - 3-5 = Good
   - 6-8 = Fair
   - >8 = Poor

3. **RMSE (Path Deviation)**
   - <3 cm = Excellent
   - 3-5 cm = Good
   - 5-10 cm = Fair
   - >10 cm = Poor

---

## Troubleshooting

### Problem: LiDAR not spinning
**Solution:**
- Check power connection (5V, GND)
- Verify Pin 12 connection
- Check Serial Monitor for errors
- Try `analogWrite(LIDAR_MOTOR_PIN, 255);`

### Problem: Motors not moving
**Solution:**
- Check battery voltage (should be >7V)
- Verify all motor driver connections
- Test with `test_calibration.ino`
- Check enable pins (PWM pins 3 and 11)

### Problem: Vehicle goes in circles
**Solution:**
- Run motor balance calibration (test menu option 3)
- Adjust `LEFT_MOTOR_FACTOR` or `RIGHT_MOTOR_FACTOR` in `config.h`
- Check if wheels are same size

### Problem: No serial connection
**Solution:**
- Check COM port in Device Manager (Windows) or `ls /dev/tty*` (Linux)
- Try different USB cable
- Ensure Arduino drivers are installed
- Check baud rate (115200)

### Problem: Erratic LiDAR readings
**Solution:**
- Clean LiDAR lens with microfiber cloth
- Remove reflective surfaces from test area
- Check for loose wire connections
- Ensure stable power supply

---

## Tips for Best Results

### 1. Consistent Test Environment
- Use same track for all tests
- Same obstacle placement
- Measure light levels with phone app
- Minimize external interference

### 2. Data Quality
- Run 3 trials per condition
- Allow vehicle to warm up (1 minute)
- Don't interfere during tests
- Take notes of any anomalies

### 3. PID Tuning
- Start with default values
- If oscillating → reduce KP
- If slow response → increase KP
- If drift → add small KI (0.01)

### 4. Battery Management
- Always start with fully charged battery
- Check voltage before each trial
- Replace/recharge if <7.4V
- Use same battery for all tests

---

## Next Steps

### After successful basic testing:

1. **Compare with Camera System**
   - Run same tests with camera vehicle
   - Use identical track and conditions
   - Analyze both datasets together

2. **Advanced Experiments**
   - Add more obstacles
   - Test different speeds
   - Try curved tracks
   - Test in complete darkness

3. **Optimize Performance**
   - Fine-tune PID parameters
   - Adjust wall following distance
   - Improve obstacle detection
   - Add predictive algorithms

---

## Common Mistakes to Avoid

❌ **Don't:**
- Run tests with low battery
- Change track between conditions
- Interfere with vehicle during trials
- Test in complete darkness (low light ≠ no light)
- Mix data from different vehicles

✅ **Do:**
- Calibrate before testing
- Document all settings
- Run multiple trials
- Keep detailed notes
- Follow consistent procedure

---

## Need Help?

### Resources
1. **Documentation**: See `README.md` for detailed info
2. **Hardware**: Check wiring diagram carefully
3. **Software**: Review error messages in Serial Monitor
4. **Analysis**: Examine raw CSV files

### Debugging Steps
1. Run `test_calibration.ino` first
2. Test each component individually
3. Check Serial Monitor output
4. Verify all connections
5. Measure voltages with multimeter

---

## Success Checklist

Before running full tests, verify:
- [ ] All hardware connections secure
- [ ] LiDAR spinning and providing data
- [ ] Motors respond to commands
- [ ] Vehicle drives relatively straight
- [ ] Collision detection works
- [ ] Data saves to CSV correctly
- [ ] Python scripts run without errors
- [ ] Test environment prepared

---

## Estimated Timeline

| Task | Time |
|------|------|
| Hardware assembly | 30 min |
| Software setup | 15 min |
| Testing & calibration | 15 min |
| First trial run | 10 min |
| All condition tests | 30 min |
| Analysis | 15 min |
| **Total** | **~2 hours** |

---

## What Success Looks Like

After following this guide, you should have:
1. ✅ Working LiDAR vehicle that follows walls
2. ✅ Data from 3 lighting conditions
3. ✅ Analysis comparing all conditions
4. ✅ Graphs showing performance metrics
5. ✅ Understanding of LiDAR advantages

---

**Good luck with your testing! 🚗💨**

Remember: The goal is to compare camera vs LiDAR performance across different lighting conditions. LiDAR should maintain consistent performance regardless of light levels!
