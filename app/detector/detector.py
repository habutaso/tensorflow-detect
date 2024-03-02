import cv2
import numpy as np
try:
    import tflite_runtime.interpreter as tflite
except ImportError:
    import tensorflow as tf
    tflite = tf.lite

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
        model_path: str = MODEL_PATH,
        label_path: str = LABEL_PATH,
        preview: bool = False,
    ):
        self.model_path = model_path
        self.label_path = label_path
        self.labels = self.__load_labels(label_path)

        # TFLiteモデルのロード
        self.interpreter = tflite.Interpreter(model_path=self.model_path)
        self.interpreter.allocate_tensors()
        # 入出力詳細の取得
        self.input_details = self.interpreter.get_input_details()
        self.output_details = self.interpreter.get_output_details()
        self.image_width = image_width
        self.image_height = image_height
        self.preview = preview

    def __load_labels(self, label_path: str):
        with open(label_path, "r") as file:
            return [line.strip() for line in file.readlines()]

    def __detect_labels(self, class_ids: list[int]):
        return [self.labels[int(cid)] for cid in class_ids]

    def __preview_detect(self, frame, boxes, classes, scores, labels):
        for box, cls, score, label in zip(boxes, classes, scores, labels):
            if score > 0.6 and score <= 1.0:
                print(f"box: {box}, class: {cls}, score: {score}")
                ymin = int(max(1, (box[0] * self.image_height)))
                xmin = int(max(1, (box[1] * self.image_width)))
                ymax = int(min(self.image_height, (box[2] * self.image_height)))
                xmax = int(min(self.image_width, (box[3] * self.image_width)))

                cv2.rectangle(frame, (xmin, ymin), (xmax, ymax), (10, 255, 0), 4)

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
                cv2.putText(frame, label, (xmin, label_ymin - 7), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)

        cv2.imshow("Object detector", frame)
        cv2.waitKey(1)

    def detect(self, frame) -> DetectionResult:
        # 画像の前処理
        input_image = cv2.resize(frame, (self.input_details[0]["shape"][2], self.input_details[0]["shape"][1]))
        input_image = np.expand_dims(input_image, axis=0)

        # モデルでの推論
        self.interpreter.set_tensor(self.input_details[0]["index"], input_image)
        self.interpreter.invoke()

        # 推論結果の取得
        boxes = self.interpreter.get_tensor(self.output_details[0]["index"])[0]
        classes = self.interpreter.get_tensor(self.output_details[1]["index"])[0]
        scores = self.interpreter.get_tensor(self.output_details[2]["index"])[0]
        labels = self.__detect_labels(classes)

        if self.preview:
            self.__preview_detect(frame, boxes, classes, scores, labels)

        return {
            "frame": frame,
            "detection_result": [
                {"box": box, "classes": cls, "score": score, "label": label}
                for box, cls, score, label in zip(boxes, classes, scores, labels)
            ],
        }
