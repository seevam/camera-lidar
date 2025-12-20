#!/usr/bin/env python3
"""
System Diagnostic Tool - Test all components of camera vehicle
Helps identify why the vehicle is not moving
"""

import cv2
import serial
import time
import sys
import os

# Add parent directory to path
sys.path.append('../src')

class SystemDiagnostic:
    def __init__(self):
        self.camera = None
        self.arduino = None
        self.issues = []
        self.warnings = []

    def print_header(self, text):
        print("\n" + "="*60)
        print(f"  {text}")
        print("="*60)

    def print_result(self, test_name, passed, message=""):
        status = "✓ PASS" if passed else "✗ FAIL"
        color_code = "\033[92m" if passed else "\033[91m"
        reset_code = "\033[0m"
        print(f"{color_code}[{status}]{reset_code} {test_name}")
        if message:
            print(f"       {message}")
        if not passed:
            self.issues.append(f"{test_name}: {message}")

    def test_camera_connection(self):
        """Test if camera can be opened"""
        self.print_header("TEST 1: Camera Connection")

        try:
            self.camera = cv2.VideoCapture(0)
            if not self.camera.isOpened():
                self.print_result("Camera Open", False, "Failed to open camera device 0")
                return False

            self.print_result("Camera Open", True, "Camera device 0 opened successfully")

            # Test frame capture
            ret, frame = self.camera.read()
            if not ret or frame is None:
                self.print_result("Frame Capture", False, "Cannot read frames from camera")
                return False

            h, w = frame.shape[:2]
            self.print_result("Frame Capture", True, f"Captured frame: {w}x{h}")

            # Show preview
            print("\n>>> Showing camera preview for 3 seconds...")
            cv2.imshow("Camera Test", frame)
            cv2.waitKey(3000)
            cv2.destroyAllWindows()

            return True

        except Exception as e:
            self.print_result("Camera Test", False, str(e))
            return False

    def test_arduino_connection(self):
        """Test if Arduino is connected"""
        self.print_header("TEST 2: Arduino Connection")

        # Try common ports
        ports_to_try = [
            "/dev/ttyUSB0",
            "/dev/ttyUSB1",
            "/dev/ttyACM0",
            "/dev/ttyACM1",
            "COM3",
            "COM4"
        ]

        connected = False
        for port in ports_to_try:
            try:
                print(f"Trying port: {port}")
                self.arduino = serial.Serial(port, 9600, timeout=2)
                time.sleep(2)  # Wait for Arduino to reset

                # Check if Arduino responds
                if self.arduino.is_open:
                    self.print_result("Arduino Connection", True, f"Connected on {port}")
                    connected = True
                    break
            except (serial.SerialException, FileNotFoundError):
                continue

        if not connected:
            self.print_result("Arduino Connection", False,
                            "Could not connect to Arduino on any port")
            print("\n>>> Available serial ports:")
            os.system("ls /dev/ttyUSB* /dev/ttyACM* 2>/dev/null || echo 'No serial ports found'")
            return False

        return True

    def test_serial_communication(self):
        """Test if Arduino responds to commands"""
        self.print_header("TEST 3: Serial Communication")

        if not self.arduino:
            self.print_result("Serial Test", False, "Arduino not connected")
            return False

        try:
            # Clear buffer
            self.arduino.reset_input_buffer()

            # Send STATUS command (if using enhanced version)
            self.arduino.write(b"STATUS\n")
            time.sleep(0.5)

            # Read response
            response = ""
            while self.arduino.in_waiting:
                response += self.arduino.read(self.arduino.in_waiting).decode('utf-8', errors='ignore')
                time.sleep(0.1)

            if response:
                self.print_result("Arduino Response", True,
                                f"Arduino is responding ({len(response)} bytes)")
                print(f"\n>>> Arduino says:\n{response[:200]}")
            else:
                self.warnings.append("No response from Arduino - might be using basic version")
                self.print_result("Arduino Response", True,
                                "Connected but no response (basic version?)")

            return True

        except Exception as e:
            self.print_result("Serial Communication", False, str(e))
            return False

    def test_motor_commands(self):
        """Test if motor commands work"""
        self.print_header("TEST 4: Motor Command Test")

        if not self.arduino:
            self.print_result("Motor Test", False, "Arduino not connected")
            return False

        print("\n>>> Testing motor commands...")
        print("Watch your vehicle - motors should activate briefly")

        tests = [
            ("Forward", "F:150\n", "Motors should move forward"),
            ("Stop", "S\n", "Motors should stop"),
            ("Left", "L:10:150\n", "Should turn slightly left"),
            ("Stop", "S\n", "Motors should stop"),
            ("Right", "R:10:150\n", "Should turn slightly right"),
            ("Stop", "S\n", "Motors should stop")
        ]

        all_passed = True
        for test_name, command, description in tests:
            print(f"\n{description}")
            input("Press ENTER to send command (or Ctrl+C to skip)...")

            try:
                self.arduino.write(command.encode())
                time.sleep(1)

                response = input("Did the motors respond correctly? (y/n): ").lower()
                if response == 'y':
                    self.print_result(f"Motor {test_name}", True)
                else:
                    self.print_result(f"Motor {test_name}", False,
                                    "Motors did not respond as expected")
                    all_passed = False

            except KeyboardInterrupt:
                print("\nSkipping remaining motor tests...")
                break
            except Exception as e:
                self.print_result(f"Motor {test_name}", False, str(e))
                all_passed = False

        # Final stop
        self.arduino.write(b"S\n")

        return all_passed

    def test_motor_controller_module(self):
        """Test the motor controller Python module"""
        self.print_header("TEST 5: Motor Controller Module")

        try:
            from motor_controller import MotorController

            # Find Arduino port
            port = None
            if self.arduino and self.arduino.is_open:
                port = self.arduino.port
                self.arduino.close()
            else:
                # Try to find port
                for p in ["/dev/ttyUSB0", "/dev/ttyACM0", "COM3"]:
                    try:
                        test_ser = serial.Serial(p, 9600, timeout=1)
                        port = p
                        test_ser.close()
                        break
                    except:
                        continue

            if not port:
                self.print_result("Motor Controller Module", False,
                                "Cannot find Arduino port")
                return False

            config = {'port': port, 'baudrate': 9600, 'max_speed': 150}
            controller = MotorController(config)

            self.print_result("Motor Controller Import", True,
                            "MotorController module loaded successfully")

            print("\n>>> Testing MotorController methods...")
            input("Press ENTER to test forward movement...")
            controller.forward(100)
            time.sleep(1)
            controller.stop()

            response = input("Did motors move forward? (y/n): ").lower()
            if response == 'y':
                self.print_result("MotorController.forward()", True)
            else:
                self.print_result("MotorController.forward()", False)

            return True

        except ImportError as e:
            self.print_result("Motor Controller Module", False,
                            f"Cannot import MotorController: {e}")
            return False
        except Exception as e:
            self.print_result("Motor Controller Module", False, str(e))
            return False

    def check_wiring(self):
        """Provide wiring checklist"""
        self.print_header("HARDWARE CHECKLIST")

        print("""
Please verify the following connections:

ARDUINO CONNECTIONS:
  ☐ Pin 2  → Left Motor Forward (IN1)
  ☐ Pin 3  → Left Motor Backward (IN2)
  ☐ Pin 4  → Right Motor Forward (IN3)
  ☐ Pin 5  → Right Motor Backward (IN4)
  ☐ Pin 9  → Left Motor Enable (ENA) - PWM
  ☐ Pin 10 → Right Motor Enable (ENB) - PWM
  ☐ GND    → Motor Driver GND
  ☐ 5V/VCC → Motor Driver Logic Power (if needed)

MOTOR DRIVER:
  ☐ Motor power supply connected (usually 6-12V)
  ☐ Motors connected to output terminals
  ☐ Power switch ON

CAMERA:
  ☐ USB camera plugged into computer/Raspberry Pi
  ☐ Camera has clear view of track/line

POWER:
  ☐ Arduino powered via USB or external supply
  ☐ Motor driver has adequate power supply
  ☐ All grounds connected together
        """)

    def print_summary(self):
        """Print diagnostic summary"""
        self.print_header("DIAGNOSTIC SUMMARY")

        if not self.issues:
            print("✓ All tests passed!")
        else:
            print(f"✗ Found {len(self.issues)} issue(s):\n")
            for i, issue in enumerate(self.issues, 1):
                print(f"{i}. {issue}")

        if self.warnings:
            print(f"\n⚠ {len(self.warnings)} warning(s):\n")
            for i, warning in enumerate(self.warnings, 1):
                print(f"{i}. {warning}")

        print("\n" + "="*60)
        print("NEXT STEPS:")
        print("="*60)

        if self.issues:
            print("\n1. Fix the issues listed above")
            print("2. Check hardware connections (see checklist above)")
            print("3. Verify Arduino code is uploaded")
            print("4. Run this diagnostic again")
        else:
            print("\n1. Test with: python3 ../src/main.py")
            print("2. Make sure debug mode is enabled in config.yaml")
            print("3. Check that a black line is visible to camera")
            print("4. Monitor serial output from Arduino")

    def cleanup(self):
        """Clean up resources"""
        if self.camera:
            self.camera.release()
        if self.arduino and self.arduino.is_open:
            self.arduino.write(b"S\n")  # Stop motors
            self.arduino.close()
        cv2.destroyAllWindows()

    def run(self):
        """Run complete diagnostic"""
        print("\n")
        print("*" * 60)
        print("*" + " " * 58 + "*")
        print("*" + "  CAMERA VEHICLE DIAGNOSTIC TOOL".center(58) + "*")
        print("*" + " " * 58 + "*")
        print("*" * 60)

        try:
            # Run tests
            self.test_camera_connection()
            self.test_arduino_connection()

            if self.arduino:
                self.test_serial_communication()
                self.test_motor_commands()
                # Uncomment to test motor controller module
                # self.test_motor_controller_module()

            self.check_wiring()
            self.print_summary()

        except KeyboardInterrupt:
            print("\n\nDiagnostic interrupted by user")
        except Exception as e:
            print(f"\n\nUnexpected error: {e}")
        finally:
            self.cleanup()

if __name__ == "__main__":
    diagnostic = SystemDiagnostic()
    diagnostic.run()
