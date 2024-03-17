import cv2
import numpy as np

try:
    import tflite_runtime.interpreter as tflite
except ImportError:
    import tensorflow as tf

    tflite = tf.lite

from machine.states import States
from typing import TypedDict

MODEL_PATH = "./app/detector/efficientdet_lite0.tflite"
LABEL_PATH = "./app/detector/labelmap.txt"


class DetectionObject(TypedDict):
    box: np.ndarray
    classes: np.ndarray
    score: np.ndarray
    label: str


class DetectionResult(TypedDict):
    frame: np.ndarray
    detection_result: list[DetectionObject]


class Detector:
    def __init__(
        self,
        image_width: int,
        image_height: int,
        threshold: float = 0.6,
        model_path: str = MODEL_PATH,
        label_path: str = LABEL_PATH,
        preview: bool = False,
    ):
        self.model_path = model_path
        self.label_path = label_path
        self.labels = self.__load_labels(label_path)
        self.threshold = threshold
        self.image_width = image_width
        self.image_height = image_height

        # TFLiteモデルのロード
        self.interpreter = tflite.Interpreter(model_path=self.model_path, num_threads=3)
        self.input_details = self.interpreter.get_input_details()
        self.output_details = self.interpreter.get_output_details()
        self.interpreter.allocate_tensors()
        # 入出力詳細の取得
        self.preview = preview

    def __load_labels(self, label_path: str):
        with open(label_path, "r") as file:
            return [line.strip() for line in file.readlines()]

    def __detect_labels(self, class_ids: list[int]):
        return [self.labels[int(cid)] for cid in class_ids]

    def __preview_color(self, states: States):
        if states == States.search:
            return (0, 255, 0)
        elif states == States.tracking:
            return (0, 0, 255)
        elif states == States.shooting:
            return (255, 0, 0)
        return (0, 0, 0)

    def __preview_detect(self, frame, boxes, classes, scores, labels, preview_mode):
        preview_color = self.__preview_color(preview_mode)
        for box, cls, score, label in zip(boxes, classes, scores, labels):
            if score > self.threshold and score <= 1.0:
                ymin = int(max(1, (box[0] * self.image_height)))
                xmin = int(max(1, (box[1] * self.image_width)))
                ymax = int(min(self.image_height, (box[2] * self.image_height)))
                xmax = int(min(self.image_width, (box[3] * self.image_width)))

                cv2.rectangle(frame, (xmin, ymin), (xmax, ymax), preview_color, 4)

                label = "%s: %d%%" % (label, int(score * 100))
                labelSize, baseLine = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)
                # Make sure not to draw label too close to top of window
                label_ymin = max(ymin, labelSize[1] + 10)
                cv2.rectangle(
                    frame,
                    (xmin, label_ymin - labelSize[1] - 10),
                    (xmin + labelSize[0], label_ymin + baseLine - 10),
                    (255, 255, 255),
                    cv2.FILLED,
                )
                cv2.line(
                    frame,
                    (xmin + (xmax - xmin) // 2, ymin + (ymax - ymin) // 2),
                    (self.image_width // 2, self.image_height // 2),
                    preview_color,
                    2,
                )
                cv2.putText(frame, label, (xmin, label_ymin - 7), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)

        cv2.imshow("Object detector", frame)
        cv2.waitKey(1)

    def detect(self, frame, preview_mode: States = States.search) -> DetectionResult:
        # 画像の前処理
        input_image = cv2.resize(frame, (self.input_details[0]["shape"][2], self.input_details[0]["shape"][1]))
        dimmed_image = np.expand_dims(input_image, axis=0)

        # モデルでの推論
        self.interpreter.set_tensor(self.input_details[0]["index"], dimmed_image)
        self.interpreter.invoke()

        # 推論結果の取得
        boxes = self.interpreter.get_tensor(self.output_details[0]["index"])[0]
        classes = self.interpreter.get_tensor(self.output_details[1]["index"])[0]
        scores = self.interpreter.get_tensor(self.output_details[2]["index"])[0]

        # 信頼度が閾値を超えるものだけを抽出
        boxes = [box for score, box in zip(scores, boxes) if score > self.threshold]
        classes = [cls for score, cls in zip(scores, classes) if score > self.threshold]
        scores = [score for score in scores if score > self.threshold]
        labels = self.__detect_labels(classes)

        if self.preview:
            preview_resized_frame = cv2.resize(frame, (self.image_width, self.image_height))
            self.__preview_detect(preview_resized_frame, boxes, classes, scores, labels, preview_mode)

        return {
            "frame": input_image,
            "detection_result": [
                {"box": box, "classes": cls, "score": score, "label": label}
                for box, cls, score, label in zip(boxes, classes, scores, labels)
            ],
        }
