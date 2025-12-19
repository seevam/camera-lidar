# Camera Vehicle - Testing Guide

## Quick Start: Testing Camera in Different Lighting Conditions

### 1. Camera Lighting Test (Python)

The easiest way to test your camera and see output in different lighting conditions:

```bash
cd /home/user/camera-lidar/camer-vehicle/test
python3 test_camera_lighting.py
```

**Features:**
- Live camera feed with lighting analysis
- Real-time brightness, contrast, and histogram display
- Multiple enhancement modes for different lighting
- Visual indicators for lighting conditions

**Controls:**
- `Q` or `ESC` - Quit
- `S` - Save current frame
- `0` - No enhancement
- `1` - Brightness adjustment (CLAHE) - Best for dark conditions
- `2` - Contrast enhancement - Best for flat/washed out lighting
- `3` - Adaptive equalization - Best for mixed lighting
- `SPACE` - Print current metrics to console

**Lighting Condition Indicators:**
- **Red** - Very Dark (< 50 brightness)
- **Orange** - Dark (50-100)
- **Green** - Good (100-150)
- **Yellow** - Bright (150-200)
- **White** - Very Bright (> 200)

### 2. Testing Complete System

Once you've verified the camera works, test the complete autonomous system:

```bash
cd /home/user/camera-lidar/camer-vehicle/src
python3 main.py
```

Make sure:
1. Arduino is connected and uploaded with the code
2. Camera is connected
3. config.yaml has correct Arduino port

### 3. Arduino Setup

#### Option A: Basic Version (Current)
Upload `camera_vehicle.ino` - Simple motor control only

#### Option B: Enhanced Version (Recommended)
Upload `camera_vehicle_enhanced.ino` - Includes diagnostics and LED indicators

**Enhanced Version Features:**
- Built-in LED (pin 13) - System status
- LED pin 12 - Line detected indicator
- LED pin 11 - Warning indicator (command timeout)
- Serial diagnostic commands
- Motor test routines

**Enhanced Arduino Commands:**
```
HELP   - Show all commands
STATUS - Show system status
TEST   - Run diagnostic test (motors and LEDs)
RESET  - Reset statistics
D      - Toggle diagnostic mode
```

### 4. Hardware Setup

**Arduino Connections:**
- Pins 2-5: Motor direction control
- Pins 9-10: Motor speed (PWM)
- Pin 13: Status LED (built-in)
- Pin 12: Line detect LED (optional, external)
- Pin 11: Warning LED (optional, external)

**Camera:**
- USB camera connected to computer/Raspberry Pi
- Default camera ID: 0 (change in config.yaml if needed)

## Testing Different Lighting Conditions

### Test Scenarios

1. **Bright Sunlight**
   - Run test_camera_lighting.py
   - Should show "Very Bright" or "Bright"
   - Try enhancement mode 2 (contrast) if washed out

2. **Indoor Lighting**
   - Should show "Good"
   - Usually best performance

3. **Low Light / Evening**
   - Will show "Dark" or "Very Dark"
   - Use enhancement mode 1 (CLAHE brightness)
   - May need to adjust `threshold` in config.yaml

4. **Mixed Lighting (shadows/sun)**
   - Use enhancement mode 3 (adaptive)
   - Check contrast level

### Adjusting for Lighting

Edit `config.yaml` to tune for your lighting:

```yaml
lane_detection:
  threshold: 60  # Lower for darker lines, higher for lighter
  roi_top_percent: 0.6
  min_contour_area: 500
  min_confidence: 0.3

camera:
  device_id: 0
  width: 640
  height: 480
  fps: 30
```

**Threshold Guide:**
- Very bright: 80-100
- Normal: 60-80
- Dark: 40-60
- Very dark: 20-40

## Troubleshooting

### Camera Not Opening
```bash
# Check available cameras
ls /dev/video*

# Test with different camera ID
python3 test_camera_lighting.py 1
```

### No Video Display
- Make sure you have a display/X11 available
- For headless systems, install X11 forwarding or VNC
- Check OpenCV installation: `pip3 install opencv-python`

### Arduino Not Responding
1. Check port in config.yaml matches your Arduino:
   ```bash
   # Linux
   ls /dev/ttyUSB* /dev/ttyACM*

   # Update config.yaml with correct port
   ```

2. Test Arduino separately:
   - Open Arduino Serial Monitor
   - Type: `HELP` and press enter
   - Should see help menu (if using enhanced version)

### Line Not Detected
1. Use test_camera_lighting.py to see what camera sees
2. Adjust threshold in config.yaml
3. Ensure good contrast between line and background
4. Check ROI settings (roi_top_percent)

## File Structure

```
camer-vehicle/
├── arduino/
│   ├── camera_vehicle.ino          # Basic version
│   └── camera_vehicle_enhanced.ino # Enhanced with diagnostics
├── src/
│   ├── main.py                     # Main autonomous control
│   ├── camera_controller.py        # Camera interface
│   ├── lane_detector.py            # Line detection
│   ├── motor_controller.py         # Arduino communication
│   ├── pid_controller.py           # PID control (NEW)
│   └── data_logger.py              # Data logging (NEW)
├── test/
│   ├── test_camera_lighting.py     # Camera test tool (NEW)
│   └── test_lane_detection.py      # Lane detection test
└── config.yaml                     # Configuration file
```

## Tips for Best Results

1. **Lighting**: Consistent, diffuse lighting works best
2. **Line**: High contrast (black line on white surface or vice versa)
3. **Line Width**: 2-5cm wide works well
4. **Surface**: Matte surface reduces glare
5. **Camera Height**: 20-40cm above surface
6. **Camera Angle**: Slight downward angle (~30-45°)

## Next Steps

1. Test camera with test_camera_lighting.py
2. Identify your lighting condition
3. Adjust config.yaml threshold if needed
4. Upload enhanced Arduino code
5. Run full system with main.py
6. Monitor logs in data/logs/

Good luck with your testing!
