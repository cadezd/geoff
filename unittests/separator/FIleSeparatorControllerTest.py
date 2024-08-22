import os.path
import pickle
import unittest

from controllers.FileSeparatorController import FileSeparatorController


class FileSeparatorControllerTest(unittest.TestCase):

    def setUp(self):
        # Delete the folder named "separator_settings" in the current directory if it exists and all files in it
        if os.path.exists("separator_settings"):
            for file in os.listdir("separator_settings"):
                os.remove(os.path.join("separator_settings", file))
            os.rmdir("separator_settings")

        # Create the controller
        self.controller: FileSeparatorController = FileSeparatorController(
            os.path.join("separator_settings", "settings.pkl"))

    def tearDown(self):
        # Delete the folder named "separator_settings" in the current directory if it exists and all files in it
        if os.path.exists("separator_settings"):
            for file in os.listdir("separator_settings"):
                os.remove(os.path.join("separator_settings", file))
            os.rmdir("separator_settings")

    def test_set_setting_success(self):
        # Check if the setting is set successfully with valid key and value
        # DPI_IN
        # valid values are: 200, 250, 300, 350, 400
        for i in range(200, 400 + 1, 50):
            self.controller.set_setting("DPI_IN", i)
            self.assertEqual(self.controller.settings["DPI_IN"], i)

        # DPI_OUT
        # valid values are: 140
        self.controller.set_setting("DPI_OUT", 140)
        self.assertEqual(self.controller.settings["DPI_OUT"], 140)

        # ZOOM
        # valid values are: 1, 2, 3
        for i in range(1, 3 + 1):
            self.controller.set_setting("ZOOM", i)
            self.assertEqual(self.controller.settings["ZOOM"], i)

        # MASKA
        # valid values are: 150, 175, 200, 225, 250
        for i in range(150, 250 + 1, 25):
            self.controller.set_setting("MASKA", i)
            self.assertEqual(self.controller.settings["MASKA"], i)

        # PODROCJE
        # valid values are: 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0
        for i in [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]:
            self.controller.set_setting("PODROCJE", i)
            self.assertEqual(self.controller.settings["PODROCJE"], i)

        # BELOST
        # valid values are: 240, 245, 250, 255
        for i in range(240, 255 + 1, 5):
            self.controller.set_setting("BELOST", i)
            self.assertEqual(self.controller.settings["BELOST"], i)

        # DEFAULT_SEPARATE
        # valid values are: 0, 1
        for i in [0, 1]:
            self.controller.set_setting("DEFAULT_SEPARATE", i)
            self.assertEqual(self.controller.settings["DEFAULT_SEPARATE"], i)

        # FILTER
        # checks that only the valid regex patterns are set
        # valid values are: any valid regex pattern
        regex_patterns = [
            r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$',  # Email Address
            r'^(https?:\/\/)?(www\.)?[a-zA-Z0-9-]+\.[a-zA-Z]{2,}(\.[a-zA-Z]{2,})?([\/\w .-]*)*\/?$',  # URL
            r'^\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}$',  # US Phone Number
            r'^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$',
            # IPv4 Address
            r'^\d{4}-\d{2}-\d{2}$',  # Date (YYYY-MM-DD)
            r'^#?([a-fA-F0-9]{6}|[a-fA-F0-9]{3})$',  # Hexadecimal Color Code
            r'^[1-9]\d*$',  # Positive Integer
            r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d]{8,}$',  # Password
            r'^.+$',  # Non-empty String
            r'^\s+|\s+$'  # Whitespace (for trimming)
        ]
        for i in range(len(regex_patterns)):
            self.controller.set_setting("FILTER", regex_patterns[i])
            self.assertEqual(self.controller.settings["FILTER"], regex_patterns[i])

    def test_set_setting_fail(self):
        # Check if the setting is not set with invalid key and value
        # DPI_IN
        # valid values are: 200, 250, 300, 350, 400, everything else is invalid
        for i in [100, 150, 500]:
            self.controller.set_setting("DPI_IN", i)
            self.assertNotEqual(self.controller.settings["DPI_IN"], i)

        # DPI_OUT
        # valid values are: 140, everything else is invalid
        for i in [100, 150, 200, 250, 300, 350, 400, 450, 500]:
            self.controller.set_setting("DPI_OUT", i)
            self.assertNotEqual(self.controller.settings["DPI_OUT"], i)

        # ZOOM
        # valid values are: 1, 2, 3, everything else is invalid
        for i in [0, 4, 5]:
            self.controller.set_setting("ZOOM", i)
            self.assertNotEqual(self.controller.settings["ZOOM"], i)

        # MASKA
        # valid values are: 150, 175, 200, 225, 250, everything else is invalid
        for i in [100, 125, 130, 135, 140, 145, 155, 160, 165, 170, 180, 185, 190, 195, 205, 210, 215, 220, 230, 235,
                  240, 245, 255]:
            self.controller.set_setting("MASKA", i)
            self.assertNotEqual(self.controller.settings["MASKA"], i)

        # PODROCJE
        # valid values are: 0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, everything else is invalid
        for i in [-1, 1.1, 1.5, 2.0]:
            self.controller.set_setting("PODROCJE", i)
            self.assertNotEqual(self.controller.settings["PODROCJE"], i)

        # BELOST
        # valid values are: 240, 245, 250, 255, everything else is invalid
        for i in [0, 50, 100, 200]:
            self.controller.set_setting("BELOST", i)
            self.assertNotEqual(self.controller.settings["BELOST"], i)

        # DEFAULT_SEPARATE
        # valid values are: 0, 1, everything else is invalid
        for i in [-1, 2, 3]:
            self.controller.set_setting("DEFAULT_SEPARATE", i)
            self.assertNotEqual(self.controller.settings["DEFAULT_SEPARATE"], i)

        # FILTER
        # valid values are: any valid regex pattern, everything else is invalid
        invalid_regex_patterns = [
            r'[a-z',  # Missing closing bracket for character class
            r'*abc',  # Quantifier '*' used without preceding element
            r'(?P<name>[a-z]+',  # Unclosed group with a name
            r'[0-9]{3,2}',  # Quantifier range is reversed (min > max)
            r'((abc)',  # Unmatched parentheses
            r'abc\k<1>',  # Invalid backreference (no such group exists)
            r'(?<=abc',  # Unclosed lookbehind assertion
            r'\u',  # Incomplete escape sequence
            r'[\w-+',  # Unbalanced character class (e.g., '-+' should be inside a valid range or properly escaped)
        ]
        for i in range(len(invalid_regex_patterns)):
            self.controller.set_setting("FILTER", invalid_regex_patterns[i])
            self.assertNotEqual(self.controller.settings["FILTER"], invalid_regex_patterns[i])

    def test_save_default_settings(self):
        # Check is the controller creates the folder named "separator_settings" in the current directory
        self.assertTrue(os.path.exists("separator_settings"))

        # Check is the controller creates the file named "settings.pkl" in the folder "separator_settings"
        self.assertTrue(os.path.exists(os.path.join("separator_settings", "settings.pkl")))

    def test_load_default_settings(self):
        # Check is the controller creates the folder named "separator_settings" in the current directory
        self.assertTrue(os.path.exists("separator_settings"))

        # Check is the controller creates the file named "settings.pkl" in the folder "separator_settings"
        self.assertTrue(os.path.exists(os.path.join("separator_settings", "settings.pkl")))

        # Load the settings from the file using pickle into dictionary
        settings = pickle.load(open(os.path.join("separator_settings", "settings.pkl"), "rb"))

        # Check is the loaded settings are the same as the default settings
        self.assertEqual(settings, self.controller.settings)

    def test_load_settings_from_existing_file(self):
        # Change some settings
        self.controller.set_setting("DPI_IN", 250)
        self.controller.set_setting("ZOOM", 3)
        self.controller.set_setting("MASKA", 175)
        self.controller.set_setting("PODROCJE", 0.5)
        self.controller.set_setting("BELOST", 240)
        self.controller.set_setting("DEFAULT_SEPARATE", 1)
        self.controller.set_setting("FILTER", r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')

        # Save the settings to the file
        self.controller.save_settings()

        # Load the settings from the file
        settings = self.controller._load_settings()

        self.assertEqual(settings, self.controller.settings)

    def test_save_settings_to_existing_file(self):
        # Change some settings
        self.controller.set_setting("DPI_IN", 250)
        self.controller.set_setting("ZOOM", 3)
        self.controller.set_setting("MASKA", 175)
        self.controller.set_setting("PODROCJE", 0.5)
        self.controller.set_setting("BELOST", 240)
        self.controller.set_setting("DEFAULT_SEPARATE", 1)
        self.controller.set_setting("FILTER", r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')

        # Save the settings to the file
        self.controller.save_settings()

        # Load the settings from the file
        settings = self.controller._load_settings()

        self.assertEqual(settings, self.controller.settings)

    def test_group_documents_barcode(self):
        # files with barcodes
        files = [
            os.path.join("test_files", "barcode1.pdf"),
            os.path.join("test_files", "barcode2.pdf"),
            os.path.join("test_files", "barcode3.pdf"),
        ]

        # set the optimal settings for barcode detection
        self.controller.set_setting("MASKA", 250)
        self.controller.set_setting("ZOOM", 1)
        self.controller.set_setting("DPI_IN", 300)
        self.controller.set_setting("PODROCJE", 0.3)
        self.controller.set_setting("BELOST", 255)
        self.controller.set_setting("DEFAULT_SEPARATE", 1)
        self.controller.set_setting("FILTER",
                                    r"(DPR|CE|DDB|DOV|PRO|PADNI|DNI|NRA|M_PDO|PDO|NPR|PRA)([0-9]{2})(\+|-|_)([0-9]{4,6})")

        # group the documents
        self.controller.group_documents(files)

        # check if the documents are grouped correctly (by checking the document names and length of each document)
        self.assertIn("M_PDO24+00081", self.controller.grouped_documents.keys())
        self.assertEqual(len(self.controller.grouped_documents["M_PDO24+00081"]), 1)

        self.assertIn("NPR24+00079", self.controller.grouped_documents.keys())
        self.assertEqual(len(self.controller.grouped_documents["NPR24+00079"]), 1)

        self.assertIn("PRA24+01733", self.controller.grouped_documents.keys())
        self.assertEqual(len(self.controller.grouped_documents["PRA24+01733"]), 1)

        self.assertIn("NPR24+00081", self.controller.grouped_documents.keys())
        self.assertEqual(len(self.controller.grouped_documents["NPR24+00081"]), 4)

    def test_group_documents_qrcode(self):
        # files with barcodes
        files = [
            os.path.join("test_files", "qrcode1.pdf"),
            os.path.join("test_files", "qrcode2.pdf"),
        ]

        # set the optimal settings for qrcode detection
        self.controller.set_setting("MASKA", 200)
        self.controller.set_setting("ZOOM", 1)
        self.controller.set_setting("DPI_IN", 300)
        self.controller.set_setting("PODROCJE", 0.3)
        self.controller.set_setting("BELOST", 255)
        self.controller.set_setting("DEFAULT_SEPARATE", 0)
        self.controller.set_setting("FILTER",
                                    r"(DPR|CE|DDB|DOV|PRO|PADNI|DNI|NRA|M_PDO|PDO|NPR|PRA)([0-9]{2})(\+|-|_)([0-9]{4,6})")

        # group the documents
        self.controller.group_documents(files)

        # check if the documents are grouped correctly (by checking the document names and length of each document)
        self.assertIn("DPR23-01745", self.controller.grouped_documents.keys())
        self.assertEqual(len(self.controller.grouped_documents["DPR23-01745"]), 2)

        self.assertIn("DPR23-01744", self.controller.grouped_documents.keys())
        self.assertEqual(len(self.controller.grouped_documents["DPR23-01744"]), 2)

        self.assertIn("DPR23-01735", self.controller.grouped_documents.keys())
        self.assertEqual(len(self.controller.grouped_documents["DPR23-01735"]), 2)

        self.assertIn("DPR23-01734", self.controller.grouped_documents.keys())
        self.assertEqual(len(self.controller.grouped_documents["DPR23-01734"]), 10)

        self.assertIn("DPR23-01732", self.controller.grouped_documents.keys())
        self.assertEqual(len(self.controller.grouped_documents["DPR23-01732"]), 1)

        self.assertIn("DPR23-01731", self.controller.grouped_documents.keys())
        self.assertEqual(len(self.controller.grouped_documents["DPR23-01731"]), 2)

        self.assertIn("DPR23-01730", self.controller.grouped_documents.keys())
        self.assertEqual(len(self.controller.grouped_documents["DPR23-01730"]), 3)

        self.assertIn("DPR23-01729", self.controller.grouped_documents.keys())
        self.assertEqual(len(self.controller.grouped_documents["DPR23-01729"]), 4)

        self.assertIn("DPR23-01728", self.controller.grouped_documents.keys())
        self.assertEqual(len(self.controller.grouped_documents["DPR23-01728"]), 6)

    def test_rename_document(self):
        files = [
            os.path.join("test_files", "qrcode1.pdf"),
        ]

        # set the optimal settings for qrcode detection
        self.controller.set_setting("MASKA", 200)
        self.controller.set_setting("ZOOM", 1)
        self.controller.set_setting("DPI_IN", 300)
        self.controller.set_setting("PODROCJE", 0.3)
        self.controller.set_setting("BELOST", 255)
        self.controller.set_setting("DEFAULT_SEPARATE", 0)
        self.controller.set_setting("FILTER",
                                    r"(DPR|CE|DDB|DOV|PRO|PADNI|DNI|NRA|M_PDO|PDO|NPR|PRA)([0-9]{2})(\+|-|_)([0-9]{4,6})")

        # group the documents
        self.controller.group_documents(files)

        # rename the document
        self.controller.rename_document("DPR23-01745", "DPR23-01745_new")

        self.assertIn("DPR23-01745_new", self.controller.grouped_documents.keys())

        # duplicate name must raise an error
        self.assertRaises(ValueError, self.controller.rename_document, "DPR23-01745_new", "DPR23-01745_new")

        # invalid name must raise an error (invalid name includes NOV DOKUMENT or NEPREPOZNANO, or it's not in the grouped documents)
        self.assertRaises(ValueError, self.controller.rename_document, "DPR23-01745_new", "NOV DOKUMENT")
        self.assertRaises(ValueError, self.controller.rename_document, "DPR23-01745_new", "NEPREPOZNANO")
        self.assertRaises(ValueError, self.controller.rename_document, "dcshdfghaskjdfhgasd", "DPR23-01745")

    def test_delete_document(self):
        files = [
            os.path.join("test_files", "qrcode1.pdf"),
        ]

        # set the optimal settings for qrcode detection
        self.controller.set_setting("MASKA", 200)
        self.controller.set_setting("ZOOM", 1)
        self.controller.set_setting("DPI_IN", 300)
        self.controller.set_setting("PODROCJE", 0.3)
        self.controller.set_setting("BELOST", 255)
        self.controller.set_setting("DEFAULT_SEPARATE", 0)
        self.controller.set_setting("FILTER",
                                    r"(DPR|CE|DDB|DOV|PRO|PADNI|DNI|NRA|M_PDO|PDO|NPR|PRA)([0-9]{2})(\+|-|_)([0-9]{4,6})")

        # group the documents
        self.controller.group_documents(files)

        # delete the document
        self.controller.delete_document("DPR23-01745")

        self.assertNotIn("DPR23-01745", self.controller.grouped_documents.keys())

        # if the document doesn't exist, it must raise an error
        self.assertRaises(ValueError, self.controller.delete_document, "dcshdfghaskjdfhgasd")

    def test_clear_grouped_documents(self):
        files = [
            os.path.join("test_files", "qrcode1.pdf"),
        ]

        # set the optimal settings for qrcode detection
        self.controller.set_setting("MASKA", 200)
        self.controller.set_setting("ZOOM", 1)
        self.controller.set_setting("DPI_IN", 300)
        self.controller.set_setting("PODROCJE", 0.3)
        self.controller.set_setting("BELOST", 255)
        self.controller.set_setting("DEFAULT_SEPARATE", 0)
        self.controller.set_setting("FILTER",
                                    r"(DPR|CE|DDB|DOV|PRO|PADNI|DNI|NRA|M_PDO|PDO|NPR|PRA)([0-9]{2})(\+|-|_)([0-9]{4,6})")

        # group the documents
        self.controller.group_documents(files)

        # clear the grouped documents
        self.controller.clear_grouped_documents()

        self.assertEqual(self.controller.grouped_documents, {})

    def test_rearrange_document_pages(self):
        files = [
            os.path.join("test_files", "qrcode1.pdf"),
        ]

        # set the optimal settings for qrcode detection
        self.controller.set_setting("MASKA", 200)
        self.controller.set_setting("ZOOM", 1)
        self.controller.set_setting("DPI_IN", 300)
        self.controller.set_setting("PODROCJE", 0.3)
        self.controller.set_setting("BELOST", 255)
        self.controller.set_setting("DEFAULT_SEPARATE", 0)
        self.controller.set_setting("FILTER",
                                    r"(DPR|CE|DDB|DOV|PRO|PADNI|DNI|NRA|M_PDO|PDO|NPR|PRA)([0-9]{2})(\+|-|_)([0-9]{4,6})")

        # group the documents
        self.controller.group_documents(files)

        # rearrange the document pages
        self.controller.rearrange_document_pages("DPR23-01734", 2, 9)
        self.controller.rearrange_document_pages("DPR23-01734", 0, 0)
        self.controller.rearrange_document_pages("DPR23-01734", 8, 1)

        # if document doesn't exist, it must raise an error
        self.assertRaises(ValueError, self.controller.rearrange_document_pages, "dcshdfghaskjdfhgasd", 0, 0)
        # if the page numbers are invalid, it must raise an error
        self.assertRaises(ValueError, self.controller.rearrange_document_pages, "DPR23-01734", -1, 0)
        self.assertRaises(ValueError, self.controller.rearrange_document_pages, "DPR23-01734", 0, -1)
        self.assertRaises(ValueError, self.controller.rearrange_document_pages, "DPR23-01734", 0, 10)
        self.assertRaises(ValueError, self.controller.rearrange_document_pages, "DPR23-01734", -1, 10)

    def test_delete_document_page(self):
        files = [
            os.path.join("test_files", "qrcode1.pdf"),
        ]

        # set the optimal settings for qrcode detection
        self.controller.set_setting("MASKA", 200)
        self.controller.set_setting("ZOOM", 1)
        self.controller.set_setting("DPI_IN", 300)
        self.controller.set_setting("PODROCJE", 0.3)
        self.controller.set_setting("BELOST", 255)
        self.controller.set_setting("DEFAULT_SEPARATE", 0)
        self.controller.set_setting("FILTER",
                                    r"(DPR|CE|DDB|DOV|PRO|PADNI|DNI|NRA|M_PDO|PDO|NPR|PRA)([0-9]{2})(\+|-|_)([0-9]{4,6})")

        # group the documents
        self.controller.group_documents(files)

        # delete the document page
        self.controller.delete_document_page("DPR23-01734", 2)
        self.controller.delete_document_page("DPR23-01734", 0)
        self.controller.delete_document_page("DPR23-01734", 5)
        self.controller.delete_document_page("DPR23-01734", 6)

        # if document doesn't exist, it must raise an error
        self.assertRaises(ValueError, self.controller.delete_document_page, "dcshdfghaskjdfhgasd", 0)
        # if the page number is invalid, it must raise an error
        self.assertRaises(ValueError, self.controller.delete_document_page, "DPR23-01734", -1)
        self.assertRaises(ValueError, self.controller.delete_document_page, "DPR23-01734", 11)

    def test_create_new_document(self):
        # files with barcodes
        files = [
            os.path.join("test_files", "qrcode1.pdf"),
        ]

        # set the optimal settings for qrcode detection
        self.controller.set_setting("MASKA", 200)
        self.controller.set_setting("ZOOM", 1)
        self.controller.set_setting("DPI_IN", 300)
        self.controller.set_setting("PODROCJE", 0.3)
        self.controller.set_setting("BELOST", 255)
        self.controller.set_setting("DEFAULT_SEPARATE", 0)
        self.controller.set_setting("FILTER",
                                    r"(DPR|CE|DDB|DOV|PRO|PADNI|DNI|NRA|M_PDO|PDO|NPR|PRA)([0-9]{2})(\+|-|_)([0-9]{4,6})")

        # group the documents
        self.controller.group_documents(files)

        # create a new document
        new_document1_pages = [
            self.controller.grouped_documents["DPR23-01745"].pop(0),
            self.controller.grouped_documents["DPR23-01744"].pop(0),
            self.controller.grouped_documents["DPR23-01735"].pop(0),
        ]

        new_document2_pages = [
            self.controller.grouped_documents["DPR23-01734"].pop(0),
            self.controller.grouped_documents["DPR23-01734"].pop(0),
            self.controller.grouped_documents["DPR23-01734"].pop(0),
        ]

        new_document3_pages = [
            self.controller.grouped_documents["DPR23-01734"].pop(0),
            self.controller.grouped_documents["DPR23-01734"].pop(0),
            self.controller.grouped_documents["DPR23-01734"].pop(0),
        ]

        self.controller.create_new_document(new_document1_pages)
        self.controller.create_new_document(new_document2_pages)
        self.controller.create_new_document(new_document3_pages)

        self.assertIn("NOV DOKUMENT", self.controller.grouped_documents.keys())
        self.assertEqual(len(self.controller.grouped_documents["NOV DOKUMENT"]), 3)

        self.assertIn("NOV DOKUMENT (1)", self.controller.grouped_documents.keys())
        self.assertEqual(len(self.controller.grouped_documents["NOV DOKUMENT (1)"]), 3)

        self.assertIn("NOV DOKUMENT (2)", self.controller.grouped_documents.keys())
        self.assertEqual(len(self.controller.grouped_documents["NOV DOKUMENT (2)"]), 3)

        self.assertRaises(ValueError, self.controller.create_new_document, [])


if __name__ == '__main__':
    unittest.main()
