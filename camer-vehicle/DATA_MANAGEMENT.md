# Trial Data Management Guide

## What is Trial Data?

When you run your camera vehicle (`python3 src/main.py`), it automatically logs data to help you analyze performance and improve your setup.

## Where is Data Stored?

```
data/logs/
├── frames_20251220_143022.csv      # Frame-by-frame tracking data
├── events_20251220_143022.txt      # Event log (line lost, etc.)
└── summary_20251220_143022.json    # Session summary statistics
```

Each session creates 3 files with timestamp `YYYYMMDD_HHMMSS`.

## What's in Each File?

### 1. Frames CSV (`frames_*.csv`)
Detailed data for every frame:
- `frame_number` - Frame counter
- `timestamp` - Unix timestamp
- `error_px` - How far off-center the line is (pixels)
- `steering_angle` - Commanded steering angle (degrees)
- `confidence` - How confident the detection is (0-1)
- `line_detected` - Boolean, was line found?

**Use for:**
- Analyzing tracking performance
- Tuning PID parameters
- Identifying problem areas on your track

### 2. Events Log (`events_*.txt`)
Text log of important events:
```
[2025-12-20 14:30:22.123] line_lost
[2025-12-20 14:30:45.456] sharp_turn: {"angle": 35}
```

**Use for:**
- Understanding what went wrong
- Debugging unexpected behavior
- Tracking specific incidents

### 3. Summary JSON (`summary_*.json`)
Overall session statistics:
```json
{
  "session_id": "20251220_143022",
  "duration_seconds": 45.2,
  "total_frames": 1356,
  "frames_with_line": 1320,
  "line_detection_rate": 0.973,
  "average_error_px": 12.5,
  "max_error_px": 45.8
}
```

**Use for:**
- Quick performance overview
- Comparing different trials
- Tracking improvement over time

## How to Analyze Trial Data

### Option 1: Use the Analysis Tool (Recommended)

```bash
cd /home/user/camera-lidar/camer-vehicle/tools
python3 analyze_trial_data.py
```

**Features:**
- List all sessions
- View summary statistics
- Plot error, steering, and confidence graphs
- Compare multiple sessions
- Export to CSV for Excel
- Clean up old logs

### Option 2: Manual Analysis

#### View Summary
```bash
cat data/logs/summary_20251220_143022.json | python3 -m json.tool
```

#### Check Latest Events
```bash
tail data/logs/events_20251220_143022.txt
```

#### Analyze in Python
```python
import pandas as pd
import matplotlib.pyplot as plt

# Load frame data
df = pd.read_csv('data/logs/frames_20251220_143022.csv')

# Plot tracking error over time
plt.plot(df['frame_number'], df['error_px'])
plt.xlabel('Frame')
plt.ylabel('Error (pixels)')
plt.title('Tracking Performance')
plt.show()

# Calculate statistics
print(f"Mean error: {df['error_px'].abs().mean():.2f} px")
print(f"Detection rate: {df['line_detected'].mean()*100:.1f}%")
```

#### Analyze in Excel/Sheets
The CSV files can be opened directly in Excel or Google Sheets.

## What to Do With Trial Data

### 1. **Tune Your PID Controller**

Look at the error and steering plots:
- **Oscillating wildly?** → Reduce `kp` (proportional gain)
- **Slow to respond?** → Increase `kp`
- **Overshooting?** → Increase `kd` (derivative gain)
- **Steady-state error?** → Increase `ki` (integral gain)

```bash
# Run analysis tool
python3 tools/analyze_trial_data.py

# Select option 3 to plot graphs
# Look for patterns in the steering response
```

### 2. **Improve Line Detection**

Check detection confidence:
- Low confidence areas? → Improve lighting or adjust threshold
- Frequent line loss? → Lower `min_confidence` threshold
- Too sensitive? → Increase `min_confidence`

### 3. **Compare Different Settings**

