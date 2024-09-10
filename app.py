import os
import gradio as gr
from gradio_client import Client, handle_file
from dotenv import load_dotenv
from groq import Groq

# Load environment variables from a .env file
load_dotenv()

# Define the path to the directory containing the audio files
AUDIO_DIR = "audio"

# Get a list of all audio files in the directory
audio_files = [os.path.join(AUDIO_DIR, f) for f in os.listdir(AUDIO_DIR) if f.endswith('.wav')]

# Initialize a global variable to keep track of the current audio file index
current_index = 0

# Initialize a dictionary to store the transcriptions
transcriptions_dict = {}

# Define the function to process the user-recorded audio
def transcribe(audio):
    # Initialize the client
    client = Client("shishirab/STTS")
    
    # Send the audio file to the endpoint and get the result
    result = client.predict(
        param_0=handle_file(audio),
        api_name="/predict"
    )
    
    # Extract the text part using string manipulation
    start_idx = result.find("text='") + len("text='")
    end_idx = result.rfind("', chunks=None")
    extracted_text = result[start_idx:end_idx]
    print(result)
    return extracted_text

# Define a function to get the next audio file and play it
def next_audio():
    global current_index
    if current_index >= len(audio_files):
        current_index = 0  # Loop back to the start
    audio_file = audio_files[current_index]
    current_index += 1
    return audio_file

# Define a function to store the transcription with the audio file name
def store_transcription(transcription):
    if current_index == 0:
        return "No audio file has been played yet."
    
    # Get the name of the last played audio file
    last_audio_file = audio_files[current_index - 1]
    audio_file_name = os.path.basename(last_audio_file)
    
    # Add the transcription and audio file name to the dictionary
    transcriptions_dict[audio_file_name] = transcription
    print(f"Stored transcription for {audio_file_name}")
    print(transcriptions_dict)  # Print the dictionary to check the stored values

    return f"Stored transcription for {audio_file_name}"

# Define a function to calculate the percentage of matching words using the Groq API
def calculate_matches():
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return "API key is not set."
    
    client = Groq(api_key=api_key)
    system_prompt = {
        "role": "system",
        "content": "You are a helpful assistant. You reply with short answers."
    }
    print(str(transcriptions_dict))
    prompt = f"Given the following data where the key contains the words played in an audio file(eg: a-b,c-d.wav here a,b,c,d are words) and the value(A,B,C,D) contains the words spoken by the user, calculate the percentage of words spoken by the user(check if A matchs with a, A with b so on correct match is when A=a ) that match the words played in the audio.MATCH ONLY THE RESPECTIVE KEY VALUE PAIR,no need to be case sensitive. Do not give code, display the words spoken by the user to words in the key:{str(transcriptions_dict)}"
    # prompt += str(transcriptions_dict)
    
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

# Create the Gradio interface
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
        clear_button=gr.Button("Clear_transcription")

    play_button.click(fn=next_audio, outputs=play_audio)
    transcribe_button.click(fn=transcribe, inputs=record_audio, outputs=transcription_box)
    transcription_box.change(fn=store_transcription, inputs=transcription_box, outputs=result_box)
    calculate_button.click(fn=calculate_matches, outputs=calculation_result)
    clear_button.click(fn=clr)
interface.launch(share=True)

