#!/usr/bin/env python3
"""
Camera-based Autonomous Vehicle
Main control program
"""

import sys
import signal
import yaml
from camera_controller import CameraController
from lane_detector import LaneDetector
from motor_controller import MotorController
from pid_controller import PIDController
from data_logger import DataLogger

class CameraVehicle:
    def __init__(self, config_file='config.yaml'):
        # Load configuration
        with open(config_file, 'r') as f:
            self.config = yaml.safe_load(f)
        
        # Initialize components
        print("Initializing camera vehicle...")
        self.camera = CameraController(self.config['camera'])
        self.lane_detector = LaneDetector(self.config['lane_detection'])
        self.motor_controller = MotorController(self.config['arduino'])
        self.pid = PIDController(self.config['pid'])
        self.logger = DataLogger(self.config['logging'])
        
        # Control flags
        self.running = False
        self.debug_mode = self.config.get('debug', False)
        
        # Setup signal handler for clean shutdown
        signal.signal(signal.SIGINT, self.signal_handler)
    
    def signal_handler(self, sig, frame):
        print("\n[INFO] Shutdown signal received")
        self.shutdown()
        sys.exit(0)
    
    def run(self):
        """Main control loop"""
        self.running = True
        print("[INFO] Starting autonomous navigation...")
        
        frame_count = 0
        lost_line_count = 0
        
        while self.running:
            # Capture frame
            frame = self.camera.get_frame()
            if frame is None:
                continue
            
            frame_count += 1
            
            # Detect lane
            line_position, confidence, processed_frame = self.lane_detector.detect(frame)
            
            if confidence > self.config['lane_detection']['min_confidence']:
                # Line found - calculate error and control
                error = line_position - (frame.shape[1] // 2)
                
                # PID control
                steering_angle = self.pid.compute(error)
                
                # Send motor command
                self.motor_controller.steer(steering_angle)
                
                # Log data
                self.logger.log_frame(frame_count, error, steering_angle, confidence)
                
                # Reset lost counter
                lost_line_count = 0
                
                if self.debug_mode:
                    print(f"Frame {frame_count}: Error={error:.1f}px, Steering={steering_angle:.1f}°")
            
            else:
                # Line lost
                lost_line_count += 1
                
                if lost_line_count > 5:  # Lost for 5 frames
                    print("[WARNING] Line lost - stopping")
                    self.motor_controller.stop()
                    self.logger.log_event("line_lost")
            
            # Show debug visualization if enabled
            if self.debug_mode:
                self.camera.show_debug(processed_frame, line_position, confidence)
                if self.camera.check_quit():
                    break
    
    def shutdown(self):
        """Clean shutdown"""
        print("[INFO] Shutting down...")
        self.running = False
        self.motor_controller.stop()
        self.camera.cleanup()
        self.logger.save_summary()
        print("[INFO] Shutdown complete")

if __name__ == "__main__":
    vehicle = CameraVehicle()
    vehicle.run()
