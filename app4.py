import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound


def fetch_youtube_transcript(video_url: str):
    """
    Fetches the transcript of a YouTube video.

    Given a URL of a YouTube video, this function uses the youtube_transcript_api
    to fetch the transcript of the video.

    Args:
        video_url (str): The URL of the YouTube video.

    Returns:
        Optional[str]: The transcript of the video or None if any error occurs.
    """
    try:
        # Extract the video ID from the URL
        video_id = video_url.split("v=")[1]
        # Fetch the transcript using the YouTubeTranscriptApi
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        # Joining the text of all transcript segments
        transcript = ' '.join([segment['text'] for segment in transcript_list])
        return transcript
    except (TranscriptsDisabled, NoTranscriptFound):
        # Return None if transcripts are disabled or not found
        return None
    except Exception as e:
        st.error(f"An error occurred: {e}")
        return None


# Streamlit App
def main():
    st.title("YouTube Video Transcript Extraction")
    st.write("Enter the URL of a YouTube video to fetch its transcript.")

    # Input field for the YouTube video URL
    video_url = st.text_input("YouTube Video URL", placeholder="https://www.youtube.com/watch?v=example")

    # Fetch and display transcript when the button is clicked
    if st.button("Get Transcript"):
        if video_url:
            with st.spinner("Fetching transcript..."):
                transcript = fetch_youtube_transcript(video_url)
                if transcript:
                    st.success("Transcript fetched successfully!")
                    st.text_area("Transcript", transcript, height=300)
                else:
                    st.warning("Transcript not available or an error occurred.")
        else:
            st.error("Please provide a valid YouTube video URL.")

# Run the Streamlit app
if __name__ == "__main__":
    main()
