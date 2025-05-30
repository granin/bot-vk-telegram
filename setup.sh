#!/bin/bash
set -e

# Install system dependencies required for building Python packages
apt-get update
apt-get install -y --no-install-recommends \
    python3 python3-pip python3-dev build-essential \
    libglib2.0-0 libgl1 libsm6 libxext6 libxrender1

# Upgrade pip and install Python requirements
python3 -m pip install --upgrade pip
pip install -r requirements.txt
