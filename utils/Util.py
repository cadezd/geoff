import os
import shutil
import threading
from tkinter import messagebox

import cv2
import fitz
import numpy as np
from PIL import Image
from fitz import Page


def run_task_in_background(task, params=None):
    thread = threading.Thread(target=task, daemon=True, kwargs=params)
    return thread.start()


def debounce(func, delay=0.05):
    def debounced(*args, **kwargs):
        def call_it():
            func(*args, **kwargs)

        if hasattr(debounced, '_timer'):
            debounced._timer.cancel()
        debounced._timer = threading.Timer(delay, call_it)
        debounced._timer.start()

    return debounced


def get_image_of_frist_page(file_path: str):
    doc = fitz.open(file_path)

    # Load the first page
    first_page = doc.load_page(0)

    # Get the width and height of the page
    rect = first_page.rect
    width = int(rect.width)
    height = int(rect.height)

    # Get the pixmap of the first page
    pix = first_page.get_pixmap(matrix=fitz.Matrix(700 / width, 920 / height))

    # Convert the pixmap to a tkinter image
    image = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)

    doc.close()

    return image


def delete_directory_content(directory_name: str):
    for file_name in os.listdir(directory_name):
        file_path = os.path.join(directory_name, file_name)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            messagebox.showerror("Napaka", "Prišlo je do napake pri brisanju začasnih datotek.\nNapaka: " + str(e))


def convert_pdfs_to_images(files: list, output_directory_name: str, dpi: int, parent=None):
    if not os.path.exists(output_directory_name):
        os.makedirs(output_directory_name)

    # Create a loading bar
    progress_bar = PopupLoadingBar(
        label_text="Pretvarjanje PDF-ov v slike...",
        progress_max=len(files),
        parent=parent
    )

    print("Converting PDFs to images...")

    order_number = 0
    for file in files:
        if progress_bar.stop_event.is_set():
            delete_directory_content("images")
            break

        file_path = file["file_path"]
        pdf = fitz.open(file_path)
        for page in pdf:
            pixmap = page.get_pixmap(dpi=dpi)
            output_image_name = os.path.join(output_directory_name, f"image{str(order_number):0>6}.png")
            print(f"Saving image {output_image_name}")
            pixmap.pil_save(output_image_name, dpi=(dpi, dpi))
            order_number += 1

        pdf.close()

        progress_bar.update()

    progress_bar.destroy()


def optimize_images(files: list, output_directory_name: str, dpi: int, parent=None):
    if not os.path.exists(output_directory_name):
        os.makedirs(output_directory_name)

    # Create a loading bar
    progress_bar = PopupLoadingBar(
        label_text="Optimiziram slike...",
        progress_max=len(files),
        parent=parent
    )

    print("Optimiziram slike...")

    order_number = 0
    for file in files:
        if progress_bar.stop_event.is_set():
            delete_directory_content("images")
            break

        file_path = file["file_path"]
        pdf = fitz.open(file_path)
        for page in pdf:
            pixmap = page.get_pixmap(dpi=dpi)
            output_image_name = os.path.join(output_directory_name, f"image{str(order_number):0>6}.png")
            print(f"Saving image {output_image_name}")
            pixmap.pil_save(output_image_name, dpi=(dpi, dpi))
            order_number += 1

        pdf.close()

        progress_bar.update()

    progress_bar.destroy()


def zoom(image, zoom_factor=2):
    return cv2.resize(image, None, fx=zoom_factor, fy=zoom_factor, interpolation=cv2.INTER_CUBIC)


def crop_image(image, scale_x=1.0, scale_y=1.0):
    width_scaled, height_scaled = image.shape[1] * scale_x, image.shape[0] * scale_y
    img_cropped = image[:int(height_scaled), :int(width_scaled)]
    return img_cropped


def is_white(image, whiteness: int):
    return np.mean(image) >= whiteness


def convert_fitz_page_to_pil_image(pdf_path: str, pdf_page: int, dpi1: int):
    file = fitz.open(pdf_path)
    page = file[pdf_page]
    pixmap = page.get_pixmap(dpi=dpi1)
    # Convert the pixmap to a numpy array
    width, height = pixmap.width, pixmap.height
    # Get the raw data from the pixmap
    raw_data = pixmap.samples
    # Calculate the number of channels based on the pixmap data format
    channels = len(raw_data) // (width * height)
    # Convert the raw data to a numpy array
    numpy_array = np.frombuffer(raw_data, dtype=np.uint8).reshape((height, width, channels))

    pil_image = Image.fromarray(numpy_array)

    return pil_image


def preprocess_image(page: Page, dpi: int, region: float, zoom_factor: int, mask: int):
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
