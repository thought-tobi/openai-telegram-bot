import uuid

import boto3


def polly_tts(text: str, voice: str) -> str:
    polly = boto3.client("polly", region_name="us-east-1")
    response = polly.synthesize_speech(
        OutputFormat="mp3",
        Text=text,
        VoiceId="Joanna"
    )
    filename = f"tmp/{uuid.uuid4()}.mp3"
    with open(filename, "wb") as f:
        f.write(response["AudioStream"].read())
    return filename
