import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading

from config import APP_NAME, APP_VERSION
from organizer import FileOrganizer


class FileOrganizerApp:
    def __init__(self, root):
        self.root = root
        self.organizer = FileOrganizer()
        self.dark_mode = False

        self.root.title(f"{APP_NAME} v{APP_VERSION}")
        self.root.geometry("840x720")
        self.root.resizable(False, False)

        self.style = ttk.Style()
        try:
            self.style.theme_use("clam")
        except tk.TclError:
            pass

        self.build_ui()
        self.apply_theme()

    def build_ui(self):
        self.title_label = tk.Label(self.root, text=APP_NAME, font=("Arial", 24, "bold"))
        self.title_label.pack(pady=(20, 5))
        self.subtitle_label = tk.Label(self.root, text="Smart file organization with Python automation")
        self.subtitle_label.pack(pady=(0, 15))
        self.theme_button = ttk.Button(self.root, text="Dark Mode", command=self.toggle_theme)
        self.theme_button.pack(pady=5)

        self.folder_frame = tk.Frame(self.root)
        self.folder_frame.pack(pady=10)
        self.folder_entry = ttk.Entry(self.folder_frame, width=68)
        self.folder_entry.pack(side=tk.LEFT, padx=5)
        ttk.Button(self.folder_frame, text="Browse Folder", command=self.select_folder).pack(side=tk.LEFT)

        self.button_frame = ttk.Frame(self.root)
        self.button_frame.pack(pady=10)
        self.organize_button = ttk.Button(self.button_frame, text="Organize Files", command=self.start_organizing)
        self.organize_button.grid(row=0, column=0, padx=8)
        ttk.Button(self.button_frame, text="Undo Last Move", command=self.undo_last).grid(row=0, column=1, padx=8)
        ttk.Button(self.button_frame, text="Manage Categories", command=self.open_category_editor).grid(row=0, column=2, padx=8)

        self.progress = ttk.Progressbar(self.root, orient="horizontal", length=660, mode="determinate")
        self.progress.pack(pady=15)

        self.log_label = tk.Label(self.root, text="Activity Log", font=("Arial", 12, "bold"))
        self.log_label.pack(pady=(10, 5))
        self.log_box = tk.Text(self.root, height=20, width=95)
        self.log_box.pack(padx=20, pady=5)

        self.status_var = tk.StringVar(value="Ready")
        self.status_label = tk.Label(self.root, textvariable=self.status_var, anchor="w", relief=tk.SUNKEN)
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X)

    def add_log(self, message):
        self.root.after(0, self._add_log_ui, message)

    def _add_log_ui(self, message):
        self.log_box.insert(tk.END, message + "\n")
        self.log_box.see(tk.END)

    def update_status(self, message):
        self.root.after(0, self.status_var.set, message)

    def select_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.folder_entry.delete(0, tk.END)
            self.folder_entry.insert(0, folder)
            self.add_log(f"Selected folder: {folder}")
            self.update_status("Folder selected")

    def update_progress(self, current, total):
        self.root.after(0, self._update_progress_ui, current, total)

    def _update_progress_ui(self, current, total):
        self.progress["maximum"] = total
        self.progress["value"] = current

    def start_organizing(self):
        folder_path = self.folder_entry.get().strip()
        if not folder_path:
            messagebox.showwarning("Warning", "Please select a folder.")
            return
        self.organize_button.config(state="disabled")
        self.progress["value"] = 0
        self.update_status("Organizing files...")
        threading.Thread(target=self.organize_worker, args=(folder_path,), daemon=True).start()

    def organize_worker(self, folder_path):
        try:
            moved, failed = self.organizer.organize(
                folder_path,
                progress_callback=self.update_progress,
                log_callback=self.add_log
            )
            self.add_log(f"Completed: {moved} moved, {failed} failed.")
            self.update_status(f"Completed: {moved} files organized")
            self.root.after(0, lambda: messagebox.showinfo(
                "Success", f"{moved} files organized successfully.\nFailed: {failed}"
            ))
        except Exception as error:
            self.add_log(f"ERROR: {error}")
            self.update_status("Error")
            self.root.after(0, lambda: messagebox.showerror("Error", str(error)))
        finally:
            self.root.after(0, lambda: self.organize_button.config(state="normal"))

    def undo_last(self):
        try:
            restored_path = self.organizer.undo_last()
            if restored_path is None:
                messagebox.showinfo("Undo", "Nothing to undo.")
                return
            self.add_log(f"Undo: {restored_path.name} restored")
            self.update_status(f"Restored: {restored_path.name}")
        except Exception as error:
            messagebox.showerror("Undo Error", str(error))

    def open_category_editor(self):
        editor = tk.Toplevel(self.root)
        editor.title("Manage Categories")
        editor.geometry("640x540")
        editor.resizable(False, False)

        ttk.Label(editor, text="Custom Categories", font=("Arial", 18, "bold")).pack(pady=15)
        category_list = tk.Listbox(editor, width=72, height=13)
        category_list.pack(pady=10)

        def refresh_categories():
            category_list.delete(0, tk.END)
            for category, extensions in self.organizer.file_types.items():
                category_list.insert(tk.END, f"{category} -> {', '.join(extensions)}")

        refresh_categories()
        form_frame = ttk.Frame(editor)
        form_frame.pack(pady=15)

        ttk.Label(form_frame, text="Category Name:").grid(row=0, column=0, padx=5, pady=5)
        category_entry = ttk.Entry(form_frame, width=32)
        category_entry.grid(row=0, column=1, padx=5)

        ttk.Label(form_frame, text="Extensions:").grid(row=1, column=0, padx=5, pady=5)
        extension_entry = ttk.Entry(form_frame, width=32)
        extension_entry.grid(row=1, column=1, padx=5)

        ttk.Label(editor, text="Example: .docx, .doc, .odt").pack()

        def add_category():
            try:
                name = category_entry.get().strip()
                extensions = extension_entry.get().split(",")
                self.organizer.add_or_update_category(name, extensions)
                refresh_categories()
                category_entry.delete(0, tk.END)
                extension_entry.delete(0, tk.END)
                self.add_log(f"Category added/updated: {name}")
            except ValueError as error:
                messagebox.showwarning("Warning", str(error))

        def delete_category():
            selection = category_list.curselection()
            if not selection:
                messagebox.showwarning("Warning", "Select a category first.")
                return
            category = list(self.organizer.file_types.keys())[selection[0]]
            if messagebox.askyesno("Delete", f"Delete category '{category}'?"):
                self.organizer.delete_category(category)
                refresh_categories()
                self.add_log(f"Category deleted: {category}")

        def reset_categories():
            if messagebox.askyesno("Reset", "Reset all categories to defaults?"):
                self.organizer.reset_categories()
                refresh_categories()
                self.add_log("Categories reset to defaults")

        editor_buttons = ttk.Frame(editor)
        editor_buttons.pack(pady=15)
        ttk.Button(editor_buttons, text="Add / Update", command=add_category).grid(row=0, column=0, padx=8)
        ttk.Button(editor_buttons, text="Delete", command=delete_category).grid(row=0, column=1, padx=8)
        ttk.Button(editor_buttons, text="Reset Defaults", command=reset_categories).grid(row=0, column=2, padx=8)

    def apply_theme(self):
        if self.dark_mode:
            bg, fg, text_bg, text_fg = "#202124", "#ffffff", "#171717", "#ffffff"
        else:
            bg, fg, text_bg, text_fg = "#f5f7fb", "#1f2937", "#ffffff", "#111827"

        self.root.configure(bg=bg)
        for widget in (self.title_label, self.subtitle_label, self.log_label, self.status_label):
            widget.config(bg=bg, fg=fg)
        self.folder_frame.config(bg=bg)
        self.log_box.config(bg=text_bg, fg=text_fg, insertbackground=text_fg)

    def toggle_theme(self):
        self.dark_mode = not self.dark_mode
        self.apply_theme()
        if self.dark_mode:
            self.theme_button.config(text="Light Mode")
            self.update_status("Dark mode enabled")
        else:
            self.theme_button.config(text="Dark Mode")
            self.update_status("Light mode enabled")


if __name__ == "__main__":
    root = tk.Tk()
    app = FileOrganizerApp(root)
    root.mainloop()
