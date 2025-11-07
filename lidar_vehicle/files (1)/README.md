# LiDAR-Based Autonomous Vehicle Testing System

## Project Overview

This system implements a LiDAR-based autonomous vehicle for comparing performance against camera-based systems under different lighting conditions.

### Research Objectives
1. **Investigate AV performance** under different light conditions
2. **Compare Camera-based** (Tesla approach) vs **LiDAR-based** (Waymo approach)
3. **Evaluate under three conditions**: Bright, Medium, and Low light

---

## Hardware Requirements

### Essential Components
1. **Microcontroller**: 
   - Arduino Mega 2560 / ESP32 DevKit
   - USB cable for programming

2. **LiDAR Sensor**:
   - **Recommended**: Ydlidar X4, RPLiDAR A1, or RPLiDAR A2
   - 360° scanning capability
   - 5-12m range
   - Serial/UART interface

3. **Motor System**:
   - 2x DC motors (with encoders preferred)
   - Motor driver: L298N or TB6612FNG
   - Chassis with wheels
   - Battery: 7.4V - 12V Li-Po/Li-Ion

4. **Additional**:
   - Bluetooth module HC-05 (optional, for wireless monitoring)
   - Breadboard and jumper wires
   - Power supply/batteries

### Hardware Connections

```
LIDAR (RPLiDAR A1/A2):
  - VCC → 5V
  - GND → GND
  - TX → Arduino RX1 (Pin 19)
  - RX → Arduino TX1 (Pin 18)
  - Motor PWM → Pin 12

MOTOR DRIVER (L298N):
  - IN1 → Pin 5  (Left Motor Forward)
  - IN2 → Pin 6  (Left Motor Backward)
  - IN3 → Pin 9  (Right Motor Forward)
  - IN4 → Pin 10 (Right Motor Backward)
  - ENA → Pin 3  (Left Motor Speed - PWM)
  - ENB → Pin 11 (Right Motor Speed - PWM)
  - Motor Power: 7.4V - 12V
  - Logic Power: 5V from Arduino

BLUETOOTH HC-05 (Optional):
  - VCC → 5V
  - GND → GND
  - TX → Pin 16 (RX2)
  - RX → Pin 17 (TX2)
```

---

## Software Setup

### 1. Arduino IDE Setup

#### Install Arduino IDE
Download from: https://www.arduino.cc/en/software

#### Install Required Libraries
In Arduino IDE, go to: **Tools → Manage Libraries**

Install the following:
1. **RPLidar** by RoboPeak
   - For RPLiDAR A1/A2 sensors
   
2. **Ydlidar** (if using Ydlidar X4)
   - May need to download from manufacturer

#### Upload Code to Arduino
1. Open `lidar_vehicle_main.ino` in Arduino IDE
2. Select your board: **Tools → Board → Arduino Mega 2560** (or ESP32)
3. Select port: **Tools → Port → COM3** (or /dev/ttyUSB0 on Linux)
4. Click **Upload** button
5. Open Serial Monitor: **Tools → Serial Monitor** (115200 baud)

### 2. Python Environment Setup

#### Install Python Dependencies
```bash
# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install requirements
pip install -r requirements.txt
```

#### Verify Installation
```bash
python -c "import serial, pandas, matplotlib; print('All dependencies installed!')"
```

---

## Project Structure

```
lidar-av-testing/
├── lidar_vehicle_main.ino       # Arduino code for vehicle
├── lidar_data_collector.py      # Python data collection script
├── analyze_performance.py       # Analysis and comparison script
├── requirements.txt             # Python dependencies
├── README.md                    # This file
│
├── data/
│   ├── raw/                     # Raw CSV data from trials
│   │   ├── camera_bright_*.csv
│   │   ├── camera_medium_*.csv
│   │   ├── camera_low_*.csv
│   │   ├── lidar_bright_*.csv
│   │   ├── lidar_medium_*.csv
│   │   └── lidar_low_*.csv
│   │
│   └── analysis/                # Analysis outputs
│       ├── comparison_table.csv
│       ├── performance_comparison.png
│       ├── analysis_report.txt
│       └── results.json
│
└── docs/
    └── hardware_setup.pdf       # Detailed hardware guide
```