Run multiple trials with different configurations:

```bash
# Trial 1: Default settings
python3 src/main.py

# Trial 2: Adjust threshold in config.yaml
# threshold: 70 → 50
python3 src/main.py

# Compare
python3 tools/analyze_trial_data.py
# Select option 4 to compare sessions
```

### 4. **Track Improvement Over Time**

Keep logs to see your progress:
- Better detection rate?
- Lower average error?
- Faster lap times?

### 5. **Debug Problems**

When something goes wrong:

1. Check events log for what happened
2. Plot the session to see when error spiked
3. Correlate with video/observations
4. Adjust configuration

### 6. **Document Your Best Settings**

Once you find good settings:

```bash
# Export your best run
python3 tools/analyze_trial_data.py
# Select option 5 to export

# Save your config.yaml
cp config.yaml config_best_settings_backup.yaml
```

## Managing Disk Space

Trial data can accumulate quickly!

### Check Data Size
```bash
du -sh data/logs
```

### Clean Old Logs

**Using the tool:**
```bash
python3 tools/analyze_trial_data.py
# Select option 6 - Clean old logs
# Choose how many recent sessions to keep
```

**Manual cleanup:**
```bash
# Keep only last 5 sessions
ls -t data/logs/summary_*.json | tail -n +6 | sed 's/summary/*/g' | xargs rm
```

### Disable Logging

If you don't need logging, edit `config.yaml`:
```yaml
logging:
  enabled: false  # Disable all logging
```

Or save less data:
```yaml
logging:
  enabled: true
  log_dir: "data/logs"
  save_video: false  # Don't save video (uses lots of space)
```

## Best Practices

### During Development/Tuning
✅ Enable logging
✅ Keep recent sessions for comparison
✅ Analyze after each major change
✅ Document what settings worked

### During Competition/Demo
⚠️ Optional: Disable logging for max performance
✅ Or keep logging for post-analysis
✅ Clean old logs beforehand

### Regular Maintenance
🗓️ Weekly: Review and clean old logs
🗓️ Monthly: Archive best runs
🗓️ Before backup: Clean unnecessary data

## Example Workflow

### Tuning Session:
```bash
# 1. Run trial with current settings
cd src
python3 main.py
# [Run for 30-60 seconds, then Ctrl+C]

# 2. Analyze the data
cd ../tools
python3 analyze_trial_data.py
# Select option 2 - View summary
# Select option 3 - Plot graphs

# 3. Adjust config.yaml based on results

# 4. Run another trial

# 5. Compare sessions (option 4)

# 6. Keep best settings, clean old attempts
```

## Exporting Data for Reports

### For Documentation:
```bash
# Generate plots
python3 tools/analyze_trial_data.py
# Select session, save plots

# Export summary
cp data/logs/summary_YYYYMMDD_HHMMSS.json report_data.json
```

### For Academic/Research Use:
All data is in standard formats (CSV, JSON, TXT) and can be:
- Imported into MATLAB
- Analyzed with pandas/numpy
- Plotted with matplotlib/gnuplot
- Included in LaTeX documents
- Shared with collaborators

## Quick Reference

```bash
# View latest summary
ls -t data/logs/summary_*.json | head -1 | xargs cat | python3 -m json.tool

# Count total sessions
ls data/logs/summary_*.json | wc -l

# Check disk usage
du -sh data/logs

# Analyze data
python3 tools/analyze_trial_data.py

# Quick plot (requires matplotlib)
python3 -c "import pandas as pd; import matplotlib.pyplot as plt; \
df = pd.read_csv('data/logs/frames_YYYYMMDD_HHMMSS.csv'); \
df['error_px'].plot(); plt.show()"
```

## Requirements for Analysis Tool

```bash
# Install if needed
pip3 install matplotlib numpy pandas
```

---

**Remember:** Trial data helps you understand and improve your vehicle's performance. Don't just delete it - analyze it! 📊
