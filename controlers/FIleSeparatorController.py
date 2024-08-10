class FileSeparatorController:
    def __init__(self):
        self.documents: list[str] = []
        self.grouped_documents: dict[str: list[str]] = {}

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

    def set_documents(self, documents: list[str]):
        ...

    def group_documents(self):
        ...

    def rename_document(self, old_name: str, new_name: str):
        ...

    def rearrange_documents(self, idx_from: int, idx_to: int):
        ...

    def delete_document_pages(self, document_name: str, indexes: list[int]):
        ...

    def delete_document(self, document_name: str):
        ...

    def create_new_document(self, document_name: str, pages: list[str]):
        ...

    def clear_grouped_documents(self):
        ...

    def clear_documents(self):
        ...

    def load_settings(self):
        ...

    def save_settings(self):
        ...

    def get_setting(self, key):
        ...

    def set_setting(self, key, value):
        ...

    def save_grouped_documents(self):
        ...
