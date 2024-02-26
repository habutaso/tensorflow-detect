from time import sleep
from typing import TypedDict
try:
    import RPi.GPIO as GPIO
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


    def search(self):
        p1 = GPIO.PWM(self.motor_pin["horizon_motor_signal_pin1"], self.motor_option["pwm_frequency"])
        p2 = GPIO.PWM(self.motor_pin["horizon_motor_signal_pin2"], self.motor_option["pwm_frequency"])
        p1.start(self.motor_option["duty_cycle_zero"])
        p2.start(self.motor_option["duty_cycle_zero"])

        # 左右にフリフリする処理　徐々に速度をあげ、徐々に下げる、逆回転させる
        # dr1=[DUTY_CYCLE_LOW  ,DUTY_CYCLE_LOW,DUTY_CYCLE_LOW ,DUTY_CYCLE_LOW ,DUTY_CYCLE_LOW ]
        dr1 = [self.motor_option["duty_cycle_low"]] * 5
        dr2 = [self.motor_option["duty_cycle_zero"]] * 5

        for i in range(5):
            p1.ChangeDutyCycle(dr1[i])
            p2.ChangeDutyCycle(dr2[i])
            sleep(0.5)
        for i in range(5):
            p2.ChangeDutyCycle(dr1[i])
            p1.ChangeDutyCycle(dr2[i])
            sleep(0.5)

        return False

    def track(self):
        pass

    def shoot(self):
        pass

    def quit(self):
        pass