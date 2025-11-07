/*
 * LiDAR-Based Autonomous Vehicle - Main Controller
 * Project: Camera vs LiDAR Performance Comparison
 * 
 * Hardware:
 * - ESP32 / Arduino Mega
 * - Ydlidar X4 or RPLiDAR A1/A2
 * - DC Motors with L298N/TB6612 Motor Driver
 * - Bluetooth Module (HC-05) for data transmission
 * 
 * This code implements wall-following and path tracking for
 * testing under different light conditions (Bright, Medium, Low)
 */

#include <RPLidar.h>
// #include <SoftwareSerial.h>  // For Bluetooth

// ==================== CONFIGURATION ====================
#define LIDAR_MOTOR_PIN 12
#define MOTOR_PWM_PIN 13

// Motor Driver Pins (L298N)
#define MOTOR_LEFT_FWD 5
#define MOTOR_LEFT_BWD 6
#define MOTOR_RIGHT_FWD 9
#define MOTOR_RIGHT_BWD 10
#define MOTOR_LEFT_EN 3
#define MOTOR_RIGHT_EN 11

// Bluetooth (optional)
#define BT_RX 16
#define BT_TX 17

// LiDAR Configuration
#define RPLIDAR_MOTOR 3

// Test Parameters
#define BASE_SPEED 80           // Base motor speed (0-255)
#define MAX_SPEED 120
#define MIN_SPEED 40
#define TURN_SPEED 60

#define TARGET_WALL_DISTANCE 300  // Target distance from wall (mm)
#define WALL_FOLLOW_SIDE 'L'      // 'L' for left wall, 'R' for right
#define OBSTACLE_THRESHOLD 200    // mm - collision detection
#define SAFE_DISTANCE 250         // mm - safety margin

// PID Parameters
#define KP 0.5
#define KI 0.0
#define KD 0.3

// Logging
#define LOG_INTERVAL 100          // ms between logs
#define TRIAL_DURATION 120000     // 2 minutes per trial

// ==================== GLOBAL VARIABLES ====================
RPLidar lidar;

// Test Configuration
String testMode = "medium";  // bright, medium, low
unsigned long trialStartTime = 0;
unsigned long lastLogTime = 0;
bool testActive = false;

// Sensor Data
float scanData[360] = {0};
bool validScan = false;

// Path Following
float currentDeviation = 0;
float prevDeviation = 0;
float integralError = 0;

// Metrics
int collisionCount = 0;
float totalDeviation = 0;
int measurementCount = 0;
float collisionDisplacements[50];
int collisionIndex = 0;

// ==================== SETUP ====================
void setup() {
  Serial.begin(115200);
  Serial1.begin(115200);  // LiDAR Serial
  
  // Initialize motor pins
  pinMode(MOTOR_LEFT_FWD, OUTPUT);
  pinMode(MOTOR_LEFT_BWD, OUTPUT);
  pinMode(MOTOR_RIGHT_FWD, OUTPUT);
  pinMode(MOTOR_RIGHT_BWD, OUTPUT);
  pinMode(MOTOR_LEFT_EN, OUTPUT);
  pinMode(MOTOR_RIGHT_EN, OUTPUT);
  
  // Initialize LiDAR
  lidar.begin(Serial1);
  pinMode(RPLIDAR_MOTOR, OUTPUT);
  analogWrite(RPLIDAR_MOTOR, 255);  // Full speed
  
  delay(1000);
  Serial.println("LiDAR Vehicle Initialized");
  Serial.println("Commands: START_BRIGHT, START_MEDIUM, START_LOW, STOP");
  
  stopMotors();
}

// ==================== MAIN LOOP ====================
void loop() {
  // Check for commands from Serial
  if (Serial.available()) {
    String command = Serial.readStringUntil('\n');
    command.trim();
    handleCommand(command);
  }
  
  // Run test if active
  if (testActive) {
    // Check trial duration
    if (millis() - trialStartTime > TRIAL_DURATION) {
      endTrial();
      return;
    }
    
    // Get LiDAR scan
    if (getLidarScan()) {
      // Process scan and calculate deviation
      processLidarData();
      
      // Apply control
      controlVehicle();
      
      // Check for obstacles/collisions
      checkCollisions();
      
      // Log data periodically
      if (millis() - lastLogTime > LOG_INTERVAL) {
        logData();
        lastLogTime = millis();
      }
    }
  }
  
  delay(10);  // Small delay to prevent overwhelming
}

