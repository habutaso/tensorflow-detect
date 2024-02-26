import time

try:
    import RPi.GPIO as GPIO
except ImportError:
    import Mock.GPIO as GPIO

# PIN設定
HORIZON_MOTOR_SIGNAL_PIN1 = 17
HORIZON_MOTOR_SIGNAL_PIN2 = 18
VERTICAL_MOTOR_SIGNAL_PIN1 = 22
VERTICAL_MOTOR_SIGNAL_PIN2 = 23
ABORT_SIGNAL_PIN = 5
LASER_PIN = 9
PWM_FREQUENCY = 1000  # PWMの周波数(回転速度やトルク、雑音に影響)

# デューティー比の設定
DUTY_CYCLE_MAX = 100
DUTY_CYCLE_HIGHT = 80
DUTY_CYCLE_MIDDLE = 60
DUTY_CYCLE_LOW = 30
DUTY_CYCLE_ZERO = 0


class MachineMotor:
    def __init__(
        self,
        horizontal_motor_signal_pin1: int = HORIZON_MOTOR_SIGNAL_PIN1,
        horizontal_motor_signal_pin2: int = HORIZON_MOTOR_SIGNAL_PIN2,
        vertical_motor_signal_pin1: int = VERTICAL_MOTOR_SIGNAL_PIN1,
        vertical_motor_signal_pin2: int = VERTICAL_MOTOR_SIGNAL_PIN2,
        laser_pin: int = LASER_PIN,
        abort_signal_pin: int = ABORT_SIGNAL_PIN,
        abort_callback: callable = lambda x: None,
    ):
        self.horizontal_motor_signal_pin1 = horizontal_motor_signal_pin1
        self.horizontal_motor_signal_pin2 = horizontal_motor_signal_pin2
        self.vertical_motor_signal_pin1 = vertical_motor_signal_pin1
        self.vertical_motor_signal_pin2 = vertical_motor_signal_pin2
        self.laser_pin = laser_pin
        self.abort_signal_pin = abort_signal_pin
        self.abort_callback = abort_callback
        self.__init_pin_setting()

    def __init_pin_setting(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.horizontal_motor_signal_pin1, GPIO.OUT)
        GPIO.setup(self.horizontal_motor_signal_pin1, GPIO.OUT)
        GPIO.setup(self.vertical_motor_signal_pin1, GPIO.OUT)
        GPIO.setup(self.vertical_motor_signal_pin1, GPIO.OUT)
        GPIO.setup(self.laser_pin, GPIO.OUT)
        GPIO.setup(self.abort_signal_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.add_event_detect(
            self.abort_signal_pin, GPIO.RISING, callback=lambda x: self.__abort_callback(x), bouncetime=200
        )

    def __abort_callback(self, channel):
        if GPIO.input(channel) == GPIO.HIGH:
            self.abort_callback()
            print("GPIOをクリーンアップ...")
            GPIO.cleanup()
        else:
            return

    def start(self):
        print(f"Starting motor {self.name}")

    def stop(self):
        print(f"Stopping motor {self.name}")
        # カラスを探索するために首振りをする関数

    def search(self):

        p1 = GPIO.PWM(self.horizontal_motor_signal_pin1, PWM_FREQUENCY)
        p2 = GPIO.PWM(self.horizontal_motor_signal_pin2, PWM_FREQUENCY)
        p1.start(DUTY_CYCLE_ZERO)
        p2.start(DUTY_CYCLE_ZERO)

        # 左右にフリフリする処理　徐々に速度をあげ、徐々に下げる、逆回転させる
        # dr1=[DUTY_CYCLE_LOW  ,DUTY_CYCLE_LOW,DUTY_CYCLE_LOW ,DUTY_CYCLE_LOW ,DUTY_CYCLE_LOW ]
        dr1 = [DUTY_CYCLE_LOW] * 5
        dr2 = [DUTY_CYCLE_ZERO] * 5

        for i in range(5):
            p1.ChangeDutyCycle(dr1[i])
            p2.ChangeDutyCycle(dr2[i])
            time.sleep(0.5)
        for i in range(5):
            p2.ChangeDutyCycle(dr1[i])
            p1.ChangeDutyCycle(dr2[i])
            time.sleep(0.5)

        return False

    def move_dist(self, dist: tuple[int, int]):
        p1 = GPIO.PWM(self.horizontal_motor_signal_pin1, PWM_FREQUENCY)
        p2 = GPIO.PWM(self.horizontal_motor_signal_pin2, PWM_FREQUENCY)
        p1.start(DUTY_CYCLE_ZERO)
        p2.start(DUTY_CYCLE_ZERO)

        if dist[0] < 0:
            dr1 = DUTY_CYCLE_MIDDLE
            dr2 = DUTY_CYCLE_ZERO
        else:
            dr1 = DUTY_CYCLE_ZERO
            dr2 = DUTY_CYCLE_MIDDLE

        for _ in range(2):
            p1.ChangeDutyCycle(dr1)
            p2.ChangeDutyCycle(dr2)
            time.sleep(0.05)
