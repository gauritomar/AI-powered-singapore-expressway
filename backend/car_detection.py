import cv2
import numpy as np
import requests

class CarDetection:
    def __init__(self, cascade_path):
        self.cascade = cv2.CascadeClassifier(cascade_path)

    def detect_car(self, camera_data):
        try:
            image_url = camera_data['image']

            image_response = requests.get(image_url)
            image_array = np.asarray(bytearray(image_response.content), dtype=np.uint8)
            image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)

            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

            objects = self.cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)

            bounding_boxes = []
            for (x, y, w, h) in objects:
                bounding_box = {'x': int(x), 'y': int(y), 'width': int(w), 'height': int(h)}
                bounding_boxes.append(bounding_box)

            camera_data['bounding_boxes'] = bounding_boxes

            return camera_data
        except Exception as e:
            raise Exception(str(e))
