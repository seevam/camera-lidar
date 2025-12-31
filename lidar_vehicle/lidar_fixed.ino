/*
 * RPLiDAR Obstacle Avoidance Robot - FIXED VERSION
 *
 * Hardware:
 * - Arduino Mega
 * - RPLiDAR A1/A2 on Serial1
 * - Motor Driver (L298N or similar)
 * - 2 DC Motors
 *
 * CRITICAL FIX: Added RPLiDAR motor control pin!
 */

#include <RPLidar.h>

// ================= LIDAR CONFIGURATION =================
RPLidar lidar;
#define RPLIDAR_MOTOR 3        // PWM pin to control LiDAR motor (CRITICAL!)
#define LIDAR_BAUD 115200

// ================= MOTOR PINS (Your Configuration) =================
// RIGHT motor
#define ENA 9                   // Right motor PWM
#define IN1 7                   // Right motor direction
#define IN2 8

// LEFT motor
#define ENB 10                  // Left motor PWM
#define IN3 5                   // Left motor direction
#define IN4 6

// ================= NAVIGATION PARAMETERS =================
#define BASE_SPEED 150
#define TURN_SPEED 130
#define MIN_DISTANCE 300        // mm (30 cm)
#define SCAN_TIMEOUT 200        // ms

// ================= GLOBALS =================
float distances[360];           // Distance readings
unsigned long lastScanTime = 0;
int validPoints = 0;
bool lidarReady = false;

// ================= SETUP =================
void setup() {
  // Initialize Serial for debugging
  Serial.begin(115200);
  delay(100);
  Serial.println("\n\n========================================");
  Serial.println("RPLiDAR OBSTACLE AVOIDANCE - STARTING");
  Serial.println("========================================\n");

  // Initialize motor pins
  pinMode(ENA, OUTPUT);
  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);
  pinMode(ENB, OUTPUT);
  pinMode(IN3, OUTPUT);
  pinMode(IN4, OUTPUT);

  // **CRITICAL FIX**: Initialize LiDAR motor control pin
  pinMode(RPLIDAR_MOTOR, OUTPUT);
  Serial.println("1. Motor pins configured");

  // Stop motors initially
  stopMotors();
  Serial.println("2. Motors stopped");

  // Initialize LiDAR Serial
  Serial1.begin(LIDAR_BAUD);
  delay(500);
  Serial.println("3. Serial1 initialized at 115200 baud");

  // Initialize LiDAR
  lidar.begin(Serial1);
  delay(500);
  Serial.println("4. LiDAR interface initialized");

  // **CRITICAL FIX**: Start LiDAR motor at full speed
  analogWrite(RPLIDAR_MOTOR, 255);
  Serial.println("5. LiDAR motor started (PWM=255)");
  Serial.println("   >> MOTOR SHOULD BE SPINNING NOW <<");

  delay(2000);  // Give motor time to spin up

  // Start scanning
  lidar.startScan();
  Serial.println("6. Scan mode started");

  // Initialize distance array
  for (int i = 0; i < 360; i++) {
    distances[i] = 0;
  }

  Serial.println("\n========================================");
  Serial.println("SYSTEM READY - Waiting for LiDAR data...");
  Serial.println("========================================\n");

  lastScanTime = millis();
}

