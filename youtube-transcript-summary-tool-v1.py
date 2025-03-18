import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi
import re
import google.generativeai as genai

# Configure Streamlit page
st.set_page_config(
    page_title="YouTube Transcript Analyzer with Gemini AI",
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


def setup_gemini(api_key: str, model_name='gemini-2.0-pro-02-05'):  #  Use the experimental model
    """Configure Gemini AI with API key and handle model availability."""
    try:
        genai.configure(api_key=api_key)
        available_models = [m.name for m in genai.list_models()]

        if model_name not in available_models:
            st.error(f"Model '{model_name}' not found. Available models are: {available_models}")
            return None  # Indicate failure

        model = genai.GenerativeModel(model_name)
        return model

    except Exception as e:
        st.error(f"Error setting up Gemini AI: {str(e)}")
        return None  # Indicate failure



def analyze_with_gemini(model, text: str, task: str = "summarize") -> str:
    """Query Gemini AI to analyze transcript."""
    if not model:
        st.error("Gemini AI model is not initialized.")
        return ""  # Or some other appropriate default

    try:
        prompt = f"Please {task} the following transcript concisely but comprehensively: {text[:30000]}"  #Gemini 2.0 pro supports 32k tokens
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        st.error(f"Gemini AI Analysis Failed: {str(e)}")
        return ""  #Or some other appropriate default



def initialize_session_state():
    """Initialize session state variables if they don't exist."""
    session_vars = {
        'transcript': None,
        'analysis': None,
        'video_id': None,
        'analysis_type': None,
        'model_name': 'gemini-2.0-pro-02-05', # Default to the experimental model
        'url': '',
        'api_key': '',
        'has_data': False,
        'processing_complete': False
    }
    for var, default in session_vars.items():
        if var not in st.session_state:
            st.session_state[var] = default

def display_persistent_content():
    """Display persistent content if it exists."""
    if st.session_state.has_data:
        # Display transcript
        with st.expander("View Transcript", expanded=False):
            st.text_area("Full Transcript", st.session_state.transcript, height=300)
            st.download_button(
                label="Download Transcript",
                data=st.session_state.transcript,
                file_name="transcript.txt",
                mime="text/plain"
            )

        # Display analysis
        st.markdown(f"### {st.session_state.analysis_type.title()} Results")
        st.write(st.session_state.analysis)
        st.download_button(
            label="Download Analysis",
            data=st.session_state.analysis,
            file_name="analysis.txt",
            mime="text/plain"
        )

def main():
    # Initialize session state
    initialize_session_state()

    st.title("📝 YouTube Transcript Analyzer with Gemini AI")
    st.markdown("**Designed and deployed by Nathan Rossow at Burst Software**")
    st.markdown("Enter a YouTube video URL and your Google AI API key to get the transcript and analyze it using Gemini AI.")

    # Input fields - use session state to persist values
    url = st.text_input("YouTube URL",
                        value=st.session_state.url,
                        placeholder="https://www.youtube.com/watch?v=...")
    api_key = st.text_input("Google AI API Key",
                           value=st.session_state.api_key,
                           placeholder="Enter your Gemini API key",
                           type="password")

    # Update session state
    st.session_state.url = url
    st.session_state.api_key = api_key

    # Model selection -  Include the experimental model in the selection.
    model_name = st.selectbox(
        "Choose Gemini Model",
        ["gemini-pro", "gemini-1.0-pro-latest", "gemini-1.5-pro-latest", "gemini-2.0-pro-02-05"],
        index=["gemini-pro", "gemini-1.0-pro-latest", "gemini-1.5-pro-latest", "gemini-2.0-pro-02-05"].index(st.session_state.model_name)
        if st.session_state.model_name in ["gemini-pro", "gemini-1.0-pro-latest", "gemini-1.5-pro-latest", "gemini-2.0-pro-02-05"] else 0
    )
    st.session_state.model_name = model_name # Update session state

    # Analysis options
    analysis_type = st.selectbox(
        "Choose Analysis Type",
        ["summarize",
         "identify main topics",
         "extract key points",
         "analyze sentiment",
         "detailed how-to guide",
         "generate FAQs",
         "create action items",
         "timeline of events",
         "pros and cons list",
         "fact vs. opinion",
         "lesson plan",
         "quiz generator",
         "glossary of terms",
         "case study",
         "comparative analysis",
         "story outline",
         "dialog extraction",
         "script formatting",
         "highlight reel script",
         "create quotes & soundbites",
         "meeting minutes",
         "executive summary",
         "market analysis",
         "presentation outline",
         "press release",
         "social media posts",
         "blog post draft",
         "product review summary",
         "video chapter markers",
         "email newsletter summary",
         "step-by-step process documentation",
         "scientific paper summary",
         "policy brief",
         "code walkthrough",
         "legal brief",
         "beginner-friendly summary",
         "expert-level analysis",
         "multilingual summary",
         "children’s educational content",
         "accessibility summary"]
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

            # Check if we need to fetch new transcript
            fetch_new = (video_id != st.session_state.video_id or
                        st.session_state.transcript is None)

            # Check if we need to reanalyze
            reanalyze = (analysis_type != st.session_state.analysis_type or
                        st.session_state.analysis is None or
                        model_name != st.session_state.model_name)  #Also check model

            # Set up progress tracking
            progress_bar = st.progress(0)
            status_text = st.empty()

            if fetch_new:
                status_text.text("Fetching transcript...")
                progress_bar.progress(25)

                try:
                    transcript = YouTubeTranscriptApi.get_transcript(video_id)
                    text = " ".join([t["text"] for t in transcript])
                    st.session_state.transcript = text
                    st.session_state.video_id = video_id
                    progress_bar.progress(50)
                except Exception as e:
                    st.error(f"Error fetching transcript: {str(e)}")
                    st.info("This could be because:\n" +
                            "- The video doesn't have subtitles/transcript\n" +
                            "- The video is private or age-restricted\n" +
                            "- The URL is invalid")
                    return
            else:
                text = st.session_state.transcript
                progress_bar.progress(50)

            if reanalyze or fetch_new:
                status_text.text("Analyzing with Gemini AI...")
                progress_bar.progress(75)

                try:
                    model = setup_gemini(api_key, model_name) # Pass model_name
                    if model is None:  #Check that model setup was successful
                        return

                    analysis = analyze_with_gemini(model, text, analysis_type)
                    st.session_state.analysis = analysis
                    st.session_state.analysis_type = analysis_type
                    st.session_state.model_name = model_name # Update model name
                    progress_bar.progress(100)
                    status_text.empty()
                except Exception as e:
                    st.error(f"AI Analysis Error: {str(e)}")
                    if "quota" in str(e).lower():
                        st.info("This might be due to API quota limitations or an invalid API key.")
                    return
            else:
                analysis = st.session_state.analysis
                progress_bar.progress(100)
                status_text.empty()

            # Mark that we have data to display
            st.session_state.has_data = True
            st.session_state.processing_complete = True

        except Exception as e:
            st.error(f"An unexpected error occurred: {str(e)}")

    # Add button to list available models
    if st.button("List Available Models"):
        if not api_key:
            st.warning("Please enter your API key first.")
        else:
            try:
                genai.configure(api_key=api_key)
                models = genai.list_models()
                model_names = [model.name for model in models]
                st.write("Available Models:")
                st.write(model_names)
            except Exception as e:
                st.error(f"Error listing models: {e}")


    # Display persistent content
    display_persistent_content()

if __name__ == "__main__":
    main()
