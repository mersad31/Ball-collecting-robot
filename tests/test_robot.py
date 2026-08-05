"""Tests for the robot main module: import, GPIO init, and PWM routing."""

import robot


class FakeGPIO:
    BOARD = "board"
    OUT = "out"

    def __init__(self):
        self.mode = None
        self.setup_calls = []
        self.output_calls = []
        self.cleaned = False

    def setmode(self, mode):
        self.mode = mode

    def setwarnings(self, flag):
        pass

    def setup(self, pin, io):
        self.setup_calls.append((pin, io))

    def output(self, pin, value):
        self.output_calls.append((pin, value))

    def PWM(self, pin, freq):
        return FakePWM(pin, freq)

    def cleanup(self):
        self.cleaned = True


class FakePWM:
    def __init__(self, pin, freq):
        self.pin = pin
        self.freq = freq
        self.duty = None
        self.stopped = False

    def start(self, duty):
        self.duty = duty

    def ChangeDutyCycle(self, duty):
        self.duty = duty

    def stop(self):
        self.stopped = True


def test_module_imports():
    assert robot is not None


def test_main_raises_when_hardware_missing():
    try:
        robot.main()
    except RuntimeError as exc:
        assert "Missing hardware dependencies" in str(exc)
        return
    raise AssertionError("expected RuntimeError")


def test_init_gpio_sets_pins_as_output(monkeypatch):
    fake = FakeGPIO()
    monkeypatch.setattr(robot, "GPIO", fake)
    robot.init_gpio()
    assert fake.mode == fake.mode  # board mode was set
    assert len(fake.setup_calls) == 4
    assert len(fake.output_calls) == 4
    for _, value in fake.output_calls:
        assert value is False


def test_make_pwms_starts_all_at_zero(monkeypatch):
    fake = FakeGPIO()
    monkeypatch.setattr(robot, "GPIO", fake)
    pwms = robot.make_pwms()
    assert len(pwms) == 4
    for channel in pwms.values():
        assert channel.duty == 0


def test_drive_forward_sets_fwd_and_clears_rev(monkeypatch):
    fake = FakeGPIO()
    monkeypatch.setattr(robot, "GPIO", fake)
    pwms = robot.make_pwms()
    robot.drive(pwms, 40, 60)
    assert pwms["right_fwd"].duty == 40
    assert pwms["left_fwd"].duty == 60
    assert pwms["right_rev"].duty == 0
    assert pwms["left_rev"].duty == 0


def test_drive_reverse_sets_rev_and_clears_fwd(monkeypatch):
    fake = FakeGPIO()
    monkeypatch.setattr(robot, "GPIO", fake)
    pwms = robot.make_pwms()
    robot.drive(pwms, -30, 50)
    assert pwms["right_rev"].duty == 30
    assert pwms["right_fwd"].duty == 0
    assert pwms["left_fwd"].duty == 50
    assert pwms["left_rev"].duty == 0


def test_drive_zero_stops_both_channels(monkeypatch):
    fake = FakeGPIO()
    monkeypatch.setattr(robot, "GPIO", fake)
    pwms = robot.make_pwms()
    robot.drive(pwms, 50, 50)
    robot.drive(pwms, 0, 0)
    for name in ("right_fwd", "right_rev", "left_fwd", "left_rev"):
        assert pwms[name].duty == 0


def test_drive_caps_pwm_at_100(monkeypatch):
    fake = FakeGPIO()
    monkeypatch.setattr(robot, "GPIO", fake)
    pwms = robot.make_pwms()
    robot.drive(pwms, 150, -150)
    assert pwms["right_fwd"].duty == 100
    assert pwms["left_rev"].duty == 100


def test_stop_all_stops_every_channel(monkeypatch):
    fake = FakeGPIO()
    monkeypatch.setattr(robot, "GPIO", fake)
    pwms = robot.make_pwms()
    robot.stop_all(pwms)
    for channel in pwms.values():
        assert channel.duty == 0
        assert channel.stopped
