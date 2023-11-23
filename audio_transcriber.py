import streamlit as st
import assemblyai as aai
from configure import api_key
import os
import requests

# Center-align subheading and image using HTML <div> tags
st.markdown(
    """
    <div style="display: flex; flex-direction: column; align-items: center; text-align: center;">
        <h1>Simple Audio Transcription App</h1>

    </div>
    """,
    unsafe_allow_html=True
)

# Add an introductory paragraph
st.markdown("""
A SImple Audio Transcription Web-App. Upload any type of audio file format to transcribe to text format.
""")

aai.settings.api_key = api_key

def read_file(uploaded_file, chunk_size=5242880):
    with io.BytesIO(uploaded_file.read()) as _file:
        while True:
            data = _file.read(chunk_size)
            if not data:
                break
            yield data

def transcribe_yt(api_key, filename):
    #  Upload audio file to AssemblyAI
    st.subheader("Uploading Audio File")
    bar = st.progress(0)

    headers = {'authorization': api_key}
    response = requests.post('https://api.assemblyai.com/v2/upload',
                             headers=headers,
                             data=read_file(filename))
    audio_url = response.json().get('upload_url')
    bar.progress(20)

    #  Transcribe uploaded audio file
    st.markdown("### Transcribing Uploaded Audio File")
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

    #. Extract transcript ID
    transcript_id = transcript_input_response.json().get("id")
    bar.progress(60)

    # Retrieve transcription results
    st.markdown("### Retrieving Transcription Results")
    # st.subheader("Retrieving Transcription Results")
    endpoint = f"https://api.assemblyai.com/v2/transcript/{transcript_id}"
    transcript_output_response = requests.get(endpoint, headers=headers)

    # Check if transcription is complete
    while transcript_output_response.json().get('status') != 'completed':
        st.warning('Transcription is processing ...')
        transcript_output_response = requests.get(endpoint, headers=headers)

    # Print transcribed text when complete
    if transcript_output_response.json().get('status') == 'completed':
        st.header('Audio Transcription Output')
        st.success(transcript_output_response.json().get("text"))
    else:
        st.error('Transcription failed or was not completed.')


    # Print transcribed text
    st.success(transcript_output_response.json().get("text"))

if __name__ == "__main__":
    api_key = api_key  # Replace with your AssemblyAI API key
    uploaded_file = st.file_uploader("Choose a local audio file", type=["mp3", "wav", "ogg"])

    if uploaded_file is not None:
        transcribe_yt(api_key, uploaded_file)

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
