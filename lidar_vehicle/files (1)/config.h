/*
 * LiDAR Vehicle Configuration File
 * 
 * Modify these settings to match your hardware setup
 * without changing the main code
 */

#ifndef CONFIG_H
#define CONFIG_H

// ==================== HARDWARE PINS ====================

// LiDAR Motor Control
#define LIDAR_MOTOR_PIN 12        // PWM pin for LiDAR motor speed control
#define LIDAR_MOTOR_SPEED 255     // 0-255, usually keep at 255

// Motor Driver Pins (L298N Configuration)
#define MOTOR_LEFT_FWD 5          // Left motor forward
#define MOTOR_LEFT_BWD 6          // Left motor backward  
#define MOTOR_RIGHT_FWD 9         // Right motor forward
#define MOTOR_RIGHT_BWD 10        // Right motor backward
#define MOTOR_LEFT_EN 3           // Left motor speed (PWM)
#define MOTOR_RIGHT_EN 11         // Right motor speed (PWM)

// Alternative: TB6612FNG Configuration (uncomment if using TB6612)
// #define MOTOR_LEFT_PWM 3
// #define MOTOR_LEFT_IN1 5
// #define MOTOR_LEFT_IN2 6
// #define MOTOR_RIGHT_PWM 11
// #define MOTOR_RIGHT_IN1 9
// #define MOTOR_RIGHT_IN2 10
// #define MOTOR_STBY 8

// Bluetooth/Serial (optional)
#define BT_RX 16                  // Bluetooth RX pin
#define BT_TX 17                  // Bluetooth TX pin

// ==================== LIDAR CONFIGURATION ====================

// LiDAR Type (uncomment the one you're using)
#define LIDAR_TYPE_RPLIDAR_A1     // RPLiDAR A1
// #define LIDAR_TYPE_RPLIDAR_A2  // RPLiDAR A2
// #define LIDAR_TYPE_YDLIDAR_X4  // Ydlidar X4

// Serial port for LiDAR
#define LIDAR_SERIAL Serial1      // For Arduino Mega: Serial1, Serial2, Serial3
#define LIDAR_BAUDRATE 115200     // Standard for RPLiDAR

// ==================== VEHICLE PARAMETERS ====================

// Motor Speed Settings
#define BASE_SPEED 80             // Normal cruising speed (0-255)
#define MAX_SPEED 120             // Maximum speed limit
#define MIN_SPEED 40              // Minimum speed to maintain movement
#define TURN_SPEED 60             // Speed during sharp turns

// Motor Direction Calibration
// If your vehicle turns opposite direction, swap these
#define LEFT_MOTOR_REVERSE false  // Set to true if left motor runs backward
#define RIGHT_MOTOR_REVERSE false // Set to true if right motor runs backward

// Speed Balancing (if one motor is faster)
#define LEFT_MOTOR_FACTOR 1.0     // Multiply left motor speed (0.8 - 1.2)
#define RIGHT_MOTOR_FACTOR 1.0    // Multiply right motor speed (0.8 - 1.2)

// ==================== PATH FOLLOWING SETTINGS ====================

// Wall Following
#define TARGET_WALL_DISTANCE 300  // Target distance from wall (mm)
#define WALL_FOLLOW_SIDE 'L'      // 'L' = follow left wall, 'R' = follow right wall
#define WALL_DETECTION_ANGLE 20   // Angular window for wall detection (degrees)

// Obstacle Detection
#define OBSTACLE_THRESHOLD 200    // Distance to consider as collision (mm)
#define SAFE_DISTANCE 250         // Safe distance margin (mm)
#define FRONT_DETECTION_ANGLE 30  // Forward-looking angle (degrees)

// Emergency Response
#define COLLISION_STOP_TIME 500   // Stop duration after collision (ms)
#define BACKUP_SPEED 60           // Speed when backing up
#define BACKUP_DURATION 300       // How long to back up (ms)

// ==================== PID CONTROLLER ====================

// PID Tuning Parameters
// Start with these values and adjust based on performance
#define KP 0.5                    // Proportional gain (0.1 - 2.0)
#define KI 0.0                    // Integral gain (0.0 - 0.5)
#define KD 0.3                    // Derivative gain (0.0 - 1.0)

// PID Limits
#define INTEGRAL_LIMIT 100        // Maximum integral accumulation
#define PID_OUTPUT_LIMIT 100      // Maximum PID output correction

/*
 * PID TUNING GUIDE:
 * 
 * If vehicle oscillates (wobbles):
 *   - Reduce KP
 *   - Increase KD
 * 
 * If vehicle responds slowly:
 *   - Increase KP
 *   - Reduce KD
 * 
 * If vehicle drifts over time:
 *   - Increase KI (but keep small, like 0.01)
 * 
 * If vehicle is unstable:
 *   - Reduce all gains by 50%
 *   - Gradually increase KP first
 */

// ==================== DATA LOGGING ====================

// Logging Settings
#define LOG_INTERVAL 100          // Milliseconds between data logs
#define TRIAL_DURATION 120000     // Trial duration (ms) - 120000 = 2 minutes

// Test Modes
#define NUM_TEST_MODES 3          // Number of light conditions
const String TEST_MODES[] = {"bright", "medium", "low"};

// ==================== LIDAR PROCESSING ====================

// Scan Processing
#define SCAN_BUFFER_SIZE 360      // Number of points in full scan
#define MIN_VALID_DISTANCE 150    // Minimum valid distance (mm)
#define MAX_VALID_DISTANCE 8000   // Maximum valid distance (mm)

// Filtering
#define USE_MEDIAN_FILTER false   // Apply median filter to distances
#define FILTER_WINDOW_SIZE 3      // Window size for filtering

// ==================== SERIAL COMMUNICATION ====================

// Serial Settings
#define SERIAL_BAUDRATE 115200    // Main serial (USB) baudrate
#define SERIAL_TIMEOUT 1000       // Timeout for serial commands (ms)

// Debug Output
#define DEBUG_ENABLED true        // Enable/disable debug messages
#define DEBUG_INTERVAL 10         // Print debug every N measurements

// ==================== ADVANCED SETTINGS ====================

// Performance
#define LOOP_DELAY 10             // Main loop delay (ms)
#define SCAN_TIMEOUT 500          // LiDAR scan timeout (ms)

// Safety Features
#define ENABLE_EMERGENCY_STOP true    // Enable emergency stop on collision
#define MAX_CONSECUTIVE_ERRORS 10     // Stop after N consecutive errors
#define WATCHDOG_ENABLED true         // Enable software watchdog

// Data Validation
#define MIN_DATA_POINTS 50        // Minimum points needed for valid trial
#define MAX_DEVIATION_CM 50       // Maximum deviation before error (cm)

// ==================== VEHICLE DIMENSIONS ====================
// Used for advanced calculations (optional)

#define VEHICLE_LENGTH 20         // cm
#define VEHICLE_WIDTH 15          // cm
#define WHEEL_BASE 15             // Distance between wheels (cm)
#define WHEEL_DIAMETER 6          // cm
#define LIDAR_HEIGHT 10           // Height above ground (cm)
#define LIDAR_OFFSET_X 0          // Offset from center X (cm)
#define LIDAR_OFFSET_Y 0          // Offset from center Y (cm)

// ==================== TRACK SPECIFICATIONS ====================
// For reference and analysis

#define TRACK_WIDTH 80            // Width of test track (cm)
#define TRACK_LENGTH 400          // Length of test track (cm)
#define NUM_OBSTACLES 10          // Number of obstacles on track
#define OBSTACLE_WIDTH 10         // Width of obstacles (cm)

#endif // CONFIG_H
