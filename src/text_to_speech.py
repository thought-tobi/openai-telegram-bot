import logging
import os
import uuid

import requests
from dotenv import load_dotenv

# voice: rachel
ELEVEN_LABS_API_BASE = "https://api.elevenlabs.io/v1"
voices = {
    "bella": "EXAVITQu4vr4xnSDxMaL",
    "trump": "6gYZDEbOjI0JvdjKspHv",
    "peterson": "meZSfOJUZoVnXBcCEVvg",
}
JSON = {
    "text": "Hello World!",
    "voice_settings": {
        "stability": 0.8,
        "similarity_boost": 0.8
    }
}


# model defaults to bella
def text_to_speech(text: str, model_id: str = "bella"):
    JSON["text"] = text
    headers = {"xi-api-key": os.getenv("ELEVENLABS_API_KEY")}
    logging.info(f"Sending text-to-speech request for text '{text}'")
    response = requests.post(f"{ELEVEN_LABS_API_BASE}/text-to-speech/{voices.get(model_id)}", json=JSON,
                             headers=headers)
    if response.status_code != 200:
        raise RuntimeError(f"Request failed with status code {response.status_code}, reason {response.text}")
    logging.info(f"Received response in {response.elapsed} (text length: {len(text)}))")
    filename = f"tmp/{uuid.uuid4()}.mp3"
    with open(filename, "wb") as f:
        f.write(response.content)
    return filename


def get_voices():
    headers = {"xi-api-key": os.getenv("ELEVENLABS_API_KEY")}
    response = requests.get(f"{ELEVEN_LABS_API_BASE}/voices", headers=headers)
    print(response.json())


if __name__ == "__main__":
    load_dotenv()
    get_voices()
