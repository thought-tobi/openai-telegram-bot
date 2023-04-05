#!/usr/bin/env bash

# create a virtual environment
python3 -m venv venv
source venv/bin/activate

# install dependencies
pip install -r requirements.txt

# create directory for writing images or audio files
mkdir -p tmp
chmod 755 tmp

# pull mongodb docker image
docker pull mongo:latest