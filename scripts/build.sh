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

# check for ffmpeg and ffprobe
if ! [ -x "$(command -v ffmpeg)" ]; then
    echo 'ffmpeg is not installed. Installing.'
    pushd opt
    curl -O https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-i686-static.tar.xz
    tar -xvf ffmpeg-release-i686-static.tar.xz
    rm ffmpeg-release-i686-static.tar.xz
    ln -s /opt/ffmpeg-*-i686-static/ff* /usr/bin
    popd
fi