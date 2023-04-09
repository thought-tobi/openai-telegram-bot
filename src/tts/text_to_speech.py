from src.data.session import Session
from src.tts.elevenlabs import elevenlabs_tts
from src.tts.polly import polly_tts
from src.tts.tts import DEFAULT_VOICE


def tts(text: str, session: Session) -> str:
    tts_function = determine_tts_api(session)
    return tts_function(text, session.tts.voice)


def determine_tts_api(session: Session):
    return polly_tts if session.tts.voice == DEFAULT_VOICE else elevenlabs_tts
