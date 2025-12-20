#!/usr/bin/env python3
"""
Data Analysis Tool for Camera Vehicle Trial Data
Analyze and visualize logged trial data
"""

import os
import json
import csv
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
import glob

class TrialDataAnalyzer:
    def __init__(self, log_dir="data/logs"):
        self.log_dir = log_dir
        self.sessions = []
        self.load_sessions()

    def load_sessions(self):
        """Find all logged sessions"""
        if not os.path.exists(self.log_dir):
            print(f"[WARNING] Log directory not found: {self.log_dir}")
            return

        # Find all summary files
        summary_files = glob.glob(os.path.join(self.log_dir, "summary_*.json"))

        for summary_file in sorted(summary_files):
            session_id = os.path.basename(summary_file).replace("summary_", "").replace(".json", "")
            self.sessions.append({
                'id': session_id,
                'summary_file': summary_file,
                'frames_file': os.path.join(self.log_dir, f"frames_{session_id}.csv"),
                'events_file': os.path.join(self.log_dir, f"events_{session_id}.txt")
            })

        print(f"[INFO] Found {len(self.sessions)} session(s)")

    def list_sessions(self):
        """List all available sessions"""
        if not self.sessions:
            print("No sessions found!")
            return

        print("\n" + "="*80)
        print("AVAILABLE SESSIONS")
        print("="*80)

        for i, session in enumerate(self.sessions, 1):
            # Load summary
            with open(session['summary_file'], 'r') as f:
                summary = json.load(f)

            duration = summary.get('duration_seconds', 0)
            frames = summary.get('total_frames', 0)
            detection_rate = summary.get('line_detection_rate', 0) * 100

            print(f"\n{i}. Session: {session['id']}")
            print(f"   Duration: {duration:.1f}s")
            print(f"   Frames: {frames}")
            print(f"   Line Detection: {detection_rate:.1f}%")

        print("\n" + "="*80)

    def analyze_session(self, session_index=0):
        """Analyze a specific session"""
        if session_index >= len(self.sessions):
            print(f"[ERROR] Session {session_index} not found")
            return None

        session = self.sessions[session_index]

        # Load summary
        with open(session['summary_file'], 'r') as f:
            summary = json.load(f)

        # Load frame data
        frames_data = []
        if os.path.exists(session['frames_file']):
            with open(session['frames_file'], 'r') as f:
                reader = csv.DictReader(f)
                frames_data = list(reader)

        # Load events
        events = []
        if os.path.exists(session['events_file']):
            with open(session['events_file'], 'r') as f:
                events = f.readlines()

        return {
            'summary': summary,
            'frames': frames_data,
            'events': events,
            'session': session
        }

    def print_summary(self, session_index=0):
        """Print detailed session summary"""
        data = self.analyze_session(session_index)
        if not data:
            return

        summary = data['summary']

        print("\n" + "="*80)
        print("SESSION ANALYSIS")
        print("="*80)
        print(f"Session ID: {summary['session_id']}")
        print(f"Duration: {summary['duration_seconds']:.2f} seconds")
        print(f"\nFrame Statistics:")
        print(f"  Total Frames: {summary['total_frames']}")
        print(f"  Frames with Line: {summary['frames_with_line']}")
        print(f"  Frames Lost Line: {summary['frames_lost_line']}")
        print(f"  Detection Rate: {summary['line_detection_rate']*100:.2f}%")
        print(f"\nTracking Performance:")
        print(f"  Average Error: {summary['average_error_px']:.2f} pixels")
        print(f"  Max Error: {summary['max_error_px']:.2f} pixels")

        if summary.get('events'):
            print(f"\nEvents ({len(summary['events'])}):")
            for event in summary['events']:
                print(f"  - {event['event']}: {event.get('details', 'N/A')}")

        print("="*80)

    def plot_session(self, session_index=0, save_plot=False):
        """Plot session data"""
        data = self.analyze_session(session_index)
        if not data or not data['frames']:
            print("[ERROR] No frame data to plot")
            return

        frames = data['frames']

        # Extract data
        frame_numbers = [int(f['frame_number']) for f in frames]
        errors = [float(f['error_px']) for f in frames]
        steering = [float(f['steering_angle']) for f in frames]
        confidence = [float(f['confidence']) for f in frames]

        # Create plots
        fig, axes = plt.subplots(3, 1, figsize=(12, 10))
        fig.suptitle(f"Session Analysis: {data['summary']['session_id']}", fontsize=14)

        # Plot 1: Tracking Error
        axes[0].plot(frame_numbers, errors, 'b-', linewidth=0.5)
        axes[0].axhline(y=0, color='r', linestyle='--', alpha=0.5)
        axes[0].set_ylabel('Error (pixels)')
        axes[0].set_title('Tracking Error Over Time')
        axes[0].grid(True, alpha=0.3)

        # Plot 2: Steering Angle
        axes[1].plot(frame_numbers, steering, 'g-', linewidth=0.5)
        axes[1].axhline(y=0, color='r', linestyle='--', alpha=0.5)
        axes[1].set_ylabel('Steering Angle (degrees)')
        axes[1].set_title('Steering Commands')
        axes[1].grid(True, alpha=0.3)

        # Plot 3: Confidence
        axes[2].plot(frame_numbers, confidence, 'orange', linewidth=0.5)
        axes[2].axhline(y=0.3, color='r', linestyle='--', alpha=0.5, label='Min Confidence')
        axes[2].set_ylabel('Confidence')
        axes[2].set_xlabel('Frame Number')
        axes[2].set_title('Line Detection Confidence')
        axes[2].legend()
        axes[2].grid(True, alpha=0.3)

        plt.tight_layout()

        if save_plot:
            filename = f"analysis_{data['summary']['session_id']}.png"
            plt.savefig(filename, dpi=150)
            print(f"[INFO] Plot saved as {filename}")

        plt.show()

    def compare_sessions(self, indices=None):
        """Compare multiple sessions"""
        if indices is None:
            indices = range(len(self.sessions))

        print("\n" + "="*80)
        print("SESSION COMPARISON")
        print("="*80)
        print(f"{'Session':<20} {'Duration':<12} {'Frames':<10} {'Detection':<12} {'Avg Error':<12}")
        print("-"*80)

        for idx in indices:
            if idx >= len(self.sessions):
                continue

            data = self.analyze_session(idx)
            if not data:
                continue

            summary = data['summary']
            print(f"{summary['session_id']:<20} "
                  f"{summary['duration_seconds']:>8.1f}s    "
                  f"{summary['total_frames']:>6}    "
                  f"{summary['line_detection_rate']*100:>8.1f}%    "
                  f"{summary['average_error_px']:>8.2f}px")

        print("="*80)

    def export_to_excel(self, session_index=0):
        """Export session data to Excel format (CSV)"""
        data = self.analyze_session(session_index)
        if not data:
            return

        session_id = data['summary']['session_id']
        output_file = f"export_{session_id}.csv"

        # Frame data already in CSV, just copy with analysis
        with open(output_file, 'w', newline='') as f:
            writer = csv.writer(f)

            # Write summary header
            writer.writerow(['SESSION SUMMARY'])
            writer.writerow(['Session ID', session_id])
            writer.writerow(['Duration (s)', data['summary']['duration_seconds']])
            writer.writerow(['Total Frames', data['summary']['total_frames']])
            writer.writerow(['Detection Rate (%)', data['summary']['line_detection_rate']*100])
            writer.writerow(['Average Error (px)', data['summary']['average_error_px']])
            writer.writerow(['Max Error (px)', data['summary']['max_error_px']])
            writer.writerow([])

            # Write frame data
            writer.writerow(['FRAME DATA'])
            if data['frames']:
                writer.writerow(data['frames'][0].keys())
                for frame in data['frames']:
                    writer.writerow(frame.values())

        print(f"[INFO] Exported to {output_file}")

    def clean_old_logs(self, keep_recent=5):
        """Delete old log files, keeping only recent sessions"""
        if len(self.sessions) <= keep_recent:
            print(f"[INFO] Only {len(self.sessions)} sessions, nothing to clean")
            return

        # Sort by session ID (which includes timestamp)
        sorted_sessions = sorted(self.sessions, key=lambda x: x['id'], reverse=True)

        # Sessions to delete
        to_delete = sorted_sessions[keep_recent:]

        print(f"\n[WARNING] About to delete {len(to_delete)} old session(s):")
        for session in to_delete:
            print(f"  - {session['id']}")

        confirm = input("\nProceed? (yes/no): ")
        if confirm.lower() != 'yes':
            print("Cancelled")
            return

        # Delete files
        for session in to_delete:
            for key in ['summary_file', 'frames_file', 'events_file']:
                if os.path.exists(session[key]):
                    os.remove(session[key])
                    print(f"[INFO] Deleted {os.path.basename(session[key])}")

        print(f"[INFO] Cleanup complete. {keep_recent} sessions retained.")

