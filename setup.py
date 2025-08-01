"""
Setup script for FileOrbit
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
readme_path = Path(__file__).parent / "README.md"
long_description = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""

# Read requirements
requirements_path = Path(__file__).parent / "requirements.txt"
if requirements_path.exists():
    with open(requirements_path, 'r', encoding='utf-8') as f:
        requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]
else:
    requirements = [
        "PySide6>=6.5.0",
        "watchdog>=3.0.0",
        "Pillow>=10.0.0",
        "psutil>=5.9.0",
        "send2trash>=1.8.0"
    ]

setup(
    name="fileorbit",
    version="1.0.0",
    author="FileOrbit Team",
    author_email="team@fileorbit.com",
    description="Modern dual-pane file manager built with Python and PySide6",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/youruser/FileOrbit",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Desktop Environment :: File Managers",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-qt>=4.2.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
        "build": [
            "pyinstaller>=5.0.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "fileorbit=main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.png", "*.ico", "*.svg", "*.qss"],
    },
)
