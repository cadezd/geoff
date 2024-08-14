from __future__ import annotations

import os
import pickle

from utils.Util import is_regex_valid


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

        self.grouped_documents: dict[str, list[str]] = {
            "Document 1": [
                os.path.join("..", "assets", "image0.png"),
                os.path.join("..", "assets", "image1.jpg"),
                os.path.join("..", "assets", "image2.jpg"),
            ],
            "Document 2": [
                os.path.join("..", "assets", "image0.png"),
                os.path.join("..", "assets", "image1.jpg"),
                os.path.join("..", "assets", "image2.jpg"),
            ],
            "Document 3": [
                os.path.join("..", "assets", "image0.png"),
                os.path.join("..", "assets", "image1.jpg"),
                os.path.join("..", "assets", "image2.jpg"),
            ],
            "Document 4": [
                os.path.join("..", "assets", "image0.png"),
                os.path.join("..", "assets", "image1.jpg"),
                os.path.join("..", "assets", "image2.jpg"),
            ],
        }

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


file_separator_controller = FileSeparatorController()
