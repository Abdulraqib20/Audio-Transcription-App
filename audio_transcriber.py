import streamlit as st
import numpy as np
from st_audiorec import st_audiorec
import assemblyai as aai
from configure import api_key
import os
import requests
import io

# Create a Streamlit app
st.set_page_config(
    page_title="Raqib's Audio Transcription App",
    layout="wide",
)

# Center-align subheading and image using HTML <div> tags
st.markdown(
    """
    <div style="display: flex; flex-direction: column; align-items: center; text-align: center;">
        <h1>Audio & Recording Transcription App</h1>
        <img src="james-kovin-F2h_WbKnX4o-unsplash (1).jpg" style="width: 70%; margin-top: 10px;">
    </div>
    """,
    unsafe_allow_html=True
)
st.image("james-kovin-F2h_WbKnX4o-unsplash (1).jpg")

# Add an introductory paragraph
st.markdown("""
This simple yet powerful tool allows you to transcribe audio files or recording to text effortlessly. Choose between two convenient options:

1. **Upload Audio File**: Upload any audio file in formats such as MP3, WAV, OGG, or AAC. Your file will be transcribed to text, providing you with a written record of the audio content.

2. **Record Audio on the App**: If you prefer to speak and transcribe in real-time, use the built-in audio recorder. Click on the "Start Recording" button, speak into your microphone, and then either save the recording or transcribe it directly.

**Instructions:**
- For uploading an audio file, click on the "Choose a local audio file" button and select the desired file. Once uploaded, you can transcribe the content by clicking on the "Transcribe Audio" button.
- To record audio directly on the app, click on the "Start Recording" button. Speak into your microphone, then choose to save the recording or transcribe it immediately.

**Note: The app supports various audio file formats, including MP3, WAV, OGG, and AAC.**
""")

def save_audio_file(audio_data, file_path='recorded_audio.wav'):
    # Save audio data as a WAV file
    np.array(audio_data).tofile(file_path)

def transcribe_audio(api_key, audio_path):
    # Upload audio file to AssemblyAI
    st.subheader("Uploading Audio File to be Transcribed to Text")
    bar = st.progress(0)

    headers = {'authorization': api_key}
    with open(audio_path, 'rb') as audio_file:
        response = requests.post('https://api.assemblyai.com/v2/upload',
                                 headers=headers,
                                 data=read_file(audio_file))
    audio_url = response.json().get('upload_url')
    bar.progress(20)

    # Transcribe uploaded audio file
    st.markdown("#### Transcribing Uploaded Audio File...")
    endpoint = "https://api.assemblyai.com/v2/transcript"

    json_data = {
        "audio_url": audio_url
    }

    headers = {
        "authorization": api_key,
        "content-type": "application/json"
    }

    transcript_input_response = requests.post(endpoint, json=json_data, headers=headers)
    bar.progress(40)

    # Extract transcript ID
    transcript_id = transcript_input_response.json().get("id")
    bar.progress(60)

    # Retrieve transcription results
    st.markdown("#### Retrieving Transcription Results...")
    endpoint = f"https://api.assemblyai.com/v2/transcript/{transcript_id}"
    transcript_output_response = requests.get(endpoint, headers=headers)

    # Check if transcription is complete
    while transcript_output_response.json().get('status') != 'completed':
        transcript_output_response = requests.get(endpoint, headers=headers)

    # Print transcribed text when complete
    if transcript_output_response.json().get('status') == 'completed':
        st.header('Audio Transcription Output')
        transcribed_text = transcript_output_response.json().get("text")
        st.success(transcribed_text)
        return transcribed_text
    else:
        st.error('Transcription failed or was not completed.')
        return None

def read_file(file_object, chunk_size=5242880):
    # Read file content in chunks
    while True:
        data = file_object.read(chunk_size)
        if not data:
            break
        yield data

def audiorec_demo_app():
    uploaded_file = st.file_uploader("Choose a local audio file", type=["mp3", "wav", "ogg", "aac"])

    if uploaded_file is not None:
        # If an audio file is uploaded
        audio_path = f"uploaded_audio.{uploaded_file.name.split('.')[-1]}"
        with open(audio_path, 'wb') as audio_file:
            audio_file.write(uploaded_file.read())

        # Display audio data as received on the Python side
        col_playback, col_space = st.columns([0.58, 0.42])
        with col_playback:
            st.audio(audio_path, format='audio/wav')

        # Add a button to transcribe the uploaded audio file
        if st.button("Transcribe Audio"):
            transcribe_audio(api_key, audio_path)

    else:
        # If no audio file is uploaded, allow recording
        wav_audio_data = st_audiorec()

        if wav_audio_data is not None:
            # Display audio data as received on the Python side
            col_playback, col_space = st.columns([0.58, 0.42])
            with col_playback:
                st.audio(wav_audio_data, format='audio/wav')

            # Add a button to save the recorded audio as a file
            if st.button("Save Recording"):
                save_audio_file(wav_audio_data)
                st.success("Recording successfully saved!")

            # Add a button to transcribe the saved audio file
            if st.button("Transcribe Audio"):
                transcribe_audio(api_key, 'recorded_audio.wav')

if __name__ == '__main__':
    audiorec_demo_app()

# footer
# line separator
st.markdown('<hr style="border: 2px solid #ddd;">', unsafe_allow_html=True)

# footer text
st.markdown(
    """
    <div style="text-align: center; padding: 10px;">
        Developed by <a href="https://github.com/Abdulraqib20" target="_blank">raqibcodes</a>
    </div>
    """,
    unsafe_allow_html=True
)
