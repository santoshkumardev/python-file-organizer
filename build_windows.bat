@echo off
python -m pip install pyinstaller
pyinstaller --noconfirm --onefile --windowed --name "PythonFileOrganizer" main.py
pause
