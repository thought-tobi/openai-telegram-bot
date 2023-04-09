import logging
import os
import uuid
import boto3

import requests
from dotenv import load_dotenv

# voice: rachel
ELEVEN_LABS_API_BASE = "https://api.elevenlabs.io/v1"
voices = {
    "bella": "EXAVITQu4vr4xnSDxMaL",
    "donald trump": "6gYZDEbOjI0JvdjKspHv",
    "jordan peterson": "meZSfOJUZoVnXBcCEVvg",
    "snoop dogg": "RpSFkaZbsz2v2aO78CPw",
    "ben shapiro": "r8jl0Lb8nWKyr8U82q7o"
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


def test_polly():
    polly = boto3.client("polly")
    response = polly.synthesize_speech(
        OutputFormat="mp3",
        Text="Hello World!",
        VoiceId="Joanna"
    )
    filename = f"tmp/{uuid.uuid4()}.mp3"
    with open(filename, "wb") as f:
        f.write(response["AudioStream"].read())
    return filename


if __name__ == "__main__":
    load_dotenv()
    # get_voices()
    test_polly()
