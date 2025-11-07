/*
 * LiDAR Vehicle Test & Calibration Script
 * 
 * Use this to verify your hardware setup before running full trials
 * Tests each component individually
 */

#include <RPLidar.h>

RPLidar lidar;

// Pin definitions (from config.h)
#define LIDAR_MOTOR_PIN 12
#define MOTOR_LEFT_FWD 5
#define MOTOR_LEFT_BWD 6
#define MOTOR_RIGHT_FWD 9
#define MOTOR_RIGHT_BWD 10
#define MOTOR_LEFT_EN 3
#define MOTOR_RIGHT_EN 11

bool testComplete = false;

void setup() {
  Serial.begin(115200);
  while (!Serial) delay(10);
  
  Serial.println("\n======================================");
  Serial.println("LIDAR VEHICLE - TEST & CALIBRATION");
  Serial.println("======================================\n");
  
  // Initialize pins
  pinMode(MOTOR_LEFT_FWD, OUTPUT);
  pinMode(MOTOR_LEFT_BWD, OUTPUT);
  pinMode(MOTOR_RIGHT_FWD, OUTPUT);
  pinMode(MOTOR_RIGHT_BWD, OUTPUT);
  pinMode(MOTOR_LEFT_EN, OUTPUT);
  pinMode(MOTOR_RIGHT_EN, OUTPUT);
  pinMode(LIDAR_MOTOR_PIN, OUTPUT);
  
  delay(1000);
  showMenu();
}

void loop() {
  if (Serial.available()) {
    char cmd = Serial.read();
    
    switch(cmd) {
      case '1':
        testMotors();
        break;
      case '2':
        testLidar();
        break;
      case '3':
        calibrateMotorBalance();
        break;
      case '4':
        testFullSystem();
        break;
      case '5':
        showMenu();
        break;
      case 'q':
        stopAll();
        Serial.println("\nStopping all systems...");
        break;
      default:
        break;
    }
  }
}

void showMenu() {
  Serial.println("\n======================================");
  Serial.println("TEST MENU");
  Serial.println("======================================");
  Serial.println("1 - Test Motors");
  Serial.println("2 - Test LiDAR");
  Serial.println("3 - Calibrate Motor Balance");
  Serial.println("4 - Test Full System");
  Serial.println("5 - Show Menu");
  Serial.println("q - Stop All");
  Serial.println("======================================");
  Serial.println("Enter command:");
}

void testMotors() {
  Serial.println("\n--- MOTOR TEST ---");
  Serial.println("Testing motors individually...\n");
  
  stopAll();
  delay(500);
  
  // Test Left Motor Forward
  Serial.println("Left Motor FORWARD (2 sec)...");
  digitalWrite(MOTOR_LEFT_FWD, HIGH);
  digitalWrite(MOTOR_LEFT_BWD, LOW);
  analogWrite(MOTOR_LEFT_EN, 100);
  delay(2000);
  stopAll();
  delay(500);
  
  // Test Left Motor Backward
  Serial.println("Left Motor BACKWARD (2 sec)...");
  digitalWrite(MOTOR_LEFT_FWD, LOW);
  digitalWrite(MOTOR_LEFT_BWD, HIGH);
  analogWrite(MOTOR_LEFT_EN, 100);
  delay(2000);
  stopAll();
  delay(500);
  
  // Test Right Motor Forward
  Serial.println("Right Motor FORWARD (2 sec)...");
  digitalWrite(MOTOR_RIGHT_FWD, HIGH);
  digitalWrite(MOTOR_RIGHT_BWD, LOW);
  analogWrite(MOTOR_RIGHT_EN, 100);
  delay(2000);
  stopAll();
  delay(500);
  
  // Test Right Motor Backward
  Serial.println("Right Motor BACKWARD (2 sec)...");
  digitalWrite(MOTOR_RIGHT_FWD, LOW);
  digitalWrite(MOTOR_RIGHT_BWD, HIGH);
  analogWrite(MOTOR_RIGHT_EN, 100);
  delay(2000);
  stopAll();
  delay(500);
  
  // Test Both Forward
  Serial.println("Both Motors FORWARD (2 sec)...");
  digitalWrite(MOTOR_LEFT_FWD, HIGH);
  digitalWrite(MOTOR_LEFT_BWD, LOW);
  digitalWrite(MOTOR_RIGHT_FWD, HIGH);
  digitalWrite(MOTOR_RIGHT_BWD, LOW);
  analogWrite(MOTOR_LEFT_EN, 100);
  analogWrite(MOTOR_RIGHT_EN, 100);
  delay(2000);
  stopAll();
  
  Serial.println("\nMotor test complete!");
  Serial.println("Check:");
  Serial.println("  ✓ Did all motors spin?");
  Serial.println("  ✓ Did they spin in correct direction?");
  Serial.println("  ✓ Was speed consistent?");
  Serial.println("\nIf motors run backward, modify config.h");
  showMenu();
}

