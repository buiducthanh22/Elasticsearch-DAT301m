from vietocr.tool.predictor import Predictor
from vietocr.tool.config import Cfg
from paddleocr import PaddleOCR
from PIL import Image

import numpy as np
import cv2
import base64
import io

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

defaultdict = {}
config = Cfg.load_config_from_name("vgg_transformer")
config['weights'] = './data/vgg_transformer.pth'
config['device'] = 'cpu'
config['cnn']['pretrained']=False


class Rec_text():

    def __init__(self) -> None:
        """
        Initializes the `RecText` object.

        Loads the text prediction model using the provided configuration.

        Args:
            self (RecText): An instance of the `RecText` class.
            config (dict): A dictionary containing configuration parameters for the text recognition model.
        """
        self.predictor = Predictor(config)

    def text(self, img):
        """
        Predicts text from an input image.

        This method utilizes the loaded text prediction model (`self.predictor`)
        to extract text from the given image (`img`).

        Args:
            self (RecText): An instance of the `RecText` class.
            img (bytes or np.ndarray): The image data to be processed for text extraction.
                This can be in the form of raw bytes or a NumPy array representing the image.

        Returns:
            str: The predicted text extracted from the input image.
        """
        result_text = self.predictor.predict(img)
        return result_text
    
    def cut_img(self, file, box_list):
        """
        Crop a specific area from the image based on a list of bounding boxes.

        This method extracts a sub-image from the provided `file` using coordinates
        defined in `box_list`.

        Args:
            self (RecText): An instance of class `RecText`.
            file: Image data read as PIL.
            box_list (list): List of four pairs of integers defining the bounding box coordinates.
                    The format is [x1, y1, x3, y3], where:
                        - (x1, y1) represents the upper left corner of the bounding box.
                        - (x3, y3) represents the lower right corner of the bounding box.

        Return:
            The image has been cropped.
        """
        x1 = box_list[0][0]
        y1 = box_list[0][1]
        x3 = box_list[2][0]
        y3 = box_list[2][1]

        try:
            img = file
            img_cut = img.crop(((int(x1), int(y1), int(x3), int(y3))))
        except (IOError, OSError, ValueError) as e:
            print(f"Error: {e}")
        return img_cut

    def rec_vietOCR(self, files, box):
        """
        Performs Vietnamese OCR on text regions defined by bounding boxes.

        Args:
            self (RecText): An instance of the `RecText` class.
            files: The image data or file path for OCR.
            box: A list of bounding boxes, each defining a region to extract text from.

        Returns:
            str: The combined text recognized from all image regions, separated by spaces.
        """
        lst_text = []
        for i in box:
            img = self.cut_img(files, i)
            text = self.text(img)
            lst_text.append(text)
        tex = ' '.join(lst_text)
        tex = tex.replace('\n', ' ')
        return tex
    
    def base64_to_cv2(self, base64_string):
        """
        Converts a Base64-encoded image string to an OpenCV (cv2) image object.

        Args:
            self (RecText): An instance of the `RecText` class.
            base64_string (str): The Base64-encoded image string.

        Returns:
            np.ndarray: The decoded image as a NumPy array that can be used with OpenCV.
        """
        img_bytes = base64.b64decode(base64_string)
        nparr = np.frombuffer(img_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        return img
    
    def base64_to_pil(self, base64_string):
        """
        Converts a Base64-encoded image string to a PIL (Pillow) Image object.

        Args:
            self (RecText): An instance of the `RecText` class.
            base64_string (str): The Base64-encoded image string.

        Returns:
            Image.Image: The decoded image as a PIL Image object.
        """
        image_bytes = base64.b64decode(base64_string)
        image_buffer = io.BytesIO(image_bytes)
        pil_image = Image.open(image_buffer)
        return pil_image

    def detect_ocr(self, img):
        """
        Detects text regions in an image using PaddleOCR's detection model.

        Args:
            self (RecText): An instance of the `RecText` class.
            img (Image.Image): The image to process.

        Returns:
            list: A list of detected text regions, where each region is a dictionary
                with keys 'box' (bounding box coordinates) and 'text' (the detected text).
        """
        det_list = []
        ocr = PaddleOCR(det_model_dir='C:/DAT301m/dev_backend/data/model_detect', use_gpu=False)
        result = ocr.ocr(img,rec=False)
        for idx in range(len(result)):
            res = result[idx]
            for line in res:
                det_list.append(line)
        return det_list

    def __call__(self, base64_img):
        """
        Performs Vietnamese OCR on text regions in a Base64-encoded image.

        This method takes a Base64-encoded image string, decodes it, and performs the
        following steps:

        1. Decodes the Base64 string to a cv2 image using `base64_to_cv2`.
        2. Detects text regions in the cv2 image using `detect_ocr`. This step
        identifies potential areas containing text but doesn't perform recognition.
        3. Decodes the Base64 string to a PIL image using `base64_to_pil`. This image
        is likely used for text recognition as PIL is more suitable for text processing.
        4. Performs Vietnamese OCR on the detected text regions (`box`) within the PIL
        image (`image_pil`) using `rec_vietOCR`.
        5. Returns the combined recognized text from all regions.

        Args:
            self (RecText): An instance of the `RecText` class.
            base64_img (str): The Base64-encoded image string.

        Returns:
            str: The combined recognized text from all detected text regions.
        """
        img_cv2 = self.base64_to_cv2(base64_img)
        box = self.detect_ocr(img_cv2)
        image_pil = self.base64_to_pil(base64_img)
        all_text = self.rec_vietOCR(image_pil, box)
        return all_text