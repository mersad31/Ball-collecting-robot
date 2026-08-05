"""Ball detection for the ball-collecting robot.

cv2 is imported optionally so this module can be imported and its pure
logic tested on machines without OpenCV installed.
"""

import numpy as np

try:
    import cv2
except ImportError:
    cv2 = None


class BallDetector:
    """Detects the best (largest) yellow ball in a BGR frame."""

    def __init__(self, min_area=100.0, min_radius=10.0):
        self.min_area = min_area
        self.min_radius = min_radius
        self.lower_yellow = np.array([13, 50, 0])
        self.upper_yellow = np.array([30, 255, 255])

    def build_mask(self, frame_bgr):
        hsv = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, self.lower_yellow, self.upper_yellow)
        mask = cv2.erode(mask, None, iterations=2)
        mask = cv2.dilate(mask, None, iterations=2)
        return mask

    def describe(self, contour):
        area = cv2.contourArea(contour)
        if area < self.min_area:
            return None
        (x, y), radius = cv2.minEnclosingCircle(contour)
        if radius < self.min_radius:
            return None
        return {"x": x, "y": y, "radius": radius, "area": area}

    def detect(self, frame_bgr):
        mask = self.build_mask(frame_bgr)
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        candidates = []
        for contour in contours:
            candidate = self.describe(contour)
            if candidate is not None:
                candidates.append(candidate)
        return select_best(candidates)


def select_best(candidates):
    """Return the candidate with the largest area, or None."""
    if not candidates:
        return None
    return max(candidates, key=lambda c: c["area"])
