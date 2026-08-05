"""Tests for robot_control drive-command logic (pure, no hardware)."""

from robot_control import (
    DriveConfig,
    FORWARD,
    SEARCH,
    STOP,
    TURN_LEFT,
    TURN_RIGHT,
    compute_control,
)

WIDTH = 640


def cfg(**overrides):
    return DriveConfig(**overrides)


def test_no_ball_triggers_search_rotation():
    cmd = compute_control(None, WIDTH, cfg())
    assert cmd["mode"] == SEARCH
    assert cmd["right"] > 0
    assert cmd["left"] < 0


def test_centered_far_ball_drives_forward():
    cmd = compute_control({"x": 320, "y": 240, "radius": 20}, WIDTH, cfg())
    assert cmd["mode"] == FORWARD
    assert cmd["right"] == 50
    assert cmd["left"] == 50


def test_centered_close_ball_stops():
    cmd = compute_control({"x": 320, "y": 240, "radius": 60}, WIDTH, cfg())
    assert cmd["mode"] == STOP
    assert cmd["right"] == 0
    assert cmd["left"] == 0


def test_ball_left_keeps_faster_on_right_motor():
    cmd = compute_control({"x": 200, "y": 240, "radius": 20}, WIDTH, cfg())
    assert cmd["mode"] == TURN_LEFT
    assert cmd["right"] > cmd["left"]


def test_ball_right_keeps_faster_on_left_motor():
    cmd = compute_control({"x": 440, "y": 240, "radius": 20}, WIDTH, cfg())
    assert cmd["mode"] == TURN_RIGHT
    assert cmd["left"] > cmd["right"]


def test_close_left_edge_uses_sharp_turn():
    cmd = compute_control({"x": 60, "y": 240, "radius": 60}, WIDTH, cfg())
    assert cmd["mode"] == TURN_LEFT
    assert cmd["left"] == 50 * 0.4


def test_close_right_edge_uses_sharp_turn():
    cmd = compute_control({"x": 600, "y": 240, "radius": 60}, WIDTH, cfg())
    assert cmd["mode"] == TURN_RIGHT
    assert cmd["right"] == 50 * 0.4


def test_turn_pwm_capped_at_100():
    cmd = compute_control({"x": 0, "y": 240, "radius": 20}, WIDTH, cfg())
    assert cmd["right"] <= 100
    assert cmd["right"] >= cmd["left"]


def test_center_buffer_ignores_small_offset():
    cmd = compute_control({"x": 315, "y": 240, "radius": 20}, WIDTH, cfg())
    assert cmd["mode"] == FORWARD


def test_invalid_camera_bound_raises():
    try:
        cfg(camera_bound=0).kp
    except ValueError:
        return
    raise AssertionError("expected ValueError")