---

## Usage Guide

### Quick Start

1. **Hardware Setup**
   - Assemble vehicle with LiDAR mounted on top
   - Connect all components as per wiring diagram
   - Power on and upload Arduino code
   - Verify LiDAR is spinning and Serial Monitor shows output

2. **Test Environment Setup**
   - Create test track with:
     - Black line on white surface (or walls for LiDAR to follow)
     - Width: 50-100cm
     - 10 obstacles placed along track
   - Set up lighting for each condition

3. **Run Data Collection**

#### Automated Testing (Recommended)
```bash
# Connect Arduino to computer
python lidar_data_collector.py --mode auto --duration 120

# This will automatically run:
# - Bright light trial (2 minutes)
# - Medium light trial (2 minutes)  
# - Low light trial (2 minutes)
```

#### Manual Testing
```bash
python lidar_data_collector.py --mode manual

# Then in the prompt:
start bright    # Start bright light trial
stop           # Stop trial
start medium   # Start medium light trial
stop
start low      # Start low light trial
stop
quit           # Exit
```

4. **Analyze Results**
```bash
python analyze_performance.py
```

This will generate:
- Comparison table (CSV)
- Performance graphs (PNG)
- Detailed report (TXT)
- JSON data for further analysis

---

## Metrics Explained

### Primary Metrics

1. **RMSE (Root Mean Square Error)**
   - Measures average path deviation in cm
   - Lower is better
   - Formula: √(Σ(deviation²) / n)

2. **Total Collisions**
   - Number of obstacle hits during trial
   - Zero is ideal

### Scoring System (0-100, lower is better)

1. **PDS (Path Deviation Score)**
   - Based on RMSE
   - PDS = (RMSE / 10) × 100
   - Weight: 40% of CPS

2. **OCS (Obstacle Collision Score)**
   - Based on collision count
   - OCS = (Collisions / 10) × 100
   - Weight: 35% of CPS

3. **ODS (Obstacle Displacement Score)**
   - Based on how far vehicle penetrated obstacle
   - ODS = (Avg Displacement / 20) × 100
   - Weight: 25% of CPS

4. **CPS (Composite Performance Score)**
   - Overall performance metric
   - CPS = 0.4×PDS + 0.35×OCS + 0.25×ODS
   - Lower score = better performance

---

## Troubleshooting

### LiDAR Issues

**Problem**: LiDAR not spinning
- Check motor control pin (should output PWM)
- Verify power supply (5V, sufficient current)
- Check wiring connections

**Problem**: No data from LiDAR
- Verify serial connection (RX/TX not swapped)
- Check baud rate (115200 for RPLiDAR)
- Ensure LiDAR is powered on

**Problem**: Erratic readings
- Clean LiDAR lens
- Remove reflective surfaces from test area
- Check for loose connections

### Motor Issues

**Problem**: Motors not moving
- Check motor driver connections
- Verify PWM pins are correct
- Test with simple motor test sketch
- Check battery voltage (should be >7V)

**Problem**: Uneven movement
- Calibrate motor speeds in code
- Check if wheels are same size
- Verify both motors receive same PWM signal

### Communication Issues

**Problem**: Can't connect to Arduino
- Check COM port in Device Manager (Windows) or `ls /dev/tty*` (Linux)
- Ensure no other program is using the port
- Try unplugging and replugging USB
- Check USB cable (some are power-only)

**Problem**: Garbled serial data
- Verify baud rate matches (115200)
- Check for loose serial connections
- Reduce serial transmission rate

---

## Testing Protocol

### Standard Test Procedure

1. **Pre-Test**
   - Charge all batteries fully
   - Clean LiDAR lens
   - Verify all connections
   - Test run without data collection

2. **Test Environment**
   - **Bright**: Natural daylight or 1000+ lux
   - **Medium**: Office lighting, 300-500 lux
   - **Low**: Dimmed lights, <100 lux
   - Measure with light meter for consistency

