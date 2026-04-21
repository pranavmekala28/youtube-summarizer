import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi
import requests
import re

# --- Config ---
GEMINI_API_KEY = "AIzaSyA4L1YCT6YYOSlyxpAjfeIyi4qhXQSOlGI"
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"
# --- Helper: Extract Video ID ---
def extract_video_id(url):
    pattern = r"(?:v=|\/)([0-9A-Za-z_-]{11})"
    match = re.search(pattern, url)
    return match.group(1) if match else None

# --- Helper: Get Transcript ---
def get_transcript(video_id):
    ytt = YouTubeTranscriptApi()
    transcript = ytt.fetch(video_id)
    return " ".join([t.text for t in transcript])

# --- Helper: Call Gemini ---
def summarize_with_gemini(transcript):
    payload = {
        "contents": [{
            "parts": [{
                "text": f"""You are a helpful assistant. Summarize the following YouTube video transcript.

Provide:
1. A clear 3-5 sentence summary
2. 5 key takeaways as bullet points
3. The main topic/theme in one line

Transcript:
{transcript[:8000]}"""
            }]
        }]
    }
    response = requests.post(GEMINI_URL, json=payload)
    result = response.json()

    if "candidates" in result:
        return result["candidates"][0]["content"]["parts"][0]["text"]
    elif "error" in result:
        error_msg = result["error"]["message"]
        return f"❌ Gemini API Error: {error_msg}"
    else:
        return f"❌ Unexpected response: {result}"

# --- Streamlit UI ---
st.set_page_config(page_title="YouTube Summarizer", page_icon="🎬")
st.title("🎬 AI YouTube Summarizer")
st.markdown("Paste a YouTube URL and get an instant AI-powered summary using Gemini!")

url = st.text_input("Enter YouTube URL:")

if st.button("Summarize"):
    if not url:
        st.warning("Please enter a YouTube URL.")
    else:
        video_id = extract_video_id(url)
        if not video_id:
            st.error("Invalid YouTube URL. Please try again.")
        else:
            with st.spinner("Fetching transcript and summarizing..."):
                try:
                    transcript = get_transcript(video_id)
                    summary = summarize_with_gemini(transcript)
                    st.success("Done!")
                    st.markdown("## 📝 Summary")
                    st.markdown(summary)
                except Exception as e:
                    st.error(f"Error: {str(e)}")