// ================= MAIN LOOP =================
void loop() {
  // Get LiDAR data
  if (IS_OK(lidar.waitPoint())) {
    float distance = lidar.getCurrentPoint().distance;
    float angle = lidar.getCurrentPoint().angle;
    byte quality = lidar.getCurrentPoint().quality;

    // Store valid data points
    if (quality > 0 && distance > 0) {
      int idx = (int)angle;
      if (idx >= 0 && idx < 360) {
        distances[idx] = distance;
        validPoints++;

        // Mark LiDAR as ready after receiving enough data
        if (!lidarReady && validPoints > 100) {
          lidarReady = true;
          Serial.println("\n*** LiDAR DATA DETECTED - SYSTEM ACTIVE ***\n");
        }
      }
    }

    // Print diagnostics every 360 points (one full rotation)
    if (validPoints % 360 == 0 && validPoints > 0) {
      printDiagnostics();
    }

    // React to obstacles if LiDAR is ready
    if (lidarReady) {
      reactToObstacle();
    }

    lastScanTime = millis();

  } else {
    // Check for timeout
    if (millis() - lastScanTime > SCAN_TIMEOUT) {
      if (!lidarReady) {
        Serial.println("WARNING: No LiDAR data received!");
        Serial.println("Check connections:");
        Serial.println("  - RX1 (pin 19) -> LiDAR TX (white)");
        Serial.println("  - TX1 (pin 18) -> LiDAR RX (green)");
        Serial.println("  - Pin 3 -> LiDAR MOTOR (orange/yellow)");
        Serial.println("  - 5V -> LiDAR 5V (red)");
        Serial.println("  - GND -> LiDAR GND (black)");
        delay(3000);
      }
      lastScanTime = millis();
    }
  }
}

// ================= OBSTACLE DETECTION =================
void reactToObstacle() {
  bool frontBlocked = false;
  float minFrontDist = 9999;

  // Check front sector (350-360 and 0-10 degrees)
  for (int i = 350; i < 360; i++) {
    if (distances[i] > 0 && distances[i] < MIN_DISTANCE) {
      frontBlocked = true;
      if (distances[i] < minFrontDist) minFrontDist = distances[i];
    }
  }
  for (int i = 0; i < 10; i++) {
    if (distances[i] > 0 && distances[i] < MIN_DISTANCE) {
      frontBlocked = true;
      if (distances[i] < minFrontDist) minFrontDist = distances[i];
    }
  }

  // React to obstacle
  if (frontBlocked) {
    Serial.print("OBSTACLE! Distance: ");
    Serial.print(minFrontDist);
    Serial.println(" mm - TURNING RIGHT");

    stopMotors();
    delay(150);

    turnRight();
    delay(500);  // Turn for 500ms

  } else {
    moveForward();
  }
}

// ================= MOTOR CONTROL =================
void moveForward() {
  // Right motor forward
  digitalWrite(IN1, HIGH);
  digitalWrite(IN2, LOW);
  analogWrite(ENA, BASE_SPEED);

  // Left motor forward
  digitalWrite(IN3, HIGH);
  digitalWrite(IN4, LOW);
  analogWrite(ENB, BASE_SPEED);
}

void turnRight() {
  // Right motor backward
  digitalWrite(IN1, LOW);
  digitalWrite(IN2, HIGH);
  analogWrite(ENA, TURN_SPEED);

  // Left motor forward
  digitalWrite(IN3, HIGH);
  digitalWrite(IN4, LOW);
  analogWrite(ENB, TURN_SPEED);
}

void stopMotors() {
  digitalWrite(IN1, LOW);
  digitalWrite(IN2, LOW);
  analogWrite(ENA, 0);

  digitalWrite(IN3, LOW);
  digitalWrite(IN4, LOW);
  analogWrite(ENB, 0);
}

// ================= DIAGNOSTICS =================
void printDiagnostics() {
  static int rotationCount = 0;
  rotationCount++;

  Serial.print("Rotation #");
  Serial.print(rotationCount);
  Serial.print(" | Valid points: ");
  Serial.print(validPoints);

  // Check front, left, right distances
  float front = getAverageDistance(0, 10);
  float left = getAverageDistance(90, 10);
  float right = getAverageDistance(270, 10);

  Serial.print(" | F: ");
  Serial.print(front);
  Serial.print("mm, L: ");
  Serial.print(left);
  Serial.print("mm, R: ");
  Serial.print(right);
  Serial.println("mm");
}

float getAverageDistance(int centerAngle, int window) {
  float sum = 0;
  int count = 0;

  for (int i = centerAngle - window; i <= centerAngle + window; i++) {
    int idx = (i + 360) % 360;
    if (distances[idx] > 0 && distances[idx] < 8000) {
      sum += distances[idx];
      count++;
    }
  }

  return (count > 0) ? (sum / count) : 0;
}
