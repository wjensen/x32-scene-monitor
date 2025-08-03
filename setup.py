#!/usr/bin/env python3
"""
Setup script for X32 Scene File Monitor
"""

from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Read requirements
def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="x32-scene-monitor",
    version="1.0.0",
    author="X32 Scene File Monitor Team",
    author_email="your-email@example.com",
    description="A Python application that watches X32 scene files and automatically applies changes to the console",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/x32-scene-monitor",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Multimedia :: Sound/Audio :: Mixers",
        "Topic :: System :: Monitoring",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=read_requirements(),
    entry_points={
        "console_scripts": [
            "x32-scene-monitor=x32_scene_monitor:main",
        ],
    },
    keywords="x32, behringer, audio, mixing, console, osc, scene, monitor",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/x32-scene-monitor/issues",
        "Source": "https://github.com/yourusername/x32-scene-monitor",
        "Documentation": "https://github.com/yourusername/x32-scene-monitor#readme",
    },
) 