// Camera-controlled autonomous vehicle - ENHANCED VERSION
// Arduino code for motor control with diagnostics and LED indicators
// This version includes status LEDs and diagnostic commands

// Motor pins
#define LEFT_MOTOR_F 2
#define LEFT_MOTOR_B 3
#define LEFT_ENABLE 9
#define RIGHT_MOTOR_F 4
#define RIGHT_MOTOR_B 5
#define RIGHT_ENABLE 10

// LED indicator pins (optional - connect LEDs to these pins)
#define LED_STATUS 13      // Built-in LED - System ready
#define LED_LINE_DETECT 12 // External LED - Line detected
#define LED_WARNING 11     // External LED - Warning/Error

// Variables
String command = "";
int baseSpeed = 150;
bool diagnosticMode = false;
unsigned long lastCommandTime = 0;
unsigned long commandTimeout = 2000; // 2 second timeout

// Statistics
unsigned long totalCommands = 0;
unsigned long lastReportTime = 0;

void setup() {
  Serial.begin(9600);

  // Setup motor pins
  pinMode(LEFT_MOTOR_F, OUTPUT);
  pinMode(LEFT_MOTOR_B, OUTPUT);
  pinMode(RIGHT_MOTOR_F, OUTPUT);
  pinMode(RIGHT_MOTOR_B, OUTPUT);
  pinMode(LEFT_ENABLE, OUTPUT);
  pinMode(RIGHT_ENABLE, OUTPUT);

  // Setup LED pins
  pinMode(LED_STATUS, OUTPUT);
  pinMode(LED_LINE_DETECT, OUTPUT);
  pinMode(LED_WARNING, OUTPUT);

  // Initial state
  stopMotors();

  // LED startup sequence
  startupSequence();

  // Status LED on - system ready
  digitalWrite(LED_STATUS, HIGH);

  Serial.println("=====================================");
  Serial.println(" CAMERA VEHICLE - ENHANCED VERSION");
  Serial.println("=====================================");
  Serial.println("System Ready!");
  Serial.println("Type 'HELP' for available commands");
  Serial.println("=====================================");

  lastCommandTime = millis();
}

void loop() {
  // Check for command timeout (safety feature)
  if (millis() - lastCommandTime > commandTimeout) {
    // No command received for 2 seconds - show warning
    digitalWrite(LED_WARNING, HIGH);
  } else {
    digitalWrite(LED_WARNING, LOW);
  }

  // Read serial commands
  if (Serial.available()) {
    command = Serial.readStringUntil('\n');
    command.trim();

    if (command.length() > 0) {
      lastCommandTime = millis();
      totalCommands++;

      // Parse command
      char cmd = command.charAt(0);

      // Handle diagnostic commands
      if (command.equals("HELP")) {
        printHelp();
        return;
      }
      else if (command.equals("STATUS")) {
        printStatus();
        return;
      }
      else if (command.equals("TEST")) {
        runDiagnosticTest();
        return;
      }
      else if (command.equals("RESET")) {
        resetStatistics();
        return;
      }

      // Handle movement commands
      switch(cmd) {
        case 'F':  // Forward
          {
            int speed = parseSpeed(command);
            moveForward(speed);
            digitalWrite(LED_LINE_DETECT, HIGH);
            if (diagnosticMode) {
              Serial.print("Forward: ");
              Serial.println(speed);
            }
          }
          break;

        case 'L':  // Left
          {
            int angle = parseAngle(command);
            int speed = parseSpeed(command);
            turnLeft(angle, speed);
            digitalWrite(LED_LINE_DETECT, HIGH);
            if (diagnosticMode) {
              Serial.print("Left: Angle=");
              Serial.print(angle);
              Serial.print(", Speed=");
              Serial.println(speed);
            }
          }
          break;

        case 'R':  // Right
          {
            int angle = parseAngle(command);
            int speed = parseSpeed(command);
            turnRight(angle, speed);
            digitalWrite(LED_LINE_DETECT, HIGH);
            if (diagnosticMode) {
              Serial.print("Right: Angle=");
              Serial.print(angle);
              Serial.print(", Speed=");
              Serial.println(speed);
            }
          }
          break;

        case 'S':  // Stop
          stopMotors();
          digitalWrite(LED_LINE_DETECT, LOW);
          if (diagnosticMode) {
            Serial.println("Stop");
          }
          break;

        case 'D':  // Toggle diagnostic mode
          diagnosticMode = !diagnosticMode;
          Serial.print("Diagnostic mode: ");
          Serial.println(diagnosticMode ? "ON" : "OFF");
          break;
      }
    }
  }

  // Report status every 10 seconds
  if (millis() - lastReportTime > 10000 && diagnosticMode) {
    printQuickStatus();
    lastReportTime = millis();
  }
}

