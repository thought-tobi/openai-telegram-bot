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

NAVY_SEALS_COPYPASTA = """What the fuck did you just fucking say about me, you little bitch? I'll have you know I 
graduated top of my class in the Navy Seals, and I've been involved in numerous secret raids on Al-Quaeda, 
and I have over 300 confirmed kills. I am trained in gorilla warfare and I'm the top sniper in the entire US armed 
forces. You are nothing to me but just another target. I will wipe you the fuck out with precision the likes of which 
has never been seen before on this Earth, mark my fucking words. You think you can get away with saying that shit to 
me over the Internet? Think again, fucker. As we speak I am contacting my secret network of spies across the USA and 
your IP is being traced right now so you better prepare for the storm, maggot. The storm that wipes out the pathetic 
little thing you call your life. You're fucking dead, kid. I can be anywhere, anytime, and I can kill you in over 
seven hundred ways, and that's just with my bare hands. Not only am I extensively trained in unarmed combat, 
but I have access to the entire arsenal of the United States Marine Corps and I will use it to its full extent to 
wipe your miserable ass off the face of the continent, you little shit. If only you could have known what unholy 
retribution your little "clever" comment was about to bring down upon you, maybe you would have held your fucking 
tongue. But you couldn't, you didn't, and now you're paying the price, you goddamn idiot. I will shit fury all over 
you and you will drown in it. You're fucking dead, kiddo. """


# model defaults to bella
def text_to_speech(text: str, model_id: str = "bella"):
    JSON["text"] = text
    headers = {"xi-api-key": os.getenv("ELEVENLABS_API_KEY")}
    logging.info(f"Sending text-to-speech request for text '{text}'")
    response = requests.post(f"{ELEVEN_LABS_API_BASE}/text-to-speech/{voices.get(model_id)}", json=JSON, headers=headers)
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
    # text_to_speech(NAVY_SEALS_COPYPASTA)
    get_voices()
