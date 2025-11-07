#!/usr/bin/env python3
"""
LiDAR Vehicle Data Collector
Collects data from Arduino/ESP32 via serial connection
Saves data for analysis and comparison with camera system
"""

import serial
import time
import csv
import os
from datetime import datetime
import argparse

class LidarDataCollector:
    def __init__(self, port='/dev/ttyUSB0', baudrate=115200, output_dir='data/raw'):
        """
        Initialize data collector
        
        Args:
            port: Serial port for Arduino/ESP32
            baudrate: Serial communication speed
            output_dir: Directory to save raw data
        """
        self.port = port
        self.baudrate = baudrate
        self.output_dir = output_dir
        self.serial_conn = None
        self.current_trial_file = None
        self.current_csv_writer = None
        self.trial_active = False
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
    def connect(self):
        """Connect to Arduino/ESP32"""
        try:
            self.serial_conn = serial.Serial(self.port, self.baudrate, timeout=1)
            time.sleep(2)  # Wait for Arduino to reset
            print(f"Connected to {self.port} at {self.baudrate} baud")
            return True
        except serial.SerialException as e:
            print(f"Error connecting to {self.port}: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from Arduino/ESP32"""
        if self.serial_conn and self.serial_conn.is_open:
            self.serial_conn.close()
            print("Disconnected")
    
    def send_command(self, command):
        """Send command to vehicle"""
        if self.serial_conn and self.serial_conn.is_open:
            self.serial_conn.write(f"{command}\n".encode())
            print(f"Sent: {command}")
        else:
            print("Not connected!")
    
    def start_trial(self, light_condition):
        """
        Start a new trial
        
        Args:
            light_condition: 'bright', 'medium', or 'low'
        """
        if light_condition not in ['bright', 'medium', 'low']:
            print("Invalid light condition! Use: bright, medium, or low")
            return
        
        # Create filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"lidar_{light_condition}_{timestamp}.csv"
        filepath = os.path.join(self.output_dir, filename)
        
        # Open CSV file
        self.current_trial_file = open(filepath, 'w', newline='')
        self.current_csv_writer = csv.writer(self.current_trial_file)
        
        # Write header
        self.current_csv_writer.writerow([
            'timestamp', 'deviation_mm', 'cumulative_collisions', 
            'light_condition', 'sensor_type'
        ])
        
        # Send start command to vehicle
        command = f"START_{light_condition.upper()}"
        self.send_command(command)
        
        self.trial_active = True
        print(f"\nTrial started: {light_condition}")
        print(f"Data file: {filepath}")
        print("Recording data...")
        
    def stop_trial(self):
        """Stop current trial"""
        if self.trial_active:
            self.send_command("STOP")
            
            if self.current_trial_file:
                self.current_trial_file.close()
                print("\nTrial stopped and data saved")
            
            self.trial_active = False
            self.current_trial_file = None
            self.current_csv_writer = None
        else:
            print("No active trial")
    
    def collect_data(self, duration_seconds=120):
        """
        Collect data for specified duration
        
        Args:
            duration_seconds: How long to collect data (default 2 minutes)
        """
        if not self.trial_active:
            print("No active trial! Start a trial first.")
            return
        
        start_time = time.time()
        data_count = 0
        
        try:
            while time.time() - start_time < duration_seconds:
                if self.serial_conn.in_waiting:
                    line = self.serial_conn.readline().decode('utf-8').strip()
                    
                    # Process different message types
                    if line.startswith("DATA,"):
                        # Data line: DATA,timestamp,deviation,collisions,mode
                        parts = line.split(',')
                        if len(parts) >= 5:
                            timestamp = parts[1]
                            deviation = parts[2]
                            collisions = parts[3]
                            mode = parts[4]
                            
                            # Write to CSV
                            self.current_csv_writer.writerow([
                                timestamp, deviation, collisions, mode, 'lidar'
                            ])
                            self.current_trial_file.flush()  # Ensure data is written
                            
                            data_count += 1
                            
                            # Print progress
                            if data_count % 10 == 0:
                                elapsed = time.time() - start_time
                                print(f"  {data_count} data points | "
                                      f"Elapsed: {elapsed:.1f}s | "
                                      f"Collisions: {collisions}")
                    
                    elif line.startswith("TRIAL_END"):
                        print("\nTrial ended by vehicle")
                        break
                    
                    elif line.startswith("!!!"):
                        print(f"  {line}")  # Print collision warnings
                    
                    else:
                        # Print other messages (debug info)
                        if line and not line.startswith("L:"):
                            print(f"  {line}")
        
        except KeyboardInterrupt:
            print("\n\nData collection interrupted by user")
        
        finally:
            print(f"\nCollected {data_count} data points")
            self.stop_trial()
    
    def run_automated_trials(self, conditions=['bright', 'medium', 'low'], 
                           duration=120, delay_between=30):
        """
        Run automated trials for all conditions
        
        Args:
            conditions: List of light conditions to test
            duration: Duration of each trial in seconds
            delay_between: Delay between trials in seconds
        """
        print("\n" + "="*50)
        print("AUTOMATED LIDAR TESTING")
        print("="*50)
        print(f"Conditions: {conditions}")
        print(f"Duration per trial: {duration}s ({duration/60:.1f} min)")
        print(f"Delay between trials: {delay_between}s")
        print(f"Total estimated time: "
              f"{(duration + delay_between) * len(conditions) / 60:.1f} min")
        print("="*50 + "\n")
        
        input("Position vehicle at start. Press Enter to begin...")
        
        for i, condition in enumerate(conditions):
            print(f"\n{'='*50}")
            print(f"TRIAL {i+1}/{len(conditions)}: {condition.upper()}")
            print(f"{'='*50}")
            
            # Start trial
            self.start_trial(condition)
            time.sleep(2)  # Wait for vehicle to start
            
            # Collect data
            self.collect_data(duration)
            
            # Delay before next trial (except for last one)
            if i < len(conditions) - 1:
                print(f"\nWaiting {delay_between}s before next trial...")
                print("Reposition vehicle if needed.")
                time.sleep(delay_between)
        
        print("\n" + "="*50)
        print("ALL TRIALS COMPLETED!")
        print("="*50 + "\n")

def main():
    parser = argparse.ArgumentParser(
        description='Collect data from LiDAR autonomous vehicle'
    )
    parser.add_argument(
        '--port', 
        default='/dev/ttyUSB0',
        help='Serial port (default: /dev/ttyUSB0)'
    )
    parser.add_argument(
        '--baudrate', 
        type=int, 
        default=115200,
        help='Serial baudrate (default: 115200)'
    )
    parser.add_argument(
        '--mode',
        choices=['manual', 'auto'],
        default='manual',
        help='Manual or automated testing (default: manual)'
    )
    parser.add_argument(
        '--duration',
        type=int,
        default=120,
        help='Trial duration in seconds (default: 120)'
    )
    
    args = parser.parse_args()
    
    # Create collector
    collector = LidarDataCollector(port=args.port, baudrate=args.baudrate)
    
    # Connect
    if not collector.connect():
        return
    
    try:
        if args.mode == 'auto':
            # Automated testing
            collector.run_automated_trials(
                conditions=['bright', 'medium', 'low'],
                duration=args.duration
            )
        else:
            # Manual mode - interactive
            print("\n" + "="*50)
            print("LIDAR DATA COLLECTOR - MANUAL MODE")
            print("="*50)
            print("\nCommands:")
            print("  start <condition>  - Start trial (bright/medium/low)")
            print("  stop              - Stop current trial")
            print("  status            - Check vehicle status")
            print("  quit              - Exit program")
            print("="*50 + "\n")
            
            while True:
                cmd = input("Enter command: ").strip().lower()
                
                if cmd.startswith('start'):
                    parts = cmd.split()
                    if len(parts) < 2:
                        print("Usage: start <bright|medium|low>")
                        continue
                    condition = parts[1]
                    collector.start_trial(condition)
                    collector.collect_data(args.duration)
                
                elif cmd == 'stop':
                    collector.stop_trial()
                
                elif cmd == 'status':
                    collector.send_command('STATUS')
                    time.sleep(0.5)
                    # Read response
                    while collector.serial_conn.in_waiting:
                        print(collector.serial_conn.readline().decode('utf-8').strip())
                
                elif cmd in ['quit', 'exit', 'q']:
                    break
                
                else:
                    print("Unknown command")
    
    except KeyboardInterrupt:
        print("\n\nExiting...")
    
    finally:
        collector.stop_trial()
        collector.disconnect()

if __name__ == "__main__":
    main()
