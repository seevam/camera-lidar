// Camera-controlled autonomous vehicle
// Arduino code for motor control

// Motor pins
#define LEFT_MOTOR_F 2
#define LEFT_MOTOR_B 3
#define LEFT_ENABLE 9
#define RIGHT_MOTOR_F 4
#define RIGHT_MOTOR_B 5
#define RIGHT_ENABLE 10

// Variables
String command = "";
int baseSpeed = 150;

void setup() {
  Serial.begin(9600);
  
  // Setup motor pins
  pinMode(LEFT_MOTOR_F, OUTPUT);
  pinMode(LEFT_MOTOR_B, OUTPUT);
  pinMode(RIGHT_MOTOR_F, OUTPUT);
  pinMode(RIGHT_MOTOR_B, OUTPUT);
  pinMode(LEFT_ENABLE, OUTPUT);
  pinMode(RIGHT_ENABLE, OUTPUT);
  
  // Initial state
  stopMotors();
  
  Serial.println("Camera Vehicle Ready!");
}

void loop() {
  // Read serial commands
  if (Serial.available()) {
    command = Serial.readStringUntil('\n');
    command.trim();
    
    // Parse command
    char cmd = command.charAt(0);
    
    switch(cmd) {
      case 'F':  // Forward
        {
          int speed = parseSpeed(command);
          moveForward(speed);
        }
        break;
        
      case 'L':  // Left
        {
          int angle = parseAngle(command);
          int speed = parseSpeed(command);
          turnLeft(angle, speed);
        }
        break;
        
      case 'R':  // Right
        {
          int angle = parseAngle(command);
          int speed = parseSpeed(command);
          turnRight(angle, speed);
        }
        break;
        
      case 'S':  // Stop
        stopMotors();
        break;
    }
  }
}

int parseAngle(String cmd) {
  int firstColon = cmd.indexOf(':');
  int secondColon = cmd.indexOf(':', firstColon + 1);
  return cmd.substring(firstColon + 1, secondColon).toInt();
}

int parseSpeed(String cmd) {
  int lastColon = cmd.lastIndexOf(':');
  return cmd.substring(lastColon + 1).toInt();
}

void moveForward(int speed) {
  analogWrite(LEFT_ENABLE, speed);
  analogWrite(RIGHT_ENABLE, speed);
  
  digitalWrite(LEFT_MOTOR_F, HIGH);
  digitalWrite(LEFT_MOTOR_B, LOW);
  digitalWrite(RIGHT_MOTOR_F, HIGH);
  digitalWrite(RIGHT_MOTOR_B, LOW);
}

void turnLeft(int angle, int speed) {
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