// ==================== LIDAR PROCESSING ====================
bool getLidarScan() {
  if (IS_OK(lidar.waitPoint())) {
    float distance = lidar.getCurrentPoint().distance;
    float angle = lidar.getCurrentPoint().angle;
    int angleInt = (int)angle;
    
    if (angleInt >= 0 && angleInt < 360 && distance > 0) {
      scanData[angleInt] = distance;
      
      // Check if we have a complete scan
      static int lastAngle = 0;
      if (angleInt < lastAngle) {
        validScan = true;
      }
      lastAngle = angleInt;
      
      return validScan;
    }
  }
  return false;
}

void processLidarData() {
  if (!validScan) return;
  
  // Get wall distances based on follow side
  float leftWall = getWallDistance(90, 20);    // Left side
  float rightWall = getWallDistance(270, 20);  // Right side
  float frontDist = getWallDistance(0, 15);    // Front
  
  // Calculate deviation from target wall distance
  if (WALL_FOLLOW_SIDE == 'L') {
    // Follow left wall
    currentDeviation = leftWall - TARGET_WALL_DISTANCE;
  } else {
    // Follow right wall
    currentDeviation = TARGET_WALL_DISTANCE - rightWall;
  }
  
  // Store for metrics
  totalDeviation += abs(currentDeviation);
  measurementCount++;
  
  // Print debug info
  if (measurementCount % 10 == 0) {
    Serial.print("L: "); Serial.print(leftWall);
    Serial.print(" R: "); Serial.print(rightWall);
    Serial.print(" F: "); Serial.print(frontDist);
    Serial.print(" Dev: "); Serial.println(currentDeviation);
  }
  
  validScan = false;  // Reset for next scan
}

float getWallDistance(int centerAngle, int window) {
  // Average distance in angular window
  float sum = 0;
  int count = 0;
  
  for (int i = centerAngle - window; i <= centerAngle + window; i++) {
    int idx = (i + 360) % 360;
    if (scanData[idx] > 0 && scanData[idx] < 8000) {  // Valid range
      sum += scanData[idx];
      count++;
    }
  }
  
  return (count > 0) ? (sum / count) : 9999;
}

// ==================== VEHICLE CONTROL ====================
void controlVehicle() {
  // PID control for wall following
  float error = currentDeviation;
  
  // Integral
  integralError += error * 0.1;  // dt = 0.1s
  integralError = constrain(integralError, -100, 100);
  
  // Derivative
  float derivative = (error - prevDeviation) / 0.1;
  
  // PID output
  float correction = KP * error + KI * integralError + KD * derivative;
  correction = constrain(correction, -100, 100);
  
  // Calculate motor speeds
  int leftSpeed = BASE_SPEED - correction;
  int rightSpeed = BASE_SPEED + correction;
  
  // Constrain speeds
  leftSpeed = constrain(leftSpeed, MIN_SPEED, MAX_SPEED);
  rightSpeed = constrain(rightSpeed, MIN_SPEED, MAX_SPEED);
  
  // Apply to motors
  setMotorSpeed(leftSpeed, rightSpeed);
  
  // Update previous error
  prevDeviation = error;
}

void setMotorSpeed(int left, int right) {
  // Left motor
  if (left >= 0) {
    digitalWrite(MOTOR_LEFT_FWD, HIGH);
    digitalWrite(MOTOR_LEFT_BWD, LOW);
    analogWrite(MOTOR_LEFT_EN, abs(left));
  } else {
    digitalWrite(MOTOR_LEFT_FWD, LOW);
    digitalWrite(MOTOR_LEFT_BWD, HIGH);
    analogWrite(MOTOR_LEFT_EN, abs(left));
  }
  
  // Right motor
  if (right >= 0) {
    digitalWrite(MOTOR_RIGHT_FWD, HIGH);
    digitalWrite(MOTOR_RIGHT_BWD, LOW);
    analogWrite(MOTOR_RIGHT_EN, abs(right));
  } else {
    digitalWrite(MOTOR_RIGHT_FWD, LOW);
    digitalWrite(MOTOR_RIGHT_BWD, HIGH);
    analogWrite(MOTOR_RIGHT_EN, abs(right));
  }
}

void stopMotors() {
  digitalWrite(MOTOR_LEFT_FWD, LOW);
  digitalWrite(MOTOR_LEFT_BWD, LOW);
  digitalWrite(MOTOR_RIGHT_FWD, LOW);
  digitalWrite(MOTOR_RIGHT_BWD, LOW);
  analogWrite(MOTOR_LEFT_EN, 0);
  analogWrite(MOTOR_RIGHT_EN, 0);
}

