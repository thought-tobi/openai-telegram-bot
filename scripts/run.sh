#!/usr/bin/env bash

# check for ffmpeg and ffprobe
if ! [ -x "$(command -v ffmpeg)" ]; then
    echo 'Error: ffmpeg is not installed.' >&2
    exit 1
fi

# get current directory path
ROOT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
export PYTHONPATH=$PYTHONPATH:$ROOT_DIR

# run mongodb docker image
docker run -d -p 27017:27017 --name mongodb mongo:latest

# activate virtual environment
source venv/bin/activate
python src/app.py &
