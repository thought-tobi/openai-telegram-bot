#!/usr/bin/env bash

source venv/bin/activate
pip install -r requirements.txt
python src/app.py > logs &