void testLidar() {
  Serial.println("\n--- LIDAR TEST ---");
  Serial.println("Starting LiDAR...\n");
  
  // Start LiDAR motor
  analogWrite(LIDAR_MOTOR_PIN, 255);
  delay(1000);
  
  // Initialize LiDAR
  lidar.begin(Serial1);
  
  Serial.println("Collecting scan data for 5 seconds...");
  Serial.println("Format: Angle | Distance (mm)");
  Serial.println("----------------------------");
  
  unsigned long startTime = millis();
  int pointCount = 0;
  
  while (millis() - startTime < 5000) {
    if (IS_OK(lidar.waitPoint())) {
      float distance = lidar.getCurrentPoint().distance;
      float angle = lidar.getCurrentPoint().angle;
      
      pointCount++;
      
      // Print every 20th point to avoid flooding
      if (pointCount % 20 == 0) {
        Serial.print("Angle: ");
        Serial.print(angle, 1);
        Serial.print("° | Distance: ");
        Serial.print(distance);
        Serial.println(" mm");
      }
    }
  }
  
  Serial.println("\nLiDAR test complete!");
  Serial.print("Collected ");
  Serial.print(pointCount);
  Serial.println(" data points");
  
  Serial.println("\nCheck:");
  Serial.println("  ✓ Is LiDAR spinning?");
  Serial.println("  ✓ Are distance readings reasonable?");
  Serial.println("  ✓ Do readings change when you move objects?");
  
  showMenu();
}

void calibrateMotorBalance() {
  Serial.println("\n--- MOTOR BALANCE CALIBRATION ---");
  Serial.println("Vehicle will drive forward for 3 seconds");
  Serial.println("Observe if it drifts left or right\n");
  Serial.println("Starting in 3...");
  delay(1000);
  Serial.println("2...");
  delay(1000);
  Serial.println("1...");
  delay(1000);
  Serial.println("GO!\n");
  
  // Drive forward
  digitalWrite(MOTOR_LEFT_FWD, HIGH);
  digitalWrite(MOTOR_LEFT_BWD, LOW);
  digitalWrite(MOTOR_RIGHT_FWD, HIGH);
  digitalWrite(MOTOR_RIGHT_BWD, LOW);
  analogWrite(MOTOR_LEFT_EN, 100);
  analogWrite(MOTOR_RIGHT_EN, 100);
  
  delay(3000);
  stopAll();
  
  Serial.println("\nTest complete!");
  Serial.println("\nResults:");
  Serial.println("  - If vehicle drifted LEFT:");
  Serial.println("    Increase RIGHT_MOTOR_FACTOR in config.h");
  Serial.println("    OR decrease LEFT_MOTOR_FACTOR");
  Serial.println("\n  - If vehicle drifted RIGHT:");
  Serial.println("    Increase LEFT_MOTOR_FACTOR in config.h");
  Serial.println("    OR decrease RIGHT_MOTOR_FACTOR");
  Serial.println("\n  - If vehicle went straight:");
  Serial.println("    Motors are balanced! ✓");
  
  showMenu();
}

void testFullSystem() {
  Serial.println("\n--- FULL SYSTEM TEST ---");
  Serial.println("Testing integrated system for 10 seconds");
  Serial.println("Vehicle will attempt wall following\n");
  
  // Start LiDAR
  analogWrite(LIDAR_MOTOR_PIN, 255);
  lidar.begin(Serial1);
  delay(1000);
  
  unsigned long startTime = millis();
  float scanData[360] = {0};
  
  Serial.println("Running...");
  
  while (millis() - startTime < 10000) {
    // Get scan
    if (IS_OK(lidar.waitPoint())) {
      float distance = lidar.getCurrentPoint().distance;
      float angle = lidar.getCurrentPoint().angle;
      int angleInt = (int)angle;
      
      if (angleInt >= 0 && angleInt < 360) {
        scanData[angleInt] = distance;
      }
    }
    
    // Every second, process and control
    if (millis() % 1000 < 50) {
      float leftWall = getAverageDistance(scanData, 90, 20);
      float rightWall = getAverageDistance(scanData, 270, 20);
      float frontWall = getAverageDistance(scanData, 0, 15);
      
      Serial.print("L: ");
      Serial.print(leftWall);
      Serial.print(" | R: ");
      Serial.print(rightWall);
      Serial.print(" | F: ");
      Serial.println(frontWall);
      
      // Simple control: move forward if clear
      if (frontWall > 300) {
        digitalWrite(MOTOR_LEFT_FWD, HIGH);
        digitalWrite(MOTOR_LEFT_BWD, LOW);
        digitalWrite(MOTOR_RIGHT_FWD, HIGH);
        digitalWrite(MOTOR_RIGHT_BWD, LOW);
        analogWrite(MOTOR_LEFT_EN, 80);
        analogWrite(MOTOR_RIGHT_EN, 80);
      } else {
        stopAll();
      }
    }
  }
  
  stopAll();
  
  Serial.println("\nFull system test complete!");
  Serial.println("Check:");
  Serial.println("  ✓ Did LiDAR provide distance readings?");
  Serial.println("  ✓ Did motors respond to sensor input?");
  Serial.println("  ✓ Did vehicle avoid obstacles?");
  
  showMenu();
}

float getAverageDistance(float* data, int centerAngle, int window) {
  float sum = 0;
  int count = 0;
  
  for (int i = centerAngle - window; i <= centerAngle + window; i++) {
    int idx = (i + 360) % 360;
    if (data[idx] > 0 && data[idx] < 8000) {
      sum += data[idx];
      count++;
    }
  }
  
  return (count > 0) ? (sum / count) : 9999;
}

void stopAll() {
  // Stop all motors
  digitalWrite(MOTOR_LEFT_FWD, LOW);
  digitalWrite(MOTOR_LEFT_BWD, LOW);
  digitalWrite(MOTOR_RIGHT_FWD, LOW);
  digitalWrite(MOTOR_RIGHT_BWD, LOW);
  analogWrite(MOTOR_LEFT_EN, 0);
  analogWrite(MOTOR_RIGHT_EN, 0);
}
