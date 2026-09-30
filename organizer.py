import json
import shutil
from pathlib import Path
from config import CATEGORY_FILE, DEFAULT_FILE_TYPES


class FileOrganizer:
    def __init__(self):
        self.file_types = self.load_categories()
        self.move_history = []

    def load_categories(self):
        try:
            with open(CATEGORY_FILE, "r", encoding="utf-8") as file:
                return json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            data = DEFAULT_FILE_TYPES.copy()
            self.save_categories(data)
            return data

    def save_categories(self, data=None):
        if data is None:
            data = self.file_types
        with open(CATEGORY_FILE, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4)

    def reset_categories(self):
        self.file_types = DEFAULT_FILE_TYPES.copy()
        self.save_categories()

    def add_or_update_category(self, name, extensions):
        clean_extensions = []
        for ext in extensions:
            ext = ext.strip().lower()
            if not ext:
                continue
            if not ext.startswith("."):
                ext = "." + ext
            clean_extensions.append(ext)

        if not name.strip():
            raise ValueError("Category name cannot be empty.")
        if not clean_extensions:
            raise ValueError("At least one extension is required.")

        self.file_types[name.strip()] = clean_extensions
        self.save_categories()

    def delete_category(self, category):
        if category in self.file_types:
            del self.file_types[category]
            self.save_categories()

    def get_category(self, extension):
        extension = extension.lower()
        for category, extensions in self.file_types.items():
            if extension in extensions:
                return category
        return "Others"

    @staticmethod
    def get_unique_path(destination):
        if not destination.exists():
            return destination

        folder = destination.parent
        stem = destination.stem
        suffix = destination.suffix
        count = 1

        while True:
            new_path = folder / f"{stem}_{count}{suffix}"
            if not new_path.exists():
                return new_path
            count += 1

    def organize(self, folder_path, progress_callback=None, log_callback=None):
        folder = Path(folder_path)
        if not folder.exists():
            raise FileNotFoundError("Selected folder does not exist.")
        if not folder.is_dir():
            raise NotADirectoryError("Selected path is not a folder.")

        files = [item for item in folder.iterdir() if item.is_file()]
        total = len(files)
        if total == 0:
            return 0, 0

        moved = 0
        failed = 0

        for index, file in enumerate(files, start=1):
            try:
                category = self.get_category(file.suffix)
                destination_folder = folder / category
                destination_folder.mkdir(exist_ok=True)
                destination = destination_folder / file.name
                destination = self.get_unique_path(destination)
                original_path = file
                shutil.move(str(file), str(destination))
                self.move_history.append((destination, original_path))
                moved += 1
                if log_callback:
                    log_callback(f"Moved: {file.name} -> {category}")
            except Exception as error:
                failed += 1
                if log_callback:
                    log_callback(f"ERROR: {file.name} -> {error}")
            if progress_callback:
                progress_callback(index, total)

        return moved, failed

    def undo_last(self):
        if not self.move_history:
            return None
        new_path, old_path = self.move_history.pop()
        if not new_path.exists():
            raise FileNotFoundError("Moved file no longer exists.")
        if old_path.exists():
            old_path = self.get_unique_path(old_path)
        shutil.move(str(new_path), str(old_path))
        return old_path
