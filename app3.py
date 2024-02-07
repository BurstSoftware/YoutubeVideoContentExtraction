import customtkinter as ctk
import pyperclip
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound
from typing import Optional

ctk.set_appearance_mode("System")  # Set the theme to match the system (Dark/Light)
ctk.set_default_color_theme("blue")  # Set the default color theme

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

def on_fetch_button_click():
    video_url = url_entry.get()
    transcript = fetch_youtube_transcript(video_url)
    # Clear the text area before inserting new transcript
    transcript_text.delete(1.0, ctk.END)
    transcript_text.insert(ctk.END, transcript if transcript else "Transcript not available or an error occurred.")

def copy_to_clipboard():
    transcript = transcript_text.get("1.0", ctk.END)
    pyperclip.copy(transcript)
    # Optionally, notify the user that text is copied to clipboard
    print("Transcript copied to clipboard.")

# Set up the GUI
root = ctk.CTk()
root.title("YouTube Transcript Fetcher")

# URL entry
ctk.CTkLabel(root, text="YouTube Video URL:").pack(pady=(10, 0))
url_entry = ctk.CTkEntry(root, width=400)
url_entry.pack(pady=(5, 10))

# Fetch Button
fetch_button = ctk.CTkButton(root, text="Fetch Transcript", command=on_fetch_button_click)
fetch_button.pack()

# Copy to Clipboard Button
copy_button = ctk.CTkButton(root, text="Copy to Clipboard", command=copy_to_clipboard)
copy_button.pack(pady=(10, 10))

# Transcript display area with scrollbar
frame = ctk.CTkFrame(root)
frame.pack(pady=(5, 10), fill="both", expand=True)
transcript_text = ctk.CTkTextbox(frame, width=400, height=200)
transcript_text.pack(side="left", fill="both", expand=True)
scrollbar = ctk.CTkScrollbar(frame, command=transcript_text.yview)
scrollbar.pack(side="right", fill="y")
transcript_text.configure(yscrollcommand=scrollbar.set)

root.mainloop()
