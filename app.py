import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi
import requests
import re

# --- Config ---
GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

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

# --- Helper: Call Groq ---
def summarize_with_groq(transcript):
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [{
            "role": "user",
            "content": f"""Summarize the following YouTube video transcript.

Provide:
1. A clear 3-5 sentence summary
2. 5 key takeaways as bullet points
3. The main topic/theme in one line

Transcript:
{transcript[:8000]}"""
        }]
    }
    response = requests.post(GROQ_URL, headers=headers, json=payload)
    result = response.json()
    if "choices" in result:
        return result["choices"][0]["message"]["content"]
    else:
        return f"❌ Error: {result}"

# --- Streamlit UI ---
st.set_page_config(page_title="YouTube Summarizer", page_icon="🎬")
st.title("🎬 AI YouTube Summarizer")
st.markdown("Paste a YouTube URL and get an instant AI-powered summary!")

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
                    summary = summarize_with_groq(transcript)
                    st.success("Done!")
                    st.markdown("## 📝 Summary")
                    st.markdown(summary)
                except Exception as e:
                    st.error(f"Error: {str(e)}")