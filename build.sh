#!/bin/bash
echo "Building Discord Message Deleter..."
echo

# Create virtual environment
python3 -m venv build_env
source build_env/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install pyinstaller

# Build executable
pyinstaller --onefile --console --name "DiscordMessageDeleter" message_deleter.py

# Clean up
deactivate
rm -rf build_env
rm -rf build
rm DiscordMessageDeleter.spec

echo
echo "Build complete! Check the 'dist' folder for DiscordMessageDeleter"