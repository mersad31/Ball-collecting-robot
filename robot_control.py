"""Pure drive-command logic for the ball-collecting robot.

No hardware dependencies: every function is testable in isolation.
Signed PWM values are used, positive = forward, negative = reverse.
"""

from dataclasses import dataclass

SEARCH = "search"
FORWARD = "forward"
TURN_LEFT = "turn_left"
TURN_RIGHT = "turn_right"
STOP = "stop"


@dataclass
class DriveConfig:
    default_speed: float = 50.0
    center_buffer: float = 10.0
    pwm_bound: float = 50.0
    camera_bound: float = 320.0
    approach_radius: float = 40.0
    close_radius: float = 50.0
    sharp_margin: float = 0.65
    search_speed: float = 30.0

    @property
    def kp(self):
        if self.camera_bound <= 0:
            raise ValueError("camera_bound must be positive")
        return self.pwm_bound / self.camera_bound


def compute_control(ball, width, cfg):
    """Return motor commands for the current ball observation.

    `ball` is the dict produced by BallDetector.detect or None.
    Returns a dict with keys: right, left (signed PWM) and mode.
    """
    if ball is None:
        return {"right": cfg.search_speed, "left": -cfg.search_speed, "mode": SEARCH}

    center = width / 2.0
    left_bound = center - cfg.center_buffer
    right_bound = center + cfg.center_buffer
    x = ball["x"]
    radius = ball["radius"]

    if left_bound <= x <= right_bound:
        if radius < cfg.approach_radius:
            return {"right": cfg.default_speed, "left": cfg.default_speed, "mode": FORWARD}
        return {"right": 0.0, "left": 0.0, "mode": STOP}

    error = center - x
    turn_pwm = min(abs(error) * cfg.kp + cfg.default_speed, 100.0)

    if x < left_bound:
        if radius > cfg.close_radius and x < center * (1 - cfg.sharp_margin):
            return {"right": cfg.default_speed, "left": cfg.default_speed * 0.4, "mode": TURN_LEFT}
        return {"right": turn_pwm, "left": cfg.default_speed, "mode": TURN_LEFT}

    if radius > cfg.close_radius and x > center * (1 + cfg.sharp_margin):
        return {"right": cfg.default_speed * 0.4, "left": cfg.default_speed, "mode": TURN_RIGHT}
    return {"right": cfg.default_speed, "left": turn_pwm, "mode": TURN_RIGHT}
