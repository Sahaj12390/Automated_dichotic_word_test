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

