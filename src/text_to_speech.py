import logging
import os
import uuid

import requests
from dotenv import load_dotenv

# voice: rachel
ELEVEN_LABS_API_BASE = "https://api.elevenlabs.io/v1"
HEADERS = {"xi-api-key": os.getenv("WHISPER_API_KEY")}
JSON = {
    "text": "Hello World!",
    "voice_settings": {
        "stability": 0,
        "similarity_boost": 0
    }
}


# model defaults to bella
async def text_to_speech(text: str, model_id: str = "EXAVITQu4vr4xnSDxMaL"):
    JSON["text"] = text
    logging.info(f"Sending text-to-speech request for text '{text}'")
    response = requests.post(f"{ELEVEN_LABS_API_BASE}/text-to-speech/{model_id}", json=JSON, headers=HEADERS)
    if response.status_code != 200:
        raise RuntimeError(f"Request failed with status code {response.status_code}, reason {response.text}")
    logging.info(f"Received response in {response.elapsed} (text length: {len(text)}))")
    filename = f"tmp/{uuid.uuid4()}.mp3"
    with open(filename, "wb") as f:
        f.write(response.content)
    return filename


def get_voices():
    response = requests.get(f"{ELEVEN_LABS_API_BASE}/voices", headers=HEADERS)
    print(response.json())


if __name__ == "__main__":
    load_dotenv()
    get_voices()
