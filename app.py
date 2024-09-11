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
def calculate_matches():
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return "API key is not set."
    
      client = Groq(api_key=api_key)
    system_prompt = {
        "role": "system",
        "content": "You are a helpful assistant. You reply with short answers."
    }
    
    prompt = f"Given the following data where the key contains the words played in an audio file " \
             f"and the value contains the words spoken by the user, calculate the percentage of " \
             f"correct matches: {str(transcriptions_dict)}"
    
    chat_history = [system_prompt, {"role": "user", "content": prompt}]
    
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=chat_history,
        max_tokens=1000,
        temperature=0.1
    )
    
    if response and response.choices:
        return response.choices[0].message.content
    else:
        return "No response from the API."
    def calculate_matches():
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return "API key is not set."
    
    # Initialize Groq client
    client = Groq(api_key=api_key)
    system_prompt = {
        "role": "system",
        "content": "You are a helpful assistant. You reply with short answers."
    }
    
    prompt = f"Given the following data where the key contains the words played in an audio file " \
             f"and the value contains the words spoken by the user, calculate the percentage of " \
             f"correct matches: {str(transcriptions_dict)}"
    
    chat_history = [system_prompt, {"role": "user", "content": prompt}]
    
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=chat_history,
        max_tokens=1000,
        temperature=0.1
    )
    
    if response and response.choices:
        return response.choices[0].message.content
    else:
        return "No response from the API."
    def clr():
    return transcriptions_dict.clear()
with gr.Blocks() as interface:
    with gr.Row():
        play_button = gr.Button("Play Next Audio")
        play_audio = gr.Audio(type="filepath", label="Audio", interactive=False)
    
    with gr.Row():
        record_audio = gr.Audio(type="filepath", label="Your Recording")
        transcribe_button = gr.Button("Transcribe Recording")
    
    with gr.Row():
        transcription_box = gr.Textbox(label="Transcription")
        result_box = gr.Textbox(label="Result")
        
    with gr.Row():
        calculate_button = gr.Button("Calculate")
        calculation_result = gr.Textbox(label="Calculation Result")
    
    with gr.Row():
        clear_button = gr.Button("Clear_transcription")

    play_button.click(fn=next_audio, outputs=play_audio)
    transcribe_button.click(fn=transcribe, inputs=record_audio, outputs=transcription_box)
    transcription_box.change(fn=store_transcription, inputs=transcription_box, outputs=result_box)
    calculate_button.click(fn=calculate_matches, outputs=calculation_result)
    clear_button.click(fn=clr)

interface.launch(share=True)