int parseAngle(String cmd) {
  int firstColon = cmd.indexOf(':');
  int secondColon = cmd.indexOf(':', firstColon + 1);
  if (firstColon == -1 || secondColon == -1) return 0;
  return cmd.substring(firstColon + 1, secondColon).toInt();
}

int parseSpeed(String cmd) {
  int lastColon = cmd.lastIndexOf(':');
  if (lastColon == -1) return baseSpeed;
  return cmd.substring(lastColon + 1).toInt();
}

void moveForward(int speed) {
  // Clamp speed
  speed = constrain(speed, 0, 255);

  analogWrite(LEFT_ENABLE, speed);
  analogWrite(RIGHT_ENABLE, speed);

  digitalWrite(LEFT_MOTOR_F, HIGH);
  digitalWrite(LEFT_MOTOR_B, LOW);
  digitalWrite(RIGHT_MOTOR_F, HIGH);
  digitalWrite(RIGHT_MOTOR_B, LOW);
}

void turnLeft(int angle, int speed) {
  // Clamp values
  angle = constrain(angle, 0, 45);
  speed = constrain(speed, 0, 255);

  // Reduce left motor speed based on angle
  int leftSpeed = map(angle, 0, 45, speed, speed/2);

  analogWrite(LEFT_ENABLE, leftSpeed);
  analogWrite(RIGHT_ENABLE, speed);

  digitalWrite(LEFT_MOTOR_F, HIGH);
  digitalWrite(LEFT_MOTOR_B, LOW);
  digitalWrite(RIGHT_MOTOR_F, HIGH);
  digitalWrite(RIGHT_MOTOR_B, LOW);
}

void turnRight(int angle, int speed) {
  // Clamp values
  angle = constrain(angle, 0, 45);
  speed = constrain(speed, 0, 255);

  // Reduce right motor speed based on angle
  int rightSpeed = map(angle, 0, 45, speed, speed/2);

  analogWrite(LEFT_ENABLE, speed);
  analogWrite(RIGHT_ENABLE, rightSpeed);

  digitalWrite(LEFT_MOTOR_F, HIGH);
  digitalWrite(LEFT_MOTOR_B, LOW);
  digitalWrite(RIGHT_MOTOR_F, HIGH);
  digitalWrite(RIGHT_MOTOR_B, LOW);
}

void stopMotors() {
  digitalWrite(LEFT_MOTOR_F, LOW);
  digitalWrite(LEFT_MOTOR_B, LOW);
  digitalWrite(RIGHT_MOTOR_F, LOW);
  digitalWrite(RIGHT_MOTOR_B, LOW);
  analogWrite(LEFT_ENABLE, 0);
  analogWrite(RIGHT_ENABLE, 0);
}

void startupSequence() {
  // LED blink sequence to indicate startup
  for (int i = 0; i < 3; i++) {
    digitalWrite(LED_STATUS, HIGH);
    digitalWrite(LED_LINE_DETECT, HIGH);
    digitalWrite(LED_WARNING, HIGH);
    delay(100);
    digitalWrite(LED_STATUS, LOW);
    digitalWrite(LED_LINE_DETECT, LOW);
    digitalWrite(LED_WARNING, LOW);
    delay(100);
  }
}

