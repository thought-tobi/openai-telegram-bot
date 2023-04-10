import logging
import os
import uuid

import requests
from dotenv import load_dotenv

VOICES = {
    "bella": "EXAVITQu4vr4xnSDxMaL",
    "donald trump": "6gYZDEbOjI0JvdjKspHv",
    "jordan peterson": "meZSfOJUZoVnXBcCEVvg",
    "snoop dogg": "RpSFkaZbsz2v2aO78CPw",
    "ben shapiro": "r8jl0Lb8nWKyr8U82q7o"
}

PAYLOAD = {
    "text": "Hello World!",
    "voice_settings": {
        "stability": 0.8,
        "similarity_boost": 0.8
    }
}

API_BASE = "https://api.elevenlabs.io/v1"
HEADERS = {"xi-api-key": os.getenv("ELEVENLABS_API_KEY")}


def elevenlabs_tts(text: str, model_id: str = "bella") -> str:
    logging.info(f"Sending text-to-speech request for text '{text}'")
    PAYLOAD["text"] = text
    response = requests.post(f"{API_BASE}/text-to-speech/{VOICES.get(model_id)}", json=PAYLOAD,
                             headers=HEADERS)

    logging.info(f"Received response in {response.elapsed} (text length: {len(text)}))")
    if response.status_code != 200:
        raise RuntimeError(f"Request failed with status code {response.status_code}, reason {response.text}")

    filename = f"tmp/{uuid.uuid4()}.mp3"
    with open(filename, "wb") as f:
        f.write(response.content)
    return filename


def get_voices():
    headers = {"xi-api-key": os.getenv("ELEVENLABS_API_KEY")}
    response = requests.get(f"{API_BASE}/voices", headers=headers)
    print(response.json())


if __name__ == "__main__":
    load_dotenv()
    get_voices()
