import base64
import io
import re
from typing import Optional

import cv2
import numpy as np
from PIL import Image
from fitz import Page


def zoom(image, zoom_factor=2) -> np.ndarray:
    """
    Zooms the image by the given factor
    :param image:
    :param zoom_factor:
    :return:
    """
    return cv2.resize(image, None, fx=zoom_factor, fy=zoom_factor, interpolation=cv2.INTER_CUBIC)


def crop_image(image, scale_x=1.0, scale_y=1.0) -> np.ndarray:
    """
    Crops the image by the given scale
    :param image:
    :param scale_x:
    :param scale_y:
    :return:
    """
    width_scaled, height_scaled = image.shape[1] * scale_x, image.shape[0] * scale_y
    img_cropped = image[:int(height_scaled), :int(width_scaled)]
    return img_cropped


def is_white(image, whiteness: int):
    """
    Checks if the image is white
    :param image:
    :param whiteness:
    :return:
    """
    return np.mean(image) >= whiteness


def preprocess_page(page: Page, dpi: int, region: float, zoom_factor: int, mask: int,
                    whiteness: int) -> Optional[np.ndarray]:
    """
    Preprocesses the page for better QR / BAR code recognition
    :param page:
    :param dpi:
    :param region:
    :param zoom_factor:
    :param mask:
    :param whiteness:
    :return:
    """
    pixmap = page.get_pixmap(dpi=dpi)
    # Convert the pixmap to a numpy array
    width, height = pixmap.width, pixmap.height
    # Get the raw data from the pixmap
    raw_data = pixmap.samples
    # Calculate the number of channels based on the pixmap data format
    channels = len(raw_data) // (width * height)
    # Convert the raw data to a numpy array
    numpy_array = np.frombuffer(raw_data, dtype=np.uint8).reshape((height, width, channels))
    # Convert the numpy array to a cv2 image
    # Depending on the pixmap data format, you may need to adjust the color channel order
    image = cv2.cvtColor(numpy_array, cv2.COLOR_RGB2BGR)

    # If the image is white, return None
    if is_white(image, whiteness):
        return None

    image_croped = crop_image(image, scale_x=1, scale_y=region)
    image_zoomed = zoom(image_croped, zoom_factor=zoom_factor)

    # Makes mask (so it recognizes BAR code better)
    mask = cv2.inRange(
        image_zoomed,
        (0, 0, 0),
        (mask, mask, mask)
    )
    # Converts image to gray
    thresholded = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)
    # Converts image to black and white
    inverted = 255 - thresholded

    return inverted


def pdf_page_to_base64(page: Page, dpi: int) -> str:
    """
    Converts the PDF page to a base64 image string
    :param page:
    :param dpi:
    :return:
    """

    # Render page to a PNG image
    pix = page.get_pixmap(dpi=dpi)

    # Convert the pixmap to an Image object
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

    # Save the image to a bytes buffer
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")

    # Get the byte data from the buffer
    img_str = buffer.getvalue()

    # Encode the byte data to base64
    img_base64 = base64.b64encode(img_str).decode("utf-8")

    return img_base64


def is_regex_valid(regex: str) -> bool:
    """
    Checks if the regex pattern is valid
    :param regex:
    :return:
    """
    try:
        re.compile(regex)
        return True
    except re.error:
        return False