3. **Trial Execution**
   - Position vehicle at start point
   - Start data collection
   - Let vehicle run for 2 minutes
   - Do not interfere unless safety issue
   - Record any anomalies

4. **Post-Test**
   - Save data files with clear naming
   - Note any hardware issues
   - Recharge batteries before next trial

5. **Repetition**
   - Run 3 trials per condition for statistical validity
   - Use same track and obstacles
   - Maintain consistent lighting

---

## Data Format

### Raw Data CSV Format

```csv
timestamp,deviation_mm,cumulative_collisions,light_condition,sensor_type
1000,45,0,bright,lidar
2000,-32,0,bright,lidar
3000,67,1,bright,lidar
...
```

- **timestamp**: Milliseconds since trial start
- **deviation_mm**: Distance from ideal path in mm (+ right, - left)
- **cumulative_collisions**: Total collisions up to this point
- **light_condition**: bright/medium/low
- **sensor_type**: camera/lidar

---

## Expected Results

### Hypothesis

**Camera System:**
- Good performance in bright light
- Degraded performance in medium light  
- Poor performance in low light
- High light dependency

**LiDAR System:**
- Consistent performance across all conditions
- No light dependency
- Better obstacle detection
- More reliable path following

### Key Comparisons

Compare CPS scores:
- Lower CPS = better performance
- Look for trends across light conditions
- Statistical significance if difference >10 points

---

## Advanced Features

### Tuning PID Parameters

In `lidar_vehicle_main.ino`, adjust:
```cpp
#define KP 0.5  // Proportional gain
#define KI 0.0  // Integral gain  
#define KD 0.3  // Derivative gain
```

**Effects:**
- Increase KP: Faster response, may oscillate
- Increase KI: Eliminates steady-state error
- Increase KD: Dampens oscillation, smooths motion

### Custom Analysis

Use results.json for:
```python
import json
import pandas as pd

with open('data/analysis/results.json') as f:
    results = json.load(f)

# Custom analysis here
camera_bright_cps = results['camera']['bright']['cps']
lidar_bright_cps = results['lidar']['bright']['cps']
improvement = ((camera_bright_cps - lidar_bright_cps) / camera_bright_cps) * 100
print(f"LiDAR improved by {improvement:.1f}%")
```

---

## Safety Notes

1. **Electrical Safety**
   - Don't exceed voltage ratings
   - Watch for shorts when wiring
   - Use proper gauge wires for current

2. **Mechanical Safety**
   - Secure all components to prevent detachment
   - Keep fingers away from spinning LiDAR
   - Use emergency stop if needed

3. **LiDAR Safety**
   - Class 1 laser (safe for eyes, but don't stare directly)
   - Ensure protective cover is intact
   - Keep lens clean

---

## Contributing

### Reporting Issues
- Include hardware setup details
- Provide serial monitor output
- Describe exact steps to reproduce

### Improvements
- Fork the repository
- Create feature branch
- Submit pull request with description

---

## References

### Hardware
- RPLiDAR documentation: https://www.slamtec.com/
- Ydlidar documentation: http://www.ydlidar.com/
- L298N datasheet: https://www.sparkfun.com/datasheets/Robotics/L298_H_Bridge.pdf

### Related Work
- Tesla Autopilot (Camera-based): https://www.tesla.com/autopilot
- Waymo (LiDAR-based): https://waymo.com/technology/
- Elektor LiDAR Vehicle: https://github.com/ClemensAtElektor/Lidar-controlled-autonomous-vehicle

---

## License

This project is for educational purposes. 
Hardware designs and code are provided as-is.

---

## Support

For questions or issues:
1. Check Troubleshooting section
2. Review serial monitor output
3. Test with simple examples first
4. Document your setup completely

---

## Acknowledgments

- Inspired by Tesla (camera) and Waymo (LiDAR) AV approaches
- Based on research in autonomous vehicle sensing
- Uses open-source libraries: RPLidar, Arduino

---

**Last Updated**: October 2025
**Version**: 1.0
