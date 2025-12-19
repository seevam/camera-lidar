"""Data Logger for recording vehicle operation data"""

import os
import csv
import json
from datetime import datetime
import time

class DataLogger:
    def __init__(self, config):
        """
        Initialize data logger

        Args:
            config: Dictionary with enabled, log_dir, save_video settings
        """
        self.enabled = config.get('enabled', True)
        self.log_dir = config.get('log_dir', 'data/logs')
        self.save_video = config.get('save_video', False)

        # Create log directory if enabled
        if self.enabled:
            os.makedirs(self.log_dir, exist_ok=True)

            # Create session timestamp
            self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")

            # Initialize log files
            self.frame_log_path = os.path.join(self.log_dir, f"frames_{self.session_id}.csv")
            self.event_log_path = os.path.join(self.log_dir, f"events_{self.session_id}.txt")
            self.summary_path = os.path.join(self.log_dir, f"summary_{self.session_id}.json")

            # Initialize CSV file
            self._init_csv()

            # Session statistics
            self.stats = {
                'start_time': time.time(),
                'end_time': None,
                'total_frames': 0,
                'frames_with_line': 0,
                'frames_lost_line': 0,
                'total_error': 0,
                'max_error': 0,
                'events': []
            }

            print(f"[INFO] Data logging enabled: {self.log_dir}")
            print(f"[INFO] Session ID: {self.session_id}")
        else:
            print("[INFO] Data logging disabled")

    def _init_csv(self):
        """Initialize CSV file with headers"""
        with open(self.frame_log_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                'frame_number',
                'timestamp',
                'error_px',
                'steering_angle',
                'confidence',
                'line_detected'
            ])

    def log_frame(self, frame_number, error, steering_angle, confidence):
        """
        Log frame data

        Args:
            frame_number: Frame counter
            error: Tracking error in pixels
            steering_angle: Computed steering angle
            confidence: Line detection confidence
        """
        if not self.enabled:
            return

        timestamp = time.time()
        line_detected = confidence > 0

        # Write to CSV
        with open(self.frame_log_path, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                frame_number,
                f"{timestamp:.3f}",
                f"{error:.2f}",
                f"{steering_angle:.2f}",
                f"{confidence:.3f}",
                line_detected
            ])

        # Update statistics
        self.stats['total_frames'] += 1
        if line_detected:
            self.stats['frames_with_line'] += 1
        else:
            self.stats['frames_lost_line'] += 1

        self.stats['total_error'] += abs(error)
        if abs(error) > self.stats['max_error']:
            self.stats['max_error'] = abs(error)

    def log_event(self, event_name, details=None):
        """
        Log an event

        Args:
            event_name: Name of the event
            details: Optional additional details (dict or string)
        """
        if not self.enabled:
            return

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        event_entry = f"[{timestamp}] {event_name}"

        if details:
            if isinstance(details, dict):
                event_entry += f": {json.dumps(details)}"
            else:
                event_entry += f": {details}"

        # Write to event log
        with open(self.event_log_path, 'a') as f:
            f.write(event_entry + '\n')

        # Add to stats
        self.stats['events'].append({
            'timestamp': timestamp,
            'event': event_name,
            'details': details
        })

        print(f"[EVENT] {event_entry}")

    def save_summary(self):
        """Save session summary"""
        if not self.enabled:
            return

        self.stats['end_time'] = time.time()

        # Calculate duration
        duration = self.stats['end_time'] - self.stats['start_time']

        # Calculate averages
        if self.stats['total_frames'] > 0:
            avg_error = self.stats['total_error'] / self.stats['total_frames']
            line_detection_rate = self.stats['frames_with_line'] / self.stats['total_frames']
        else:
            avg_error = 0
            line_detection_rate = 0

        # Create summary
        summary = {
            'session_id': self.session_id,
            'duration_seconds': duration,
            'total_frames': self.stats['total_frames'],
            'frames_with_line': self.stats['frames_with_line'],
            'frames_lost_line': self.stats['frames_lost_line'],
            'line_detection_rate': line_detection_rate,
            'average_error_px': avg_error,
            'max_error_px': self.stats['max_error'],
            'events': self.stats['events']
        }

        # Save to JSON
        with open(self.summary_path, 'w') as f:
            json.dump(summary, f, indent=2)

        # Print summary
        print("\n" + "="*60)
        print("SESSION SUMMARY")
        print("="*60)
        print(f"Session ID: {self.session_id}")
        print(f"Duration: {duration:.1f} seconds")
        print(f"Total Frames: {self.stats['total_frames']}")
        print(f"Line Detection Rate: {line_detection_rate*100:.1f}%")
        print(f"Average Error: {avg_error:.2f} px")
        print(f"Max Error: {self.stats['max_error']:.2f} px")
        print(f"Events: {len(self.stats['events'])}")
        print("="*60)
        print(f"Logs saved to: {self.log_dir}")
        print("="*60 + "\n")

    def get_stats(self):
        """Get current statistics"""
        return self.stats.copy()
