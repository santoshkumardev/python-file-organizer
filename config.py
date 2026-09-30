from pathlib import Path

APP_NAME = "Python File Organizer"
APP_VERSION = "1.0.0"

BASE_DIR = Path(__file__).resolve().parent
CATEGORY_FILE = BASE_DIR / "categories.json"

DEFAULT_FILE_TYPES = {
    "PDF": [".pdf"],
    "Images": [".jpg", ".jpeg", ".png", ".gif"],
    "Data": [".csv", ".xlsx", ".xls"],
    "Text": [".txt", ".log"],
    "Archives": [".zip", ".rar"]
}
