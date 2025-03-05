"""
Setup script for WinRegi application
"""
import os
import sys
from setuptools import setup, find_packages

# Check if running on Windows
if not sys.platform.startswith('win'):
    print("WinRegi is only compatible with Windows")
    sys.exit(1)

# Get current directory
current_dir = os.path.abspath(os.path.dirname(__file__))

# Read required packages from requirements.txt
with open(os.path.join(current_dir, 'requirements.txt'), 'r') as f:
    requirements = f.read().splitlines()

setup(
    name="winregi",
    version="0.1.0",
    description="AI-Powered Windows Registry Manager",
    author="WinRegi Team",
    author_email="info@winregi.com",
    url="https://github.com/winregi/winregi",
    packages=find_packages(),
    package_data={
        '': ['*.png', '*.ico', '*.json'],
    },
    entry_points={
        'console_scripts': [
            'winregi=main:main',
        ],
    },
    install_requires=requirements,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Operating System :: Microsoft :: Windows",
    ],
    python_requires='>=3.8',
)