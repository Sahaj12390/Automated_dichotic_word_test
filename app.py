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


