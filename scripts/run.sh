#!/usr/bin/env bash

# get current directory path
ROOT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
export PYTHONPATH=$PYTHONPATH:$ROOT_DIR

# activate virtual environment
source venv/bin/activate
python src/app.py &

# run mongodb docker image
docker run -d -p 27017:27017 --name mongodb mongo:latest