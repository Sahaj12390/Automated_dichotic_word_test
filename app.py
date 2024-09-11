import os
import gradio as gr
from gradio_client import Client, handle_file
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

AUDIO_DIR = "audio"

audio_files = [os.path.join(AUDIO_DIR, f) for f in os.listdir(AUDIO_DIR) if f.endswith('.wav')]

current_index = 0

transcriptions_dict = {}

def transcribe(audio):
    client = Client("shishirab/STTS")
    

    result = client.predict(
        param_0=handle_file(audio),
        api_name="/predict"
    )
   
    start_idx = result.find("text='") + len("text='")
    end_idx = result.rfind("', chunks=None")
    extracted_text = result[start_idx:end_idx]
    
    print(result) 
    return extracted_text
def next_audio():
    global current_index
    if current_index >= len(audio_files):
        current_index = 0 
      audio_file = audio_files[current_index]
    current_index += 1
    return audio_file
def store_transcription(transcription):
    if current_index == 0:
        return "No audio file has been played yet."
    last_audio_file = audio_files[current_index - 1]
    audio_file_name = os.path.basename(last_audio_file)
    
    transcriptions_dict[audio_file_name] = transcription
    
    print(f"Stored transcription for {audio_file_name}")
    print(transcriptions_dict)  
    return f"Stored transcription for {audio_file_name}"