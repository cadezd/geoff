import pickle
import re
from tkinter import filedialog

from pyzbar.pyzbar import ZBarSymbol
from pyzbar.pyzbar import decode

from utils.Util import *


class Seperator:
    def __init__(self):
        self.settings = {
            "DPI_IN": 300,
            "DPI_OUT": 140,
            "ZOOM": 2,
            "MASKA": 200,
            "PODROCJE": 0.3,
            "BELOST": 255,
            "FILTER": r"(DPR|CE|DDB|DOV|PRO|PADNI|DNI|NRA|PDO|NPR|PRA)([0-9]{2})(\+|-|_)([0-9]{4})",
            "DEFAULT_SEPARATE": "QR koda",
        }
        self.load_settings()

        self.documents = []
        self.grouped_pdfs = dict()

    def load_settings(self):
        # Creates settings file if it doesn't exist
        if not os.path.exists('settings/settings.cfg'):
            os.mkdir('settings')
            with open('settings/settings.cfg', 'wb') as f:
                pickle.dump(self.settings, f)

        # Loads data from file
        with open('settings/settings.cfg', 'rb') as f:
            self.settings = pickle.load(f)

        print("Settings loaded:", self.settings)

    def save_settings(self):
        # Save settings to file
        with open('settings/settings.cfg', 'wb') as f:
            pickle.dump(self.settings, f)

        print("Settings saved:", self.settings)

    def get_setting(self, key):
        return self.settings[key]

    def set_setting(self, key, value):
        self.settings[key] = value

    def get_file_paths(self, parent=None):
        # Asks the user to select one or more PDF files and adds them to the documents list
        file_paths = filedialog.askopenfilenames(
            filetypes=[("PDF Files", "*.pdf")],
            title="Izberite enega ali več PDF dokumentov"
        )

        if file_paths:
            # Sort the file paths by name
            file_paths = sorted(
                file_paths,
                key=lambda x: os.path.basename(x),
                reverse=True
            )

            # Create a popup loading bar
            popup = PopupLoadingBar(
                "Nalagam PDF dokumente...",
                len(file_paths),
                parent=parent
            )

            print("Selected PDF files:")
            for file_path in file_paths:

                # Check if the stop loading bar has been closed by the user and stop the function execution
                if popup.stop_event.is_set():
                    break

                # Create a dictionary with the document data
                documetn_data = {
                    "file_path": file_path,
                    "file_name": os.path.basename(file_path),
                    "first_image": get_image_of_frist_page(file_path),
                }

                print(documetn_data)
                popup.update()

                # Check if the document is already in the list
                if documetn_data not in self.documents:
                    self.documents.append(documetn_data)

            popup.destroy()

    def delete_content(self):
        # Deletes all content from the program
        print("Deleting content...")
        self.documents.clear()
        print("Documents deleted!", self.documents)
        self.grouped_pdfs.clear()
        print("Grouped PDFs deleted!", self.grouped_pdfs)

    def sort_pdfs(self):
        self.grouped_pdfs = dict(sorted(self.grouped_pdfs.items()))

    def change_document_name(self, old_name, new_name):
        # Changes the name od PDF in grouped_PDFs dictionary without changing the order
        replacement = {old_name: new_name}
        for k, v in list(self.grouped_pdfs.items()):
            self.grouped_pdfs[replacement.get(k, k)] = self.grouped_pdfs.pop(k)

        self.sort_pdfs()

        print("New name:", new_name)
        print("Grouped PDFs:", self.grouped_pdfs)

    def create_new_document(self, new_document_name, new_document_content):
        # Deletes pages from old document
        for pdf_page in new_document_content:
            self.delete_page(pdf_page)

        # Adds new document to grouped_PDFs and sorts pages by page number
        self.grouped_pdfs[new_document_name] = sorted(new_document_content, key=lambda x: x[1])
        self.sort_pdfs()

    def delete_page(self, page_path):
        print("Deleting page:", page_path)

        pdfs_to_remove = []
        for pdf_name, pdf_content in self.grouped_pdfs.items():
            print(pdf_content, page_path in pdf_content)
            if page_path in pdf_content:
                self.grouped_pdfs[pdf_name] = [item for item in pdf_content if item != page_path]
                if not self.grouped_pdfs[pdf_name]:
                    pdfs_to_remove.append(pdf_name)

                break

        print(pdfs_to_remove)
        for pdf_name in pdfs_to_remove:
            del self.grouped_pdfs[pdf_name]

        self.sort_pdfs()

        # Returns True if all pages of PDF have been deleted
        return len(pdfs_to_remove) > 0

    def group_pdfs(self, parent=None):
        if not self.documents:
            messagebox.showwarning(
                "Opozorilo",
                "Najprej morate izbrati vsaj eno PDF datoteko!",
                parent=parent
            )
            return False

        # progress bar
        popup = PopupLoadingBar(
            "Grupiram PDF dokumente...",
            len(self.documents),
            parent=parent
        )

        print("Grouping PDFs...")
        for document_data in self.documents:
            key = "NEPREPOZNANO"
            document = fitz.open(document_data["file_path"])

            # Check if the stop loading bar has been closed by the user and stop the function execution
            if popup.stop_event.is_set():
                self.grouped_pdfs.clear()
                return False

            for i, page in enumerate(document):
                # Preprocess the image for better QR / BAR code recognition
                inverted = preprocess_image(
                    page,
                    self.settings['DPI_IN'],
                    self.settings['PODROCJE'],
                    self.settings['ZOOM'],
                    self.settings['MASKA'],
                )

                # Decodes the QR / BAR code
                symbol = ZBarSymbol.QRCODE if parent.lower_controls_frame.combo_code.get() == "QR koda" else ZBarSymbol.CODE39
                decoded_codes = decode(inverted, symbols=[symbol])
                decoded_codes = [code.data.decode("utf-8").replace(" ", "_") for code in decoded_codes]

                print("Decoded codes:", decoded_codes)
                # Filters invalid codes
                filtered_codes = [code for code in decoded_codes if re.match(self.settings['FILTER'], code)]
                print("Filtered codes:", filtered_codes)

                # Group the PDFs
                if filtered_codes:
                    key = filtered_codes[0]
                if key not in self.grouped_pdfs:
                    self.grouped_pdfs[key] = []
                self.grouped_pdfs[key].append((str(document_data["file_path"]), int(i)))

            popup.update()

        self.sort_pdfs()
        popup.destroy()
        print("Grouped PDFs:", self.grouped_pdfs)
        return True

    def save_pdf_files(self):
        if len(self.documents) == 0:
            messagebox.showwarning("Obvestilo", "Izbrati morate vsaj eno PDF datoteko.")
            return False

        # User selects the output folder
        output_folder = filedialog.askdirectory(title="Izberite mapo za shranjevanje dokumentov")
        if not output_folder:
            return False

        # Save the PDFs
        try:
            old_pdf_path = ""
            for pdf_name, pdf_content in self.grouped_pdfs.items():
                print("Saving PDF:", pdf_name)
                output_pdf = fitz.open()

                if not pdf_content:
                    continue

                source_pdf = fitz.open(pdf_content[0][0])
                for pdf_path, pdf_page in pdf_content:
                    if old_pdf_path != pdf_path:
                        source_pdf = fitz.open(pdf_path)
                        old_pdf_path = pdf_path

                    output_pdf.insert_pdf(source_pdf, from_page=pdf_page, to_page=pdf_page)

                output_pdf.save(os.path.join(output_folder, pdf_name + ".pdf"))

            messagebox.showinfo("Obvestilo", "Dokumenti so bili uspešno shranjeni!")
            return True
        except Exception as e:
            messagebox.showerror("Napaka", "Prišlo je do napake pri shranjevanju dokumentov.\nNapaka: " + str(e))
            return False
