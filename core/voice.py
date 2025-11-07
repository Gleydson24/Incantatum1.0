# core/voice.py
import threading
import queue
import time

voice_queue = queue.Queue()

try:
    import speech_recognition as sr
    HAS_SR = True
except Exception:
    HAS_SR = False
    sr = None

HAS_POCKET = False
if HAS_SR:
    try:
        import pocketsphinx  # noqa: F401
        HAS_POCKET = True
    except Exception:
        HAS_POCKET = False

class VoiceListener(threading.Thread):
    def __init__(self, phrase_time_limit=3, pause_threshold=0.7, energy_threshold=300):
        super().__init__(daemon=True)
        self._stop = threading.Event()
        self.phrase_time_limit = phrase_time_limit
        self.pause_threshold = pause_threshold
        self.energy_threshold = energy_threshold

        self.enabled = HAS_SR
        self.use_pocketsphinx = HAS_POCKET and HAS_SR

        if self.enabled:
            self.recognizer = sr.Recognizer()
            self.recognizer.pause_threshold = float(self.pause_threshold)
            try:
                self.recognizer.energy_threshold = int(self.energy_threshold)
            except Exception:
                pass
        else:
            self.recognizer = None

    def run(self):
        if not self.enabled:
            return

        try:
            mic = sr.Microphone()
        except Exception:
            return

        try:
            with mic as source:
                try:
                    self.recognizer.adjust_for_ambient_noise(source, duration=1.0)
                except Exception:
                    pass
        except Exception:
            return

        while not self._stop.is_set():
            try:
                with mic as source:
                    audio = self.recognizer.listen(source, phrase_time_limit=self.phrase_time_limit)

                if self.use_pocketsphinx:
                    try:
                        text = self.recognizer.recognize_sphinx(audio, language="pt-BR")
                        text = text.strip().lower()
                        if text:
                            voice_queue.put(text)
                        continue
                    except sr.UnknownValueError:
                        continue
                    except Exception:
                        pass

                try:
                    text = self.recognizer.recognize_google(audio, language="pt-BR")
                    text = text.strip().lower()
                    if text:
                        voice_queue.put(text)
                except sr.UnknownValueError:
                    continue
                except sr.RequestError:
                    break
                except Exception:
                    continue

            except Exception:
                time.sleep(0.15)
                continue

    def stop(self):
        self._stop.set()