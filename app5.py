from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound
from typing import Optional, Tuple
from urllib.parse import urlparse, parse_qs
import yt_dlp
import os
import speech_recognition as sr
from pydub import AudioSegment
import tempfile


def extract_video_id(video_url: str) -> Optional[str]:
    """
    Extracts the video ID from various forms of YouTube URLs.

    Args:
        video_url (str): The YouTube video URL

    Returns:
        Optional[str]: The video ID if found, None otherwise
    """
    try:
        parsed_url = urlparse(video_url)

        if parsed_url.hostname in ('www.youtube.com', 'youtube.com'):
            if parsed_url.path == '/watch':
                return parse_qs(parsed_url.query)['v'][0]
            elif parsed_url.path.startswith(('/embed/', '/v/')):
                return parsed_url.path.split('/')[2]
        elif parsed_url.hostname == 'youtu.be':
            return parsed_url.path[1:]

        return None
    except Exception:
        return None


def fetch_youtube_transcript(video_url: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Fetches the transcript of a YouTube video.

    Args:
        video_url (str): The URL of the YouTube video.

    Returns:
        Tuple[Optional[str], Optional[str]]: A tuple containing (transcript, error_message)
    """
    try:
        video_id = extract_video_id(video_url)
        if not video_id:
            return None, "Invalid YouTube URL format"

        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        transcript = ' '.join(segment['text'].strip() for segment in transcript_list)
        return transcript, None

    except TranscriptsDisabled:
        return None, "Transcripts are disabled for this video"
    except NoTranscriptFound:
        return None, "No transcript found for this video"
    except Exception as e:
        return None, f"An unexpected error occurred: {str(e)}"


def download_audio(video_url: str, output_path: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Downloads the audio from a YouTube video.

    Args:
        video_url (str): The URL of the YouTube video
        output_path (str): Path where the audio file should be saved

    Returns:
        Tuple[Optional[str], Optional[str]]: A tuple containing (file_path, error_message)
    """
    try:
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'wav',
                'preferredquality': '192',
            }],
            'outtmpl': output_path,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])

        return f"{output_path}.wav", None
    except Exception as e:
        return None, f"Error downloading audio: {str(e)}"


def transcribe_audio(audio_path: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Transcribes an audio file to text using speech recognition.

    Args:
        audio_path (str): Path to the audio file

    Returns:
        Tuple[Optional[str], Optional[str]]: A tuple containing (transcription, error_message)
    """
    try:
        recognizer = sr.Recognizer()

        # Load audio file
        audio = AudioSegment.from_wav(audio_path)

        # Split audio into chunks to handle long files
        chunk_length_ms = 30000  # 30 seconds
        chunks = [audio[i:i + chunk_length_ms] for i in range(0, len(audio), chunk_length_ms)]

        full_transcript = []

        # Process each chunk
        for i, chunk in enumerate(chunks):
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=True) as temp_audio:
                chunk.export(temp_audio.name, format="wav")
                with sr.AudioFile(temp_audio.name) as source:
                    audio_data = recognizer.record(source)
                    try:
                        text = recognizer.recognize_google(audio_data)
                        full_transcript.append(text)
                    except sr.UnknownValueError:
                        continue
                    except sr.RequestError as e:
                        return None, f"API Error: {str(e)}"

        return " ".join(full_transcript), None
    except Exception as e:
        return None, f"Error transcribing audio: {str(e)}"


def main():
    video_url = input("Enter YouTube video URL: ")

    print("\nChoose an option:")
    print("1. Get YouTube's official transcript")
    print("2. Extract audio and create transcript")
    choice = input("Enter your choice (1 or 2): ")

    if choice == "1":
        transcript, error = fetch_youtube_transcript(video_url)
        if transcript:
            print("\nTranscript:")
            print(transcript)
        else:
            print(f"\nError: {error}")

    elif choice == "2":
        # Create a temporary directory for audio files
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = os.path.join(temp_dir, "audio")

            print("\nDownloading audio...")
            audio_path, error = download_audio(video_url, output_path)

            if error:
                print(f"Error: {error}")
                return

            print("Transcribing audio...")
            transcript, error = transcribe_audio(audio_path)

            if transcript:
                print("\nTranscription:")
                print(transcript)
            else:
                print(f"\nError: {error}")
    else:
        print("Invalid choice. Please select 1 or 2.")


if __name__ == "__main__":
    main()
