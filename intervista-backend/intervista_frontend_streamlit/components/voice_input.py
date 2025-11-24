import speech_recognition as sr
import pyttsx3
import threading
import queue

# Global TTS engine
engine = pyttsx3.init()
engine.setProperty('rate', 180)
engine.setProperty('volume', 1.0)

# Queue to serialize TTS calls
tts_queue = queue.Queue()

def tts_worker():
    while True:
        text = tts_queue.get()
        if text is None:
            break
        engine.say(text)
        engine.runAndWait()
        tts_queue.task_done()

# Start TTS worker thread
threading.Thread(target=tts_worker, daemon=True).start()

# ---------------------------
# Voice Input
# ---------------------------
def get_voice_input() -> str:
    r = sr.Recognizer()
    r.pause_threshold = 1.0  # allow brief pauses
    with sr.Microphone() as source:
        print("🎙️ Listening... Speak now!")
        audio = r.listen(source,timeout=None, phrase_time_limit=None)
    try:
        return r.recognize_google(audio)
    except sr.UnknownValueError:
        return ""
    except sr.RequestError as e:
        return f"Error: {e}"

# ---------------------------
# Speak Text (Queued)
# ---------------------------
def speak_text(text: str):
    if text:
        tts_queue.put(text)
