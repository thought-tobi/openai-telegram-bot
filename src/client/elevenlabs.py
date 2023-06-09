import logging
import os
import uuid

import requests
from dotenv import load_dotenv

PAYLOAD = {
    "text": "Hello World!",
    "voice_settings": {
        "stability": 0.8,
        "similarity_boost": 0.8
    }
}

API_BASE = "https://api.elevenlabs.io/v1"


def tts(text: str, model_id: str) -> str:
    logging.info(f"Sending text-to-speech request for text '{text}'")
    PAYLOAD["text"] = text
    headers = {"xi-api-key": os.getenv("ELEVENLABS_API_KEY")}
    response = requests.post(f"{API_BASE}/text-to-speech/{model_id}", json=PAYLOAD, headers=headers)

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


# utility in case you need to check for your voice ids; elevenlabs doesn't offer an easier way of fetching them
if __name__ == "__main__":
    load_dotenv()
    get_voices()
