from gtts import gTTS
import time

def text_to_audio(text):

    filename = f"audio_{int(time.time())}.mp3"

    tts = gTTS(
        text=text,
        lang="en"
    )

    tts.save(filename)

    return filename
