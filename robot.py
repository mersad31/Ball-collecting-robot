"""Improved ball-collecting robot control loop.

Runs on a Raspberry Pi with a camera and a two-motor chassis.
Hardware imports are optional so the module can be imported and tested
on any machine; call main() on the Raspberry Pi.
"""

import time

try:
    import cv2
except ImportError:
    cv2 = None

try:
    from picamera.array import PiRGBArray
    from picamera import PiCamera
except ImportError:
    PiCamera = None
    PiRGBArray = None

try:
    import RPi.GPIO as GPIO
except ImportError:
    GPIO = None

from robot_control import DriveConfig, compute_control
from robot_vision import BallDetector

PINS = {
    "right_fwd": 7,
    "right_rev": 11,
    "left_fwd": 13,
    "left_rev": 15,
}
PWM_FREQ = 50


def _require_hardware():
    missing = []
    if cv2 is None:
        missing.append("opencv-python")
    if PiCamera is None:
        missing.append("picamera")
    if GPIO is None:
        missing.append("RPi.GPIO")
    if missing:
        raise RuntimeError("Missing hardware dependencies: " + ", ".join(missing))


def init_gpio():
    GPIO.setmode(GPIO.BOARD)
    GPIO.setwarnings(False)
    for pin in PINS.values():
        GPIO.setup(pin, GPIO.OUT)
    for pin in PINS.values():
        GPIO.output(pin, False)


def make_pwms():
    pwms = {name: GPIO.PWM(pin, PWM_FREQ) for name, pin in PINS.items()}
    for channel in pwms.values():
        channel.start(0)
    return pwms


def drive(pwms, right, left):
    """Apply signed PWM values; positive drives forward, negative reverses."""
    for name, value in (("right", right), ("left", left)):
        fwd = pwms[name + "_fwd"]
        rev = pwms[name + "_rev"]
        if value > 0:
            fwd.ChangeDutyCycle(min(value, 100))
            rev.ChangeDutyCycle(0)
        elif value < 0:
            rev.ChangeDutyCycle(min(-value, 100))
            fwd.ChangeDutyCycle(0)
        else:
            fwd.ChangeDutyCycle(0)
            rev.ChangeDutyCycle(0)


def stop_all(pwms):
    for channel in pwms.values():
        channel.ChangeDutyCycle(0)
        channel.stop()


def main():
    _require_hardware()
    camera = PiCamera()
    camera.resolution = (640, 480)
    camera.framerate = 15
    raw = PiRGBArray(camera, size=camera.resolution)

    cfg = DriveConfig()
    detector = BallDetector()
    pwms = None
    try:
        init_gpio()
        pwms = make_pwms()
        cfg.camera_bound = camera.resolution[0] / 2.0
        time.sleep(0.1)
        for frame in camera.capture_continuous(raw, format="bgr", use_video_port=True):
            image = frame.array
            ball = detector.detect(image)
            cmd = compute_control(ball, camera.resolution[0], cfg)
            drive(pwms, cmd["right"], cmd["left"])
            raw.truncate(0)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
    finally:
        if pwms is not None:
            stop_all(pwms)
        if GPIO is not None:
            GPIO.cleanup()
        camera.close()


if __name__ == "__main__":
    main()
