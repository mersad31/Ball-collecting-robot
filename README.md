# 🤖 Ball-Collecting Robot

A Raspberry Pi robot that finds a yellow ball with computer vision and drives toward it.

---

## 🎯 The Problem

How do you make a very low-cost robot (Raspberry Pi Zero, one camera, two DC motors) find and reach a ball on its own, without any special sensors?

## 💡 The Approach

The robot runs a simple **see → decide → move** loop on every camera frame:

1. **Vision** (`robot_vision.py`): convert the frame to HSV, keep the yellow range, clean the mask (erode/dilate), find contours, filter by area and radius, and pick the largest candidate.
2. **Control** (`robot_control.py`): turn the ball's position and size into motor commands.
3. **Drive** (`robot.py`): send the commands to the motors with PWM on the Raspberry Pi GPIO pins.

| Situation | Behavior |
|---|---|
| No ball visible | Spin in place to search |
| Ball off-center | Turn toward it, proportionally to the error |
| Ball centered and far | Drive forward |
| Ball centered and close | Stop |

The vision and control logic has **no hardware dependencies**, so it is unit-tested on any computer.

<!-- TODO: add a photo or GIF of the robot, e.g. ![Robot](docs/robot.gif) -->

## 🧰 Hardware

| Part | Purpose |
|---|---|
| Raspberry Pi Zero | Main computer |
| Pi camera module | Vision (640×480, 15 fps) |
| L293D motor driver | Drives two DC motors |
| Robot chassis, wheels, power | Body |

GPIO pins (BOARD numbering): right forward `7`, right reverse `11`, left forward `13`, left reverse `15`.

## 🚀 Getting Started

On the Raspberry Pi:

```bash
git clone https://github.com/mersad31/Ball-collecting-robot.git
cd Ball-collecting-robot
pip install opencv-python numpy
python robot.py
```

`picamera` and `RPi.GPIO` are also required on the Pi. Press `q` to stop.

## 🧪 Tests

```bash
pip install pytest numpy
pytest tests
```

## 📂 Repository Layout

| File | Purpose |
|---|---|
| `robot.py` | Main loop, camera and motor (GPIO/PWM) handling |
| `robot_vision.py` | Yellow-ball detection |
| `robot_control.py` | Drive-command logic |
| `tests/` | Unit tests for vision and control |

## 🔭 Not Implemented Yet

- Gripper to actually pick the ball up
- Obstacle avoidance with an ultrasonic sensor

## 📝 License

See [LICENSE](LICENSE).
