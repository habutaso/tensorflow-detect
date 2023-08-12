from tflite_support.task import core, processor, vision


class Detector:
    def __init__(self, model_filename: str, num_threads: int, max_results: int, score_threshold: float):
        self.base_options = core.BaseOptions(file_name=model_filename, num_threads=num_threads)
        self.detection_options = processor.DetectionOptions(max_results=max_results, score_threshold=score_threshold)
        self.detector_options = vision.ObjectDetectorOptions(
            base_options=self.base_options, detection_options=self.detection_options
        )

        self.detector = vision.ObjectDetector.create_from_options(self.detector_options)

    def detect(self, image):
        tensor = vision.TensorImage.create_from_array(image)
        detection_result = self.detector.detect(tensor)
        return detection_result
