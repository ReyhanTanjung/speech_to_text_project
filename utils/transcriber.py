# utils/transcriber.py
import speech_recognition as sr
from pydub import AudioSegment
from pydub.utils import make_chunks
import os
import time
from datetime import datetime, timedelta
import numpy as np
from scipy.io import wavfile
import noisereduce as nr
import librosa
from PyQt5.QtCore import QThread, pyqtSignal

class TranscriberThread(QThread):
    progress_updated = pyqtSignal(str)  # For updating progress messages
    result_ready = pyqtSignal(list)     # For sending transcription results
    
    def __init__(self, audio_file, chunk_length_ms=30000):
        super().__init__()
        self.audio_file = audio_file
        self.chunk_length_ms = chunk_length_ms
        self.is_running = True

    def format_timestamp(self, milliseconds):
        seconds = int(milliseconds / 1000)
        return str(timedelta(seconds=seconds))

    def preprocess_audio(self, audio_path):
        self.progress_updated.emit("Memulai preprocessing audio...")
        
        y, sr = librosa.load(audio_path, sr=None)
        
        reduced_noise = nr.reduce_noise(
            y=y,
            sr=sr,
            prop_decrease=1.0,
            stationary=True,
            n_std_thresh_stationary=1.5
        )
        
        normalized = librosa.util.normalize(reduced_noise)
        normalized = (normalized * 32767).astype(np.int16)
        
        preprocessed_path = "preprocessed_audio.wav"
        wavfile.write(preprocessed_path, sr, normalized)
        
        self.progress_updated.emit("Preprocessing audio selesai")
        return preprocessed_path

    def transcribe_audio_chunk(self, chunk, recognizer):
        try:
            chunk = chunk.set_frame_rate(16000)
            chunk = chunk.set_channels(1)
            
            chunk.export("temp_chunk.wav", format="wav")
            
            with sr.AudioFile("temp_chunk.wav") as source:
                audio = recognizer.record(source)
                
            text = recognizer.recognize_google(
                audio,
                language="id-ID",
                show_all=False
            )
            return text
        except sr.UnknownValueError:
            return "[tidak dapat mengenali audio]"
        except sr.RequestError as e:
            return f"[Error: {str(e)}]"
        finally:
            if os.path.exists("temp_chunk.wav"):
                os.remove("temp_chunk.wav")

    def run(self):
        try:
            preprocessed_path = self.preprocess_audio(self.audio_file)
            audio = AudioSegment.from_wav(preprocessed_path)
            
            recognizer = sr.Recognizer()
            recognizer.energy_threshold = 300
            recognizer.dynamic_energy_threshold = True
            recognizer.dynamic_energy_adjustment_damping = 0.15
            recognizer.dynamic_energy_ratio = 1.5
            recognizer.pause_threshold = 0.8
            
            chunks = make_chunks(audio, self.chunk_length_ms)
            self.progress_updated.emit(f"File audio dibagi menjadi {len(chunks)} bagian")
            
            transcription = []
            
            for i, chunk in enumerate(chunks):
                if not self.is_running:
                    break
                    
                start_time = i * self.chunk_length_ms
                end_time = start_time + len(chunk)
                
                self.progress_updated.emit(f"Memproses bagian {i+1}/{len(chunks)}...")
                text = self.transcribe_audio_chunk(chunk, recognizer)
                
                if text and text.strip() and text != "[tidak dapat mengenali audio]":
                    transcription.append({
                        'start_time': self.format_timestamp(start_time),
                        'end_time': self.format_timestamp(end_time),
                        'text': text
                    })
            
            if os.path.exists(preprocessed_path):
                os.remove(preprocessed_path)
                
            self.result_ready.emit(transcription)
            
        except Exception as e:
            self.progress_updated.emit(f"Error: {str(e)}")

    def stop(self):
        self.is_running = False