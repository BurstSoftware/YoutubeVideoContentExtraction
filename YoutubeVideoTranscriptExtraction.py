from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound
from typing import Optional


def fetch_youtube_transcript(video_url: str) -> Optional[str]:
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
        print(f"An error occurred: {e}")
        return None

# Example usage
video_url = "https://www.youtube.com/watch?v=4ZqJSfV4818"
transcript = fetch_youtube_transcript(video_url)
print(transcript if transcript else "Transcript not available or an error occurred.")
