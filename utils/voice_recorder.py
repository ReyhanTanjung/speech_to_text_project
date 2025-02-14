import speech_recognition as sr
from datetime import datetime
from PyQt5.QtCore import QThread, pyqtSignal

class VoiceRecorderThread(QThread):
    textUpdated = pyqtSignal(str, str)  # Changed to emit timestamp and text separately
    recordedUpdated = pyqtSignal(str, str)
    
    def __init__(self, keywords):
        super().__init__()
        self.is_running = True
        self.recognizer = sr.Recognizer()
        self.keywords = keywords
        
    def run(self):
        with sr.Microphone() as source:
            self.recognizer.adjust_for_ambient_noise(source)
            
            while self.is_running:
                try:
                    audio = self.recognizer.listen(source)
                    text = self.recognizer.recognize_google(audio, language="id-ID")
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    
                    self.textUpdated.emit(timestamp, text)
                    
                    if any(keyword.lower() in text.lower() for keyword in self.keywords):
                        self.recordedUpdated.emit(timestamp, text)
                except sr.UnknownValueError:
                    pass
                except sr.RequestError as e:
                    self.textUpdated.emit(
                        datetime.now().strftime("%H:%M:%S"),
                        f"Error: {str(e)}"
                    )
    
    def stop(self):
        self.is_running = False