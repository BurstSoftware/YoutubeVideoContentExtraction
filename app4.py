# requirements.txt
streamlit==1.32.0
youtube_transcript_api==0.6.1

# app.py
import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound
import re

def extract_video_id(url: str) -> str:
    """
    Extract YouTube video ID from various URL formats.
    
    Args:
        url (str): YouTube URL in any format
        
    Returns:
        str: Video ID or None if not found
    """
    # Patterns for different YouTube URL formats
    patterns = [
        r'(?:v=|/v/|youtu\.be/|/embed/)([^&?\n]+)',  # Standard, shortened and embed URLs
        r'(?:watch\?|/v/|youtu\.be/|/embed/)([^&?\n]+)'  # Other variations
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None

def fetch_youtube_transcript(video_url: str) -> str:
    """
    Fetches the transcript of a YouTube video.
    
    Args:
        video_url (str): The URL of the YouTube video.
        
    Returns:
        Optional[str]: The transcript of the video or None if any error occurs.
    """
    try:
        # Extract the video ID using the improved function
        video_id = extract_video_id(video_url)
        
        if not video_id:
            st.error("Invalid YouTube URL format. Please check the URL.")
            return None
            
        # Fetch the transcript using the YouTubeTranscriptApi
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        
        # Joining the text of all transcript segments with proper spacing
        transcript = ' '.join([segment['text'].strip() for segment in transcript_list])
        return transcript
        
    except (TranscriptsDisabled, NoTranscriptFound):
        st.error("Transcript is not available for this video. This could be because:\n"
                "1. Subtitles are disabled\n"
                "2. No transcript exists\n"
                "3. The video is private or age-restricted")
        return None
    except ValueError as e:
        st.error(f"Invalid video URL: {e}")
        return None
    except Exception as e:
        st.error(f"An unexpected error occurred: {str(e)}")
        return None

def main():
    # Set page config
    st.set_page_config(
        page_title="YouTube Transcript Extractor",
        page_icon="📝",
        layout="wide"
    )
    
    # Main UI
    st.title("📝 YouTube Video Transcript Extraction")
    st.write("Enter the URL of a YouTube video to fetch its transcript.")
    
    # Input field for the YouTube video URL
    video_url = st.text_input(
        "YouTube Video URL",
        placeholder="https://www.youtube.com/watch?v=example"
    )
    
    # Add a try sample button
    if st.button("Try with sample video"):
        video_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        st.session_state['video_url'] = video_url
        st.experimental_rerun()
    
    # Fetch and display transcript when the button is clicked
    if st.button("Get Transcript"):
        if video_url:
            with st.spinner("Fetching transcript..."):
                transcript = fetch_youtube_transcript(video_url)
                if transcript:
                    st.success("Transcript fetched successfully!")
                    
                    # Display transcript in a scrollable text area
                    st.text_area(
                        "Transcript",
                        transcript,
                        height=300,
                        key="transcript_area"
                    )
                    
                    # Add download button
                    st.download_button(
                        label="Download Transcript",
                        data=transcript,
                        file_name="transcript.txt",
                        mime="text/plain"
                    )
        else:
            st.warning("Please provide a YouTube video URL.")

if __name__ == "__main__":
    main()
