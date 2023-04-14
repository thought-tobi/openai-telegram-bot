from src.session.session import Session
from src.session.tts import DEFAULT
from src.client.tts.elevenlabs import elevenlabs_tts
from src.client.tts.polly import polly_tts


def tts(text: str, session: Session) -> str:
    tts_function = determine_tts_api(session)
    return tts_function(text, session.tts.voice)


def determine_tts_api(session: Session):
    return polly_tts if session.tts.voice is DEFAULT else elevenlabs_tts
