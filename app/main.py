import sys

from machine.karasu_mashine import KarasuMachine
from machine.karasu_machine_control import KarasuMachineControl
from utils.coordinate import Coordinate

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

# カメラ設定
CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480
CAMERA_FPS = 15

# 物体検知用設定値
DETECTOR_MODEL_FILENAME = "efficientdet_lite0.tflite"
DETECTOR_THREADS = 4
DETECTOR_DETECT_NUM_MAX = 1
DETECTOR_SCORE_THRESHOLD = 0.6

# 中心オブジェクト
CENTER = Coordinate(CAMERA_WIDTH // 2, CAMERA_HEIGHT // 2)


def abort_callback(karasu_machine, channel):
    if GPIO.input(channel) == GPIO.HIGH:
        karasu_machine.abort()  # 状態遷移のトリガー
        print("GPIOをクリーンアップ...")
        sys.stderr.close()
        GPIO.cleanup()
    else:
        return


def init_pin_setting():
    GPIO.setmode(GPIO.BCM)

    # モーター設定
    GPIO.setup(HORIZON_MOTOR_SIGNAL_PIN1, GPIO.OUT)
    GPIO.setup(HORIZON_MOTOR_SIGNAL_PIN2, GPIO.OUT)
    GPIO.setup(VERTICAL_MOTOR_SIGNAL_PIN1, GPIO.OUT)
    GPIO.setup(VERTICAL_MOTOR_SIGNAL_PIN2, GPIO.OUT)

    # レーザー設定
    GPIO.setup(LASER_PIN, GPIO.OUT)

    # 中断信号設定
    GPIO.setup(ABORT_SIGNAL_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)


def main():
    # 初期化処理
    try:
        # GPIO_PINの初期化
        init_pin_setting()

        karasu_machine = KarasuMachine()
        # 中断イベント検知を設定
        GPIO.add_event_detect(
            ABORT_SIGNAL_PIN, GPIO.RISING, callback=lambda x: abort_callback(karasu_machine, x), bouncetime=200
        )

        KarasuMachineControl(karasu_machine).main_process()

    except KeyboardInterrupt:
        # Ctrl+Cが押された場合の処理
        pass
    except Exception as e:
        print(e)
    finally:
        # プログラム終了時にGPIOをクリーンアップ
        print("GPIOをクリーンアップ...")
        GPIO.cleanup()


if __name__ == "__main__":
    main()
