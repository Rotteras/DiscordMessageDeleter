@echo off
echo Building Discord Message Deleter...
echo.

REM Create virtual environment
python -m venv build_env
call build_env\Scripts\activate

REM Install dependencies
pip install -r requirements.txt
pip install pyinstaller

REM Build executable
pyinstaller --onefile --console --name "DiscordMessageDeleter" message_deleter.py

REM Clean up
deactivate
rmdir /s /q build_env
rmdir /s /q build
del DiscordMessageDeleter.spec

echo.
echo Build complete! Check the 'dist' folder for DiscordMessageDeleter.exe
pause