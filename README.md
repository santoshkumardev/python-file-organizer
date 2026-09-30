# Python File Organizer

A desktop automation tool built with Python and Tkinter that automatically organizes files into folders based on file type.

## Features
- Organize files by extension
- Custom categories
- JSON-based persistent settings
- Duplicate filename protection
- Undo last move
- Progress bar
- Activity log
- Dark / light mode
- Status bar
- Error handling
- Windows EXE build support

## Run
```bash
python main.py
```

## Build Windows EXE
```bash
pyinstaller --onefile --windowed --name "PythonFileOrganizer" main.py
```

The generated EXE will appear in:
```text
dist/PythonFileOrganizer.exe
```
