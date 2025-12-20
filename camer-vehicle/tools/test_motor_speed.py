#!/usr/bin/env python3
"""
Motor Speed Test Tool
Find the optimal motor speed for your vehicle
"""

import serial
import time
import sys

class MotorSpeedTester:
    def __init__(self, port='/dev/ttyUSB0', baudrate=9600):
        self.port = port
        self.baudrate = baudrate
        self.arduino = None

    def connect(self):
        """Connect to Arduino"""
        try:
            print(f"Connecting to Arduino on {self.port}...")
            self.arduino = serial.Serial(self.port, self.baudrate, timeout=2)
            time.sleep(2)  # Wait for Arduino reset
            print("✓ Connected!")
            return True
        except Exception as e:
            print(f"✗ Connection failed: {e}")
            return False

    def test_speed(self, speed, duration=3):
        """Test motors at specific speed"""
        if not self.arduino:
            return

        print(f"\nTesting speed: {speed}/255")
        print("="*50)

        # Send forward command
        command = f"F:{speed}\n"
        self.arduino.write(command.encode())

        print(f"Motors running at {speed} for {duration} seconds...")
        print("Watch your vehicle!")

        time.sleep(duration)

        # Stop motors
        self.arduino.write(b"S\n")
        print("Motors stopped")

    def find_minimum_speed(self):
        """Find minimum speed needed to move vehicle"""
        print("\n" + "="*50)
        print("FINDING MINIMUM SPEED TO MOVE")
        print("="*50)
        print("\nThis will test increasing speeds to find the")
        print("minimum speed needed to move your vehicle.\n")

        # Test speeds from 50 to 255 in steps of 20
        test_speeds = list(range(50, 256, 20))

        for speed in test_speeds:
            self.test_speed(speed, duration=2)

            response = input(f"\nDid vehicle move? (y/n/q to quit): ").lower()

            if response == 'y':
                print(f"\n✓ Minimum speed found: {speed}")
                print(f"Recommended max_speed in config.yaml: {min(speed + 50, 255)}")
                return speed
            elif response == 'q':
                print("Test cancelled")
                return None

        print("\n✗ Vehicle didn't move even at maximum speed!")
        print("Check power supply and motor connections.")
        return None

    def progressive_speed_test(self):
        """Run progressive speed test"""
        print("\n" + "="*50)
        print("PROGRESSIVE SPEED TEST")
        print("="*50)

        speeds = [100, 150, 200, 220, 240, 255]

        for speed in speeds:
            self.test_speed(speed, duration=2)

            response = input("\nContinue to next speed? (y/n): ").lower()
            if response != 'y':
                break

        print("\nTest complete!")

    def manual_test(self):
        """Manual speed testing"""
        print("\n" + "="*50)
        print("MANUAL SPEED TEST")
        print("="*50)
        print("Enter speed values (0-255) to test")
        print("Type 'q' to quit\n")

        while True:
            try:
                speed_input = input("Enter speed (0-255): ").strip()

                if speed_input.lower() == 'q':
                    break

                speed = int(speed_input)

                if speed < 0 or speed > 255:
                    print("Speed must be between 0 and 255")
                    continue

                duration = input("Duration in seconds [3]: ").strip()
                duration = int(duration) if duration else 3

                self.test_speed(speed, duration)

            except ValueError:
                print("Invalid input!")
            except KeyboardInterrupt:
                print("\nTest interrupted")
                break

    def power_check(self):
        """Check if power supply is adequate"""
        print("\n" + "="*50)
        print("POWER SUPPLY CHECK")
        print("="*50)
        print("""
Please verify:

Motor Driver Power:
  ☐ Voltage: 6-12V DC (measure with multimeter)
  ☐ Current capacity: At least 1A (preferably 2A+)
  ☐ Battery fresh/charged
  ☐ Power switch ON
  ☐ Power LED on motor driver lit

Common Issues:
  ✗ USB power alone - NOT enough for motors!
  ✗ Weak batteries - Replace or recharge
  ✗ Loose power connections
  ✗ Insufficient current capacity

Solutions:
  ✓ Use 6V-12V battery pack (4-8 AA batteries)
  ✓ Use 7.4V LiPo battery
  ✓ Use 9V-12V DC power adapter (1A+)
  ✓ Ensure common ground (Arduino + Motor driver)
        """)

        input("\nPress Enter to continue...")

    def cleanup(self):
        """Stop motors and close connection"""
        if self.arduino:
            self.arduino.write(b"S\n")
            time.sleep(0.5)
            self.arduino.close()
            print("\n✓ Connection closed")

    def run(self):
        """Main menu"""
        if not self.connect():
            return

        try:
            while True:
                print("\n" + "="*50)
                print("MOTOR SPEED TEST TOOL")
                print("="*50)
                print("\nOptions:")
                print("  1. Find minimum speed to move")
                print("  2. Progressive speed test (100→255)")
                print("  3. Manual speed test")
                print("  4. Power supply check")
                print("  0. Exit")

                choice = input("\nSelect option: ").strip()

                if choice == '0':
                    break
                elif choice == '1':
                    self.find_minimum_speed()
                elif choice == '2':
                    self.progressive_speed_test()
                elif choice == '3':
                    self.manual_test()
                elif choice == '4':
                    self.power_check()
                else:
                    print("Invalid option")

        except KeyboardInterrupt:
            print("\n\nTest interrupted")
        finally:
            self.cleanup()

def main():
    print("="*50)
    print("  MOTOR SPEED TEST TOOL")
    print("="*50)

    # Try to find Arduino port
    ports_to_try = [
        '/dev/ttyUSB0',
        '/dev/ttyUSB1',
        '/dev/ttyACM0',
        '/dev/ttyACM1',
        'COM3',
        'COM4'
    ]

    port = None
    if len(sys.argv) > 1:
        port = sys.argv[1]
    else:
        print("\nSearching for Arduino...")
        for p in ports_to_try:
            try:
                test = serial.Serial(p, 9600, timeout=1)
                test.close()
                port = p
                print(f"Found Arduino on {p}")
                break
            except:
                continue

    if not port:
        print("\n✗ Could not find Arduino automatically")
        port = input("Enter Arduino port: ").strip()

    tester = MotorSpeedTester(port)
    tester.run()

if __name__ == "__main__":
    main()