// ==================== COLLISION DETECTION ====================
void checkCollisions() {
  // Check front and side sectors for obstacles
  float frontDist = getWallDistance(0, 30);
  float frontLeftDist = getWallDistance(45, 20);
  float frontRightDist = getWallDistance(315, 20);
  
  bool collision = false;
  float minDist = 9999;
  
  if (frontDist < OBSTACLE_THRESHOLD) {
    collision = true;
    minDist = min(minDist, frontDist);
  }
  if (frontLeftDist < OBSTACLE_THRESHOLD) {
    collision = true;
    minDist = min(minDist, frontLeftDist);
  }
  if (frontRightDist < OBSTACLE_THRESHOLD) {
    collision = true;
    minDist = min(minDist, frontRightDist);
  }
  
  if (collision) {
    collisionCount++;
    
    // Calculate displacement (how far into obstacle zone)
    float displacement = OBSTACLE_THRESHOLD - minDist;
    if (collisionIndex < 50) {
      collisionDisplacements[collisionIndex++] = displacement;
    }
    
    Serial.println("!!! COLLISION DETECTED !!!");
    Serial.print("Distance: "); Serial.println(minDist);
    
    // Emergency stop and back up
    stopMotors();
    delay(500);
    
    // Back up slightly
    setMotorSpeed(-60, -60);
    delay(300);
    stopMotors();
    delay(500);
  }
}

// ==================== DATA LOGGING ====================
void logData() {
  // Format: timestamp,deviation_mm,collision,light_condition
  Serial.print("DATA,");
  Serial.print(millis() - trialStartTime);
  Serial.print(",");
  Serial.print(currentDeviation);
  Serial.print(",");
  Serial.print(collisionCount);
  Serial.print(",");
  Serial.println(testMode);
}

// ==================== COMMAND HANDLING ====================
void handleCommand(String command) {
  if (command.startsWith("START_")) {
    if (command == "START_BRIGHT") {
      startTrial("bright");
    } else if (command == "START_MEDIUM") {
      startTrial("medium");
    } else if (command == "START_LOW") {
      startTrial("low");
    }
  } else if (command == "STOP") {
    endTrial();
  } else if (command == "STATUS") {
    printStatus();
  }
}

void startTrial(String mode) {
  Serial.print("Starting trial: ");
  Serial.println(mode);
  
  testMode = mode;
  trialStartTime = millis();
  lastLogTime = millis();
  testActive = true;
  
  // Reset metrics
  collisionCount = 0;
  totalDeviation = 0;
  measurementCount = 0;
  collisionIndex = 0;
  integralError = 0;
  prevDeviation = 0;
  
  Serial.println("TRIAL_START," + mode + "," + String(trialStartTime));
}

void endTrial() {
  if (!testActive) return;
  
  Serial.println("Ending trial...");
  testActive = false;
  stopMotors();
  
  // Calculate final metrics
  float avgDeviation = (measurementCount > 0) ? 
                       (totalDeviation / measurementCount) : 0;
  
  float avgDisplacement = 0;
  if (collisionIndex > 0) {
    for (int i = 0; i < collisionIndex; i++) {
      avgDisplacement += collisionDisplacements[i];
    }
    avgDisplacement /= collisionIndex;
  }
  
  // Calculate scores
  float pds = avgDeviation / 10.0 * 100;  // Normalize to 0-100
  float ocs = (collisionCount / 10.0) * 100;  // Assuming 10 obstacles
  float ods = (avgDisplacement / 20.0) * 100;
  float cps = 0.4 * pds + 0.35 * ocs + 0.25 * ods;
  
  // Print summary
  Serial.println("\n===== TRIAL SUMMARY =====");
  Serial.print("Mode: "); Serial.println(testMode);
  Serial.print("Duration: "); Serial.print((millis() - trialStartTime) / 1000); 
  Serial.println(" seconds");
  Serial.print("Average Deviation: "); Serial.print(avgDeviation); 
  Serial.println(" mm");
  Serial.print("Collisions: "); Serial.println(collisionCount);
  Serial.print("Avg Displacement: "); Serial.print(avgDisplacement); 
  Serial.println(" mm");
  Serial.println("\n--- Scores ---");
  Serial.print("PDS: "); Serial.println(pds);
  Serial.print("OCS: "); Serial.println(ocs);
  Serial.print("ODS: "); Serial.println(ods);
  Serial.print("CPS: "); Serial.println(cps);
  Serial.println("========================\n");
  
  Serial.println("TRIAL_END," + testMode + "," + String(avgDeviation) + "," + 
                 String(collisionCount) + "," + String(avgDisplacement));
}

void printStatus() {
  Serial.println("\n===== STATUS =====");
  Serial.print("Test Active: "); Serial.println(testActive ? "YES" : "NO");
  Serial.print("Mode: "); Serial.println(testMode);
  if (testActive) {
    Serial.print("Elapsed: "); Serial.print((millis() - trialStartTime) / 1000);
    Serial.println(" seconds");
    Serial.print("Measurements: "); Serial.println(measurementCount);
    Serial.print("Collisions: "); Serial.println(collisionCount);
  }
  Serial.println("==================\n");
}
