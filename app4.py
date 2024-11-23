# app.py
import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi
import re

# Configure Streamlit page
st.set_page_config(
    page_title="YouTube Transcript Fetcher",
    page_icon="📝",
    layout="centered"
)

# Add custom CSS
st.markdown("""
    <style>
        .stButton>button {
            width: 100%;
            margin-top: 10px;
        }
        .stTextInput>div>div>input {
            width: 100%;
        }
    </style>
    """, unsafe_allow_html=True)

def extract_video_id(url: str) -> str:
    """Extract video ID from various YouTube URL formats."""
    if not url:
        return None
        
    patterns = [
        r'(?:v=|\/)([0-9A-Za-z_-]{11}).*',
        r'(?:youtu\.be\/)([0-9A-Za-z_-]{11})',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None

def main():
    st.title("📝 YouTube Transcript Fetcher")
    st.markdown("Enter a YouTube video URL to get its transcript.")
    
    # Input for URL
    url = st.text_input("YouTube URL", placeholder="https://www.youtube.com/watch?v=...")
    
    if st.button("Get Transcript"):
        if not url:
            st.warning("Please enter a YouTube URL")
            return
            
        try:
            video_id = extract_video_id(url)
            if not video_id:
                st.error("Invalid YouTube URL. Please check the URL and try again.")
                return
                
            with st.spinner("Fetching transcript..."):
                transcript = YouTubeTranscriptApi.get_transcript(video_id)
                text = " ".join([t["text"] for t in transcript])
                
                # Create a download button
                st.download_button(
                    label="Download Transcript",
                    data=text,
                    file_name="transcript.txt",
                    mime="text/plain"
                )
                
                # Display transcript in a text area
                st.text_area("Transcript", text, height=300)
                
        except Exception as e:
            st.error(f"Error: {str(e)}")
            st.info("This could be because:\n" +
                   "- The video doesn't have subtitles/transcript\n" +
                   "- The video is private or age-restricted\n" +
                   "- The URL is invalid")

if __name__ == "__main__":
    main()