void printHelp() {
  Serial.println("\n========== HELP ==========");
  Serial.println("Movement Commands:");
  Serial.println("  F:[speed]          - Move forward");
  Serial.println("  L:[angle]:[speed]  - Turn left");
  Serial.println("  R:[angle]:[speed]  - Turn right");
  Serial.println("  S                  - Stop");
  Serial.println("  D                  - Toggle diagnostic mode");
  Serial.println();
  Serial.println("Diagnostic Commands:");
  Serial.println("  HELP    - Show this help");
  Serial.println("  STATUS  - Show detailed status");
  Serial.println("  TEST    - Run motor diagnostic test");
  Serial.println("  RESET   - Reset statistics");
  Serial.println();
  Serial.println("LED Indicators:");
  Serial.println("  Status LED (13)      - System ready");
  Serial.println("  Line Detect LED (12) - Line detected/moving");
  Serial.println("  Warning LED (11)     - Command timeout");
  Serial.println("==========================\n");
}

void printStatus() {
  Serial.println("\n========== STATUS ==========");
  Serial.print("Uptime: ");
  Serial.print(millis() / 1000);
  Serial.println(" seconds");
  Serial.print("Total Commands: ");
  Serial.println(totalCommands);
  Serial.print("Base Speed: ");
  Serial.println(baseSpeed);
  Serial.print("Diagnostic Mode: ");
  Serial.println(diagnosticMode ? "ON" : "OFF");
  Serial.print("Last Command: ");
  Serial.print((millis() - lastCommandTime) / 1000);
  Serial.println(" seconds ago");
  Serial.println("============================\n");
}

void printQuickStatus() {
  Serial.print("[STATUS] Uptime: ");
  Serial.print(millis() / 1000);
  Serial.print("s, Commands: ");
  Serial.println(totalCommands);
}

void runDiagnosticTest() {
  Serial.println("\n===== DIAGNOSTIC TEST =====");
  Serial.println("Testing motors and LEDs...");

  stopMotors();

  // Test LEDs
  Serial.println("1. Testing LEDs...");
  digitalWrite(LED_STATUS, HIGH);
  delay(300);
  digitalWrite(LED_LINE_DETECT, HIGH);
  delay(300);
  digitalWrite(LED_WARNING, HIGH);
  delay(300);
  digitalWrite(LED_STATUS, LOW);
  digitalWrite(LED_LINE_DETECT, LOW);
  digitalWrite(LED_WARNING, LOW);
  Serial.println("   LEDs OK");

  // Test left motor
  Serial.println("2. Testing LEFT motor...");
  analogWrite(LEFT_ENABLE, 100);
  digitalWrite(LEFT_MOTOR_F, HIGH);
  digitalWrite(LEFT_MOTOR_B, LOW);
  delay(1000);
  stopMotors();
  delay(500);
  Serial.println("   Left motor tested");

  // Test right motor
  Serial.println("3. Testing RIGHT motor...");
  analogWrite(RIGHT_ENABLE, 100);
  digitalWrite(RIGHT_MOTOR_F, HIGH);
  digitalWrite(RIGHT_MOTOR_B, LOW);
  delay(1000);
  stopMotors();
  delay(500);
  Serial.println("   Right motor tested");

  // Test both motors
  Serial.println("4. Testing BOTH motors...");
  moveForward(100);
  delay(1000);
  stopMotors();
  Serial.println("   Both motors tested");

  // Turn status LED back on
  digitalWrite(LED_STATUS, HIGH);

  Serial.println("===== TEST COMPLETE =====\n");
}

void resetStatistics() {
  totalCommands = 0;
  lastReportTime = millis();
  Serial.println("Statistics reset!");
}
