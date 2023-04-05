#!/usr/bin/env bash

# check if venv folder exists
if [ ! -d "venv" ]; then
    # create virtual environment
    python3 -m venv venv
fi
# activate virtual environment
source venv/bin/activate

# install dependencies
pip install -r requirements.txt

# create directory for writing images or audio files
mkdir -p tmp
chmod 755 tmp
