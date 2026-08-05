"""Tests for robot_vision ball detection logic."""

import robot_vision
from robot_vision import BallDetector, select_best


class FakeCV2:
    COLOR_BGR2HSV = "BGR2HSV"
    RETR_EXTERNAL = "external"
    CHAIN_APPROX_SIMPLE = "simple"

    def __init__(self, contours, areas, circles):
        self._contours = contours
        self._areas = areas
        self._circles = circles

    def cvtColor(self, img, code):
        return img

    def inRange(self, hsv, low, up):
        return "mask"

    def erode(self, m, kernel, iterations):
        return m

    def dilate(self, m, kernel, iterations):
        return m

    def findContours(self, mask, mode, method):
        return (self._contours, "hierarchy")

    def contourArea(self, contour):
        return self._areas[contour]

    def minEnclosingCircle(self, contour):
        return self._circles[contour]


def test_select_best_returns_largest_area():
    candidates = [
        {"x": 1, "y": 1, "radius": 10, "area": 100},
        {"x": 2, "y": 2, "radius": 20, "area": 300},
    ]
    assert select_best(candidates)["area"] == 300


def test_select_best_empty():
    assert select_best([]) is None


def test_describe_filters_small_contours(monkeypatch):
    fake = FakeCV2([], {"small": 5}, {"small": ((1, 1), 3)})
    monkeypatch.setattr(robot_vision, "cv2", fake)
    detector = BallDetector(min_area=100.0, min_radius=10.0)
    assert detector.describe("small") is None


def test_describe_filters_tiny_radius(monkeypatch):
    fake = FakeCV2([], {"big_area": 500}, {"big_area": ((150, 120), 5)})
    monkeypatch.setattr(robot_vision, "cv2", fake)
    detector = BallDetector(min_area=100.0, min_radius=10.0)
    assert detector.describe("big_area") is None


def test_describe_returns_ball_dict(monkeypatch):
    fake = FakeCV2([], {"c": 500}, {"c": ((150, 120), 25)})
    monkeypatch.setattr(robot_vision, "cv2", fake)
    detector = BallDetector(min_area=100.0, min_radius=10.0)
    assert detector.describe("c") == {"x": 150, "y": 120, "radius": 25, "area": 500}


def test_detect_picks_largest_contour(monkeypatch):
    fake = FakeCV2(
        contours=["small", "big"],
        areas={"small": 100, "big": 900},
        circles={"small": ((100, 100), 10), "big": ((200, 150), 30)},
    )
    monkeypatch.setattr(robot_vision, "cv2", fake)
    detector = BallDetector(min_area=100.0, min_radius=10.0)
    ball = detector.detect("frame")
    assert ball["x"] == 200
    assert ball["radius"] == 30
    assert ball["area"] == 900


def test_detect_returns_none_when_no_ball(monkeypatch):
    fake = FakeCV2(contours=[], areas={}, circles={})
    monkeypatch.setattr(robot_vision, "cv2", fake)
    detector = BallDetector(min_area=100.0, min_radius=10.0)
    assert detector.detect("frame") is None
