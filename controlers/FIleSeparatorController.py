from __future__ import annotations

import base64
import os
import pickle
import re
from io import BytesIO
from pprint import pprint

import fitz
from PIL import Image
from pyzbar.pyzbar import ZBarSymbol
from pyzbar.pyzbar import decode
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas

from utils.Util import is_regex_valid, preprocess_page, pdf_page_to_base64


class FileSeparatorController:
    def __init__(self, settings_path: str = os.path.join("..", "separator_settings", "settings.pkl")):
        # Settings path
        self.settings_path: str = settings_path
        # Default settings
        self.settings: dict[str, int | float | str] = self._load_settings()
        # Valid values for each setting
        self.valid_settings_values: dict[str, list[int | float]] = {
            "DPI_IN": [200, 250, 300, 350, 400],
            "DPI_OUT": [140],
            "ZOOM": [1, 2, 3],
            "MASKA": [150, 175, 200, 225, 250],
            "PODROCJE": [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
            "BELOST": [240, 245, 250, 255],
            "DEFAULT_SEPARATE": [0, 1],
        }

        # Progress of the separation
        self.progress: float = 0
        self.grouped_documents: dict[str, list[str]] = {}

    def _load_settings(self) -> dict:
        settings: dict[str, int | float | str] = {
            "DPI_IN": 300,
            "DPI_OUT": 140,
            "ZOOM": 2,
            "MASKA": 200,
            "PODROCJE": 0.3,
            "BELOST": 255,
            "FILTER": r"(DPR|CE|DDB|DOV|PRO|PADNI|DNI|NRA|PDO|NPR|PRA)([0-9]{2})(\+|-|_)([0-9]{4})",
            "DEFAULT_SEPARATE": 0,
        }

        # Creates settings file if it doesn't exist
        if not os.path.exists(self.settings_path):
            os.mkdir(os.path.dirname(self.settings_path))
            with open(self.settings_path, 'wb') as f:
                pickle.dump(settings, f)

        # Loads data from file
        with open(self.settings_path, 'rb') as f:
            settings = pickle.load(f)

        return settings

    def save_settings(self) -> None:
        # Save settings to file
        with open(self.settings_path, 'wb') as f:
            pickle.dump(self.settings, f)

    def set_setting(self, key: str, value: int | float | str) -> None:
        if key in self.valid_settings_values:
            if value in self.valid_settings_values[key]:
                self.settings[key] = value
        elif key == "FILTER":
            if is_regex_valid(value.strip()):
                self.settings[key] = value.strip()

    def group_documents(self, document_paths: list[str]) -> None:
        # Resets the progress
        self.progress = 0
        self.report_progress()

        # Decodes the QR / BAR code
        symbol = ZBarSymbol.QRCODE if self.settings["DEFAULT_SEPARATE"] == 0 else ZBarSymbol.CODE39
        # Default key
        key = "NEPREPOZNANO"

        # await asyncio.sleep(1)

        # Iterate through all document paths
        for i, document_path in enumerate(document_paths):
            print("Processing document:", document_path)

            # Open the document and iterate through all pages
            document = fitz.open(document_path)
            for page in document:
                # Preprocess the image for better QR / BAR code recognition
                inverted = preprocess_page(
                    page,
                    self.settings['DPI_IN'],
                    self.settings['PODROCJE'],
                    self.settings['ZOOM'],
                    self.settings['MASKA'],
                )

                decoded_codes = decode(inverted, symbols=[symbol])
                decoded_codes = [code.data.decode("utf-8").replace(" ", "_") for code in decoded_codes]

                # Filters invalid codes
                filtered_codes = [code for code in decoded_codes if re.match(self.settings["FILTER"], code)]

                # Group the PDFs
                if filtered_codes:
                    key = filtered_codes[0]
                if key not in self.grouped_documents:
                    self.grouped_documents[key] = []
                self.grouped_documents[key].append(pdf_page_to_base64(page=page, dpi=120))

            # Update the progress
            self.progress = (i + 1) / len(document_paths)
            self.report_progress()

        pprint(self.grouped_documents.keys())

    def rename_document(self, old_name: str, new_name: str) -> None:
        if not new_name or len(new_name.strip()) == 0 or "NOV DOKUMENT" in new_name or "NEPREPOZNANO" in new_name:
            raise ValueError(f"Ime dokumenta {new_name} ni veljavno!")

        if old_name not in self.grouped_documents:
            raise ValueError(f"Dokument {old_name} ne obstaja!")

        if new_name in self.grouped_documents:
            raise ValueError(f"Dokument {new_name} že obstaja!")

        self.grouped_documents[new_name] = self.grouped_documents.pop(old_name)

    def delete_document(self, name: str) -> None:
        if name not in self.grouped_documents:
            raise ValueError(f"Dokument {name} ne obstaja!")

        self.grouped_documents.pop(name)

    def clear_grouped_documents(self):
        self.grouped_documents.clear()

    def rearrange_document_pages(self, document_name: str, idx_from: int, idx_to: int) -> None:
        if document_name not in self.grouped_documents:
            raise ValueError(f"Dokument {document_name} ne obstaja!")

        if idx_from < 0 or idx_from >= len(self.grouped_documents[document_name]):
            raise ValueError(f"Začetni indeks {idx_from} ni veljaven!")

        if idx_to < 0 or idx_to >= len(self.grouped_documents[document_name]):
            raise ValueError(f"Končni indeks {idx_to} ni veljaven!")

        step: int = 1 if idx_from < idx_to else -1

        print(f"idx_from: {idx_from}, idx_to: {idx_to}, step: {step}")

        for i in range(idx_from, idx_to, step):
            print(i)
            self.grouped_documents[document_name][i], self.grouped_documents[document_name][i + step] = \
                self.grouped_documents[document_name][i + step], self.grouped_documents[document_name][i]

    def delete_document_page(self, document_name: str, idx: int) -> None:
        if document_name not in self.grouped_documents:
            raise ValueError(f"Dokument {document_name} ne obstaja!")

        if idx < 0 or idx >= len(self.grouped_documents[document_name]):
            raise ValueError(f"Indeks {idx} ni veljaven!")

        self.grouped_documents[document_name].pop(idx)

    def create_new_document(self, pages: list[str]) -> tuple[str, list[str]]:
        if not pages:
            raise ValueError("Izbrati morate vsaj eno stran, da lahko ustvarite nov dokument!")

        new_document_name: str = "NOV DOKUMENT"
        i: int = 1
        while new_document_name in self.grouped_documents:
            new_document_name = f"NOV DOKUMENT ({i})"
            i += 1

        self.grouped_documents[new_document_name] = pages

        return new_document_name, pages



    def save_documents(self, output_directory: str) -> None:
        for document_name, images_base64_list in self.grouped_documents.items():
            # Create a new PDF canvas
            pdf_path = os.path.join(output_directory, f"{document_name}.pdf")
            c = canvas.Canvas(pdf_path, pagesize=letter)

            for image_base64 in images_base64_list:
                # Decode the base64 image
                image_data = base64.b64decode(image_base64)
                image = Image.open(BytesIO(image_data))

                # Convert image to RGB if it's not
                if image.mode != "RGB":
                    image = image.convert("RGB")

                # Get the image dimensions
                image_width, image_height = image.size

                # Calculate the image's aspect ratio
                aspect_ratio = image_width / image_height

                # Calculate dimensions to fit the image within the PDF page while preserving aspect ratio
                pdf_width, pdf_height = letter

                if aspect_ratio > 1:
                    # Image is wider than it is tall
                    new_width = pdf_width
                    new_height = pdf_width / aspect_ratio
                else:
                    # Image is taller than it is wide
                    new_height = pdf_height
                    new_width = pdf_height * aspect_ratio

                # Center the image on the page
                x_offset = (pdf_width - new_width) / 2
                y_offset = (pdf_height - new_height) / 2

                # Create an ImageReader object from the image
                image_stream = BytesIO()
                image.save(image_stream, format="JPEG")
                image_stream.seek(0)
                image_reader = ImageReader(image_stream)

                # Draw the image on the PDF canvas directly from memory
                c.drawImage(image_reader, x_offset, y_offset, width=new_width, height=new_height)
                c.showPage()  # Create a new page for the next image

            # Save the PDF
            c.save()

    def report_progress(self):
        # This method will be overridden in the Separator View to update the progress bar
        pass


file_separator_controller = FileSeparatorController()
