import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi
import re
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

# Configure Streamlit page
st.set_page_config(
    page_title="YouTube Transcript Fetcher with Gemini AI",
    page_icon="🧠",
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

def setup_gemini(api_key: str):
    """Configure Gemini AI with API key."""
    try:
        genai.configure(api_key=api_key)
        # Use the Gemini Pro model
        model = genai.GenerativeModel('gemini-pro')
        return model
    except Exception as e:
        raise Exception(f"Error setting up Gemini AI: {str(e)}")

def analyze_with_gemini(model, text: str, task: str = "summarize") -> str:
    """Query Gemini AI to analyze transcript."""
    try:
        prompt = f"Please {task} the following transcript concisely but comprehensively: {text[:30000]}"
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        raise Exception(f"Gemini AI Analysis Failed: {str(e)}")

def main():
    st.title("📝 YouTube Transcript Analyzer with Gemini AI")
    st.markdown("Enter a YouTube video URL and your Google AI API key to get the transcript and analyze it using Gemini AI.")

    # Input fields
    url = st.text_input("YouTube URL", placeholder="https://www.youtube.com/watch?v=...")
    api_key = st.text_input("Google AI API Key", placeholder="Enter your Gemini API key", type="password")

    # Analysis options
    analysis_type = st.selectbox(
        "Choose Analysis Type",
        ["summarize", "identify main topics", "extract key points", "analyze sentiment"]
    )

    if st.button("Get Transcript and Analyze"):
        if not url or not api_key:
            st.warning("Please enter both a YouTube URL and your Gemini API key")
            return

        try:
            # Extract video ID
            video_id = extract_video_id(url)
            if not video_id:
                st.error("Invalid YouTube URL. Please check the URL and try again.")
                return

            # Set up progress tracking
            progress_bar = st.progress(0)
            status_text = st.empty()

            # Fetch transcript
            status_text.text("Fetching transcript...")
            progress_bar.progress(25)
            
            try:
                transcript = YouTubeTranscriptApi.get_transcript(video_id)
                text = " ".join([t["text"] for t in transcript])
                progress_bar.progress(50)
            except Exception as e:
                st.error(f"Error fetching transcript: {str(e)}")
                st.info("This could be because:\n" +
                        "- The video doesn't have subtitles/transcript\n" +
                        "- The video is private or age-restricted\n" +
                        "- The URL is invalid")
                return

            # Display transcript
            with st.expander("View Transcript"):
                st.text_area("Full Transcript", text, height=300)

            # Initialize Gemini and analyze
            status_text.text("Analyzing with Gemini AI...")
            progress_bar.progress(75)
            
            try:
                model = setup_gemini(api_key)
                analysis = analyze_with_gemini(model, text, analysis_type)
                progress_bar.progress(100)
                status_text.empty()

                # Display results
                st.markdown(f"### {analysis_type.title()} Results")
                st.write(analysis)

                # Provide download options
                col1, col2 = st.columns(2)
                with col1:
                    st.download_button(
                        label="Download Transcript",
                        data=text,
                        file_name="transcript.txt",
                        mime="text/plain"
                    )
                with col2:
                    st.download_button(
                        label="Download Analysis",
                        data=analysis,
                        file_name="analysis.txt",
                        mime="text/plain"
                    )

            except Exception as e:
                st.error(f"AI Analysis Error: {str(e)}")
                if "quota" in str(e).lower():
                    st.info("This might be due to API quota limitations or an invalid API key.")

        except Exception as e:
            st.error(f"An unexpected error occurred: {str(e)}")

if __name__ == "__main__":
    main()
