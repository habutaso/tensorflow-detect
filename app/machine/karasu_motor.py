from time import sleep
from typing import TypedDict

try:
    import RPi.GPIO as GPIO  # type: ignore
except ImportError:
    import Mock.GPIO as GPIO


class MotorPin(TypedDict):
    horizon_motor_signal_pin1: int
    horizon_motor_signal_pin2: int
    vertical_motor_signal_pin1: int
    vertical_motor_signal_pin2: int
    abort_signal_pin: int
    laser_pin: int


class MotorOption(TypedDict):
    pwm_frequency: int
    duty_cycle_zero: int
    duty_cycle_low: int
    duty_cycle_medium: int
    duty_cycle_high: int
    duty_cycle_max: int


class KarasuMotor:
    def __init__(self, motor_pin: MotorPin, motor_option: MotorOption):
        self.motor_pin = motor_pin
        self.motor_option = motor_option
        self.motor_count = 0
        self.init_pin_setting()

    def init_pin_setting(self):
        GPIO.setmode(GPIO.BCM)

        # モーター設定
        GPIO.setup(self.motor_pin["horizon_motor_signal_pin1"], GPIO.OUT)
        GPIO.setup(self.motor_pin["horizon_motor_signal_pin2"], GPIO.OUT)
        GPIO.setup(self.motor_pin["vertical_motor_signal_pin1"], GPIO.OUT)
        GPIO.setup(self.motor_pin["vertical_motor_signal_pin2"], GPIO.OUT)

        # レーザー設定
        GPIO.setup(self.motor_pin["laser_pin"], GPIO.OUT)

        # 中断信号設定
        GPIO.setup(self.motor_pin["abort_signal_pin"], GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    def search(self, search_count: int) -> None:
        p1 = GPIO.PWM(self.motor_pin["horizon_motor_signal_pin1"], self.motor_option["pwm_frequency"])
        p2 = GPIO.PWM(self.motor_pin["horizon_motor_signal_pin2"], self.motor_option["pwm_frequency"])
        p1.start(self.motor_option["duty_cycle_zero"])
        p2.start(self.motor_option["duty_cycle_zero"])

        # 左右にフリフリする処理　徐々に速度をあげ、徐々に下げる、逆回転させる
        dr1 = self.motor_option["duty_cycle_low"]
        dr2 = self.motor_option["duty_cycle_zero"]

        while self.motor_count < 10:
            if search_count % 10 < 5:
                p1.ChangeDutyCycle(dr1)
                p2.ChangeDutyCycle(dr2)
            else:
                p2.ChangeDutyCycle(dr1)
                p1.ChangeDutyCycle(dr2)
            sleep(0.2)
            p1.ChangeDutyCycle(self.motor_option["duty_cycle_zero"])
            p2.ChangeDutyCycle(self.motor_option["duty_cycle_zero"])
            sleep(1)
            self.motor_count += 1
        self.motor_count = 0

    def track(self, x_center_diff: int, y: int) -> None:
        p1 = GPIO.PWM(self.motor_pin["horizon_motor_signal_pin1"], self.motor_option["pwm_frequency"])
        p2 = GPIO.PWM(self.motor_pin["horizon_motor_signal_pin2"], self.motor_option["pwm_frequency"])
        p1.start(self.motor_option["duty_cycle_zero"])
        p2.start(self.motor_option["duty_cycle_medium"])

        dr1, dr2 = (
            (self.motor_option["duty_cycle_zero"], self.motor_option["duty_cycle_medium"])
            if x_center_diff < 0
            else (self.motor_option["duty_cycle_medium"], self.motor_option["duty_cycle_zero"])
        )

        for _ in range(2):
            p1.ChangeDutyCycle(dr1)
            p2.ChangeDutyCycle(dr2)
            sleep(0.05)

    def shoot(self) -> None:
        p1 = GPIO.PWM(self.motor_pin["horizon_motor_signal_pin1"], self.motor_option["pwm_frequency"])
        p2 = GPIO.PWM(self.motor_pin["horizon_motor_signal_pin2"], self.motor_option["pwm_frequency"])
        p1.start(self.motor_option["duty_cycle_zero"])
        p2.start(self.motor_option["duty_cycle_zero"])

        dr1 = [self.motor_option["duty_cycle_high"], self.motor_option["duty_cycle_zero"]] * 8
        dr2 = dr1[::-1]

        for c1, c2 in zip(dr1, dr2):
            p1.ChangeDutyCycle(c1)
            p2.ChangeDutyCycle(c2)
            sleep(0.1)

    def kill(self):
        print("kill all pin ...")
        for pin in self.motor_pin.values():
            GPIO.cleanup(pin)

    def quit(self):
        pass
