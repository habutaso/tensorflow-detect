import sys
import cv2
from transitions import Machine
import RPi.GPIO as GPIO
from time import sleep
from tflite_support.task import processor
from typing import Tuple

from camera import Camera
from coordinate import Coordinate, DetectionCoordinate
from detector import Detector
from visualize import get_diff_from_center


sys.stderr = open("./err.log", "w")


class KarasuSystem:
    # on_enter_XXX は状態遷移時必ず実行される共通処理
    def __init__(self):
        self.detection_result = processor.DetectionResult([])
        self.point_diffs_buf = []
        

    def on_enter_Search(self):
        # カラス検索処理を実行
        print("探索モード: カラスを探しています...")
        result = search_karasu()

        # 見つかった
        if result == True:
            print("見つかりました")
            self.crow_detected()

        # 見つからないまま一定時間経過
        else:
            print("見つかりませんでした")
            self.no_crow_detected() # 再度Searchに遷移

    def on_enter_Tracking(self):
        # 追跡処理を実行
        print("追跡モード: カラスを追跡しています...")

        self.detection_result = detect_karasu()

        if len(self.point_diffs_buf) > 4 and not all(d[0] for d in self.point_diffs_buf):
            # 追跡できなくなった場合
            print("no")
            self.point_diffs_buf = []
            self.crow_lost()

        if not self.detection_result.detections:
            self.point_diffs_buf.append((None, None))
            self.continue_tracking()
        detect_object = self.detection_result.detections[0]
        coordinate = DetectionCoordinate(detect_object)
        point_diff: Tuple[int, int] = get_diff_from_center(CENTER, coordinate.gravity)
        move_camera(point_diff)
        print("diff: ", self.point_diffs_buf)
        self.point_diffs_buf.append(point_diff)


        # 一定時間中心とのズレが少なかった場合
        if all(d[0] is not None and d[0] < 20 for d in self.point_diffs_buf):
            self.point_diffs_buf = []
            self.crow_centered()
        else:
            self.continue_tracking()

    def on_enter_Shooting(self):
        # 射撃処理
        print("射撃モード: カラスを狙っています...")
        # レーザーを照射しながら、少し動かす
        # やりたいことが終わったら
        shoot_karasu()
        self.shooting_done()

    def on_exit_Shooting(self):
        print("射撃完了: 再び探索モードに移行します。")

    def on_enter_Quit(self):
        print("システム終了: システムを終了します。")
    
    # after_ はafterで指定した特定のイベントヒット時に状態遷移後最後に実行される処理
    def after_initializing(self):
        print("初期化完了時の処理")

# 環境変数設定----------------------------------------------------------------------

# PIN設定
HORIZON_MOTOR_SIGNAL_PIN1 = 17
HORIZON_MOTOR_SIGNAL_PIN2 = 18
VERTICAL_MOTOR_SIGNAL_PIN1 = 22
VERTICAL_MOTOR_SIGNAL_PIN2 = 23
ABORT_SIGNAL_PIN = 5
LASER_PIN = 9

PWM_FREQUENCY = 1000 # PWMの周波数(回転速度やトルク、雑音に影響)

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

# 状態遷移マシンを初期化
karasu_system = KarasuSystem()

# カメラを初期化
camera = Camera(0)
camera.set_wh(CAMERA_WIDTH, CAMERA_HEIGHT)
camera.set_fps(CAMERA_FPS)

# 物体検知を初期化
detector = Detector(
    model_filename=DETECTOR_MODEL_FILENAME,
    num_threads=DETECTOR_THREADS,
    max_results=DETECTOR_DETECT_NUM_MAX,
    score_threshold=DETECTOR_SCORE_THRESHOLD
)
# 環境変数設定-終-------------------------------------------------------------------

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

    return


def detect_karasu():
    # カラスの検知
    _, image = camera.device.read()
    # image = cv2.flip(image, 1)
    rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    return detector.detect(rgb_image)


