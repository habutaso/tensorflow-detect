import sys
import os

from distutils.util import strtobool

from machine.karasu_detector import KarasuDetector
from machine.karasu_machine_control import KarasuMachineControl
from machine.karasu_motor import KarasuMotor, MotorOption, MotorPin
from utils.coordinate import Coordinate

from detector.detector import Detector
from devices.camera import Camera


try:
    import RPi.GPIO as GPIO
except ImportError:
    import Mock.GPIO as GPIO


# プレビューの有無
KARASU_PREVIEW = bool(strtobool(os.getenv("KARASU_PREVIEW", "False"))) or True

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
CAMERA_WIDTH = 800
CAMERA_HEIGHT = 600
CAMERA_FPS = 15
CAMERA_ID = 0

# 物体検知用設定値
DETECTOR_MODEL_FILENAME = "efficientdet_lite0.tflite"
DETECTOR_THREADS = 4
DETECTOR_DETECT_NUM_MAX = 1
DETECTOR_SCORE_THRESHOLD = 0.6

# 中心オブジェクト
CENTER = Coordinate(CAMERA_WIDTH // 2, CAMERA_HEIGHT // 2)


def abort_callback(channel):
    if GPIO.input(channel) == GPIO.HIGH:
        print("GPIOをクリーンアップ...")
        sys.stderr.close()
        GPIO.cleanup()
    else:
        return


def main():
    motor_pin: MotorPin = {
        "horizon_motor_signal_pin1": HORIZON_MOTOR_SIGNAL_PIN1,
        "horizon_motor_signal_pin2": HORIZON_MOTOR_SIGNAL_PIN2,
        "vertical_motor_signal_pin1": VERTICAL_MOTOR_SIGNAL_PIN1,
        "vertical_motor_signal_pin2": VERTICAL_MOTOR_SIGNAL_PIN2,
        "laser_pin": LASER_PIN,
        "abort_signal_pin": ABORT_SIGNAL_PIN,
    }

    motor_option: MotorOption = {
        "pwm_frequency": PWM_FREQUENCY,
        "duty_cycle_zero": DUTY_CYCLE_ZERO,
        "duty_cycle_low": DUTY_CYCLE_LOW,
        "duty_cycle_medium": DUTY_CYCLE_MIDDLE,
        "duty_cycle_high": DUTY_CYCLE_HIGHT,
        "duty_cycle_max": DUTY_CYCLE_MAX,
    }

    try:
        detector = Detector(CAMERA_WIDTH, CAMERA_HEIGHT, preview=KARASU_PREVIEW)
        camera = Camera(CAMERA_ID, width=CAMERA_WIDTH, height=CAMERA_HEIGHT, fps=CAMERA_FPS)
        motor = KarasuMotor(motor_pin, motor_option)
        karasu_machine = KarasuDetector(detector, camera, motor)
        # 中断イベント検知を設定
        GPIO.add_event_detect(
            ABORT_SIGNAL_PIN, GPIO.RISING, callback=lambda x: abort_callback(karasu_machine, x), bouncetime=200
        )

        KarasuMachineControl(karasu_machine).main_process()

    except KeyboardInterrupt:
        # Ctrl+Cが押された場合の処理
        pass
    # except Exception as e:
    finally:
        # プログラム終了時にGPIOをクリーンアップ
        print("GPIOをクリーンアップ...")
        GPIO.cleanup()


if __name__ == "__main__":
    main()
