#!/usr/bin/env bash

# check for ffmpeg and ffprobe
if ! [ -x "$(command -v ffmpeg)" ]; then
    echo 'Error: ffmpeg is not installed.' >&2
    exit 1
else
    echo "ffmpeg is installed"
fi

# run mongodb docker image
docker ps --format '{{.Names}}' | grep -q mongo
if [ "$?" -eq 0 ]; then
  echo "mongodb is already running"
else
  docker run -d -p 27017:27017 --name mongodb mongo:latest
fi

# check that .env exists
if [ ! -f .env ]; then
  echo "Error: .env file does not exist." >&2
  exit 1
else
  echo ".env file exists"
fi

# get current directory path
ROOT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
export PYTHONPATH=$PYTHONPATH:$ROOT_DIR

# activate virtual environment
source venv/bin/activate
echo "venv activated"
python src/app.py &
echo "app started, pid $!"