# カラスを探索するために首振りをする関数
def search_karasu():
    detection_result = []

    p1 = GPIO.PWM(HORIZON_MOTOR_SIGNAL_PIN1, PWM_FREQUENCY)
    p2 = GPIO.PWM(HORIZON_MOTOR_SIGNAL_PIN2, PWM_FREQUENCY)
    p1.start(DUTY_CYCLE_ZERO)
    p2.start(DUTY_CYCLE_ZERO)

    # 左右にフリフリする処理　徐々に速度をあげ、徐々に下げる、逆回転させる
    dr1=[DUTY_CYCLE_LOW  ,DUTY_CYCLE_LOW,DUTY_CYCLE_LOW ,DUTY_CYCLE_LOW ,DUTY_CYCLE_LOW ]
    dr2=[DUTY_CYCLE_ZERO ,DUTY_CYCLE_ZERO  ,DUTY_CYCLE_ZERO  ,DUTY_CYCLE_ZERO   ,DUTY_CYCLE_ZERO]

    for i in range(5):
        p1.ChangeDutyCycle(dr1[i])
        p2.ChangeDutyCycle(dr2[i])
        sleep(0.2)
        detection_result = detect_karasu()
        if detection_result.detections:
            return True
    for i in range(5):
        p2.ChangeDutyCycle(dr1[i])
        p1.ChangeDutyCycle(dr2[i])
        sleep(0.2)
        detection_result = detect_karasu()
        if detection_result.detections:
            return True

    return  False


def move_camera(diff: Tuple[int, int]):
    p1 = GPIO.PWM(HORIZON_MOTOR_SIGNAL_PIN1, PWM_FREQUENCY)
    p2 = GPIO.PWM(HORIZON_MOTOR_SIGNAL_PIN2, PWM_FREQUENCY)
    p1.start(DUTY_CYCLE_ZERO)
    p2.start(DUTY_CYCLE_ZERO)

    if diff[0] < 0:
        dr1 = DUTY_CYCLE_MIDDLE
        dr2 = DUTY_CYCLE_ZERO
    else:
        dr1 = DUTY_CYCLE_ZERO
        dr2 = DUTY_CYCLE_MIDDLE

    for _ in range(3):
        p1.ChangeDutyCycle(dr1)
        p2.ChangeDutyCycle(dr2)


def shoot_karasu():
    p1 = GPIO.PWM(HORIZON_MOTOR_SIGNAL_PIN1, PWM_FREQUENCY)
    p2 = GPIO.PWM(HORIZON_MOTOR_SIGNAL_PIN2, PWM_FREQUENCY)
    p1.start(DUTY_CYCLE_ZERO)
    p2.start(DUTY_CYCLE_ZERO)

    dr1 = [DUTY_CYCLE_HIGHT, DUTY_CYCLE_ZERO] * 8
    dr2 = dr1[::-1]

    for c1, c2 in zip(dr1, dr2):
        p1.ChangeDutyCycle(c1)
        p2.ChangeDutyCycle(c2)
        sleep(0.1)


# 中断処理
def abort_callback(channel):
    if GPIO.input(channel) == GPIO.HIGH:
        karasu_system.abort()  # 状態遷移のトリガー
        print("GPIOをクリーンアップ...")
        sys.stderr.close()
        GPIO.cleanup()
    else:
        return

# ステートマシンの初期化処理
def init_statemachine():
    # 状態リストを定義
    states = ['Initial', 'Search', 'Tracking', 'Shooting', 'Quit']

    # 遷移リストを定義
    transitions = [
        { 'trigger': 'initialize_done', 'source': 'Initial', 'dest': 'Search' },
        { 'trigger': 'no_crow_detected', 'source': 'Search', 'dest': 'Search' },
        { 'trigger': 'crow_detected', 'source': 'Search', 'dest': 'Tracking' },
        { 'trigger': 'crow_lost', 'source': 'Tracking', 'dest': 'Search' },
        { 'trigger': 'crow_centered', 'source': 'Tracking', 'dest': 'Shooting' },
        { 'trigger': 'continue_tracking', 'source': 'Tracking', 'dest': 'Tracking' },
        { 'trigger': 'shooting_done', 'source': 'Shooting', 'dest': 'Search' },
        { 'trigger': 'abort', 'source': '*', 'dest': 'Quit' }  # '*'は全ての状態から遷移可能を意味する
    ]

    machine = Machine(model=karasu_system, states=states, transitions=transitions, initial='Initial')
    
    return


def main():
    # 初期化処理
    try:
        # GPIO_PINの初期化
        init_pin_setting()

        # ステートマシンの初期化
        init_statemachine()

        # 中断イベント検知を設定
        GPIO.add_event_detect(ABORT_SIGNAL_PIN, GPIO.RISING, callback=abort_callback, bouncetime=200)

        # 初期化終了→Search状態へ遷移
        karasu_system.initialize_done()  # Searchに遷移
        
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

