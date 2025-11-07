import serial
import time

class MotorController:
    def __init__(self, config):
        self.port = config['port']
        self.baudrate = config['baudrate']
        self.max_speed = config['max_speed']
        
        # Initialize serial connection
        try:
            self.arduino = serial.Serial(self.port, self.baudrate)
            time.sleep(2)  # Arduino reset time
            print(f"[INFO] Arduino connected on {self.port}")
        except Exception as e:
            print(f"[ERROR] Failed to connect to Arduino: {e}")
            self.arduino = None
    
    def steer(self, angle):
        """Send steering command to Arduino"""
        if not self.arduino:
            return
        
        # Constrain angle
        angle = max(-45, min(45, angle))
        
        # Create command
        if abs(angle) < 5:
            command = f"F:{self.max_speed}"  # Forward
        elif angle > 0:
            command = f"R:{int(angle)}:{self.max_speed}"  # Right
        else:
            command = f"L:{int(abs(angle))}:{self.max_speed}"  # Left
        
        # Send command
        try:
            self.arduino.write(f"{command}\n".encode())
        except:
            print("[ERROR] Failed to send command to Arduino")
    
    def stop(self):
        """Stop motors"""
        if self.arduino:
            self.arduino.write(b"S:0\n")
    
    def cleanup(self):
        """Close serial connection"""
        if self.arduino:
            self.stop()
            self.arduino.close()
