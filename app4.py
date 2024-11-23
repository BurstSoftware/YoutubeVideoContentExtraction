# app.py
import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi

def fetch_transcript(url):
    try:
        video_id = url.split("v=")[1]
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        return " ".join([t["text"] for t in transcript_list])
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return None

st.title("YouTube Transcript Extractor")

url = st.text_input("Enter YouTube URL")
if st.button("Get Transcript"):
    if url:
        transcript = fetch_transcript(url)
        if transcript:
            st.write(transcript)