def main():
    import sys

    analyzer = TrialDataAnalyzer()

    if not analyzer.sessions:
        print("\n[INFO] No trial data found yet.")
        print("Trial data will be created when you run: python3 src/main.py")
        return

    print("\n" + "="*80)
    print("TRIAL DATA ANALYSIS TOOL")
    print("="*80)

    while True:
        print("\nOptions:")
        print("  1. List all sessions")
        print("  2. Show session summary")
        print("  3. Plot session data")
        print("  4. Compare sessions")
        print("  5. Export session to CSV")
        print("  6. Clean old logs")
        print("  0. Exit")

        choice = input("\nSelect option: ").strip()

        if choice == '0':
            break

        elif choice == '1':
            analyzer.list_sessions()

        elif choice == '2':
            analyzer.list_sessions()
            idx = int(input("\nEnter session number: ")) - 1
            analyzer.print_summary(idx)

        elif choice == '3':
            analyzer.list_sessions()
            idx = int(input("\nEnter session number: ")) - 1
            save = input("Save plot? (y/n): ").lower() == 'y'
            analyzer.plot_session(idx, save_plot=save)

        elif choice == '4':
            analyzer.compare_sessions()

        elif choice == '5':
            analyzer.list_sessions()
            idx = int(input("\nEnter session number: ")) - 1
            analyzer.export_to_excel(idx)

        elif choice == '6':
            keep = int(input("\nHow many recent sessions to keep? [5]: ") or "5")
            analyzer.clean_old_logs(keep)
            analyzer.load_sessions()  # Reload

        else:
            print("Invalid option")

if __name__ == "__main__":
    main()
