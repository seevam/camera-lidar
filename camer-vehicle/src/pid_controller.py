"""PID Controller for steering control"""

import time

class PIDController:
    def __init__(self, config):
        """
        Initialize PID controller

        Args:
            config: Dictionary with kp, ki, kd, and max_output
        """
        self.kp = config.get('kp', 0.5)
        self.ki = config.get('ki', 0.0)
        self.kd = config.get('kd', 0.1)
        self.max_output = config.get('max_output', 45)

        # PID state variables
        self.previous_error = 0
        self.integral = 0
        self.last_time = None

        # Anti-windup limits
        self.integral_max = 100

        print(f"[INFO] PID initialized: Kp={self.kp}, Ki={self.ki}, Kd={self.kd}, Max={self.max_output}")

    def compute(self, error, dt=None):
        """
        Compute PID output

        Args:
            error: Current error (desired - actual)
            dt: Time delta (optional, will auto-calculate if None)

        Returns:
            PID output value (steering angle)
        """
        # Calculate time delta
        current_time = time.time()
        if dt is None:
            if self.last_time is not None:
                dt = current_time - self.last_time
            else:
                dt = 0.033  # Default ~30fps

        self.last_time = current_time

        # Prevent division by zero
        if dt <= 0:
            dt = 0.033

        # Proportional term
        p_term = self.kp * error

        # Integral term with anti-windup
        self.integral += error * dt

        # Clamp integral to prevent windup
        if self.integral > self.integral_max:
            self.integral = self.integral_max
        elif self.integral < -self.integral_max:
            self.integral = -self.integral_max

        i_term = self.ki * self.integral

        # Derivative term
        derivative = (error - self.previous_error) / dt
        d_term = self.kd * derivative

        # Calculate output
        output = p_term + i_term + d_term

        # Clamp output to max
        if output > self.max_output:
            output = self.max_output
        elif output < -self.max_output:
            output = -self.max_output

        # Update previous error
        self.previous_error = error

        return output

    def reset(self):
        """Reset PID controller state"""
        self.previous_error = 0
        self.integral = 0
        self.last_time = None

    def set_tunings(self, kp=None, ki=None, kd=None):
        """Update PID tuning parameters"""
        if kp is not None:
            self.kp = kp
        if ki is not None:
            self.ki = ki
        if kd is not None:
            self.kd = kd

        print(f"[INFO] PID tunings updated: Kp={self.kp}, Ki={self.ki}, Kd={self.kd}")

    def get_components(self, error, dt=None):
        """
        Get individual PID components for debugging

        Returns:
            Dictionary with p_term, i_term, d_term, output
        """
        # This is a debug version that returns components
        if dt is None:
            dt = 0.033

        p_term = self.kp * error
        i_term = self.ki * self.integral
        derivative = (error - self.previous_error) / dt
        d_term = self.kd * derivative
        output = p_term + i_term + d_term

        # Clamp output
        if output > self.max_output:
            output = self.max_output
        elif output < -self.max_output:
            output = -self.max_output

        return {
            'p_term': p_term,
            'i_term': i_term,
            'd_term': d_term,
            'output': output,
            'error': error
        }
