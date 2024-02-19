#!/bin/bash

echo "Building Windows Executable..."
pyinstaller --onefile maktabkhoone_downloader.py

if [ $? -ne 0 ]; then
    echo "Error: PyInstaller failed to build the Windows executable."
    exit 1
fi

echo "Building Debian Package..."
dpkg-deb --build your_project

if [ $? -ne 0 ]; then
    echo "Error: dpkg-deb failed to build the Debian package."
    exit 1
fi

echo "Build process completed successfully."
exit 0
