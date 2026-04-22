import streamlit as st
import requests
import re
import os

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
YOUTUBE_API_KEY = os.environ.get("YOUTUBE_API_KEY")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

def extract_video_id(url):
    pattern = r"(?:v=|\/)([0-9A-Za-z_-]{11})"
    match = re.search(pattern, url)
    return match.group(1) if match else None

def get_video_info(video_id):
    url = f"https://www.googleapis.com/youtube/v3/videos?part=snippet&id={video_id}&key={YOUTUBE_API_KEY}"
    response = requests.get(url)
    data = response.json()
    st.write("Debug:", data)  # temporary debug line
    if "items" in data and len(data["items"]) > 0:
        snippet = data["items"][0]["snippet"]
        title = snippet["title"]
        description = snippet["description"]
        return title, description
    return None, None

def summarize_with_groq(title, description):
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [{
            "role": "user",
            "content": f"""Summarize the following YouTube video based on its title and description.

Provide:
1. A clear 3-5 sentence summary
2. 5 key takeaways as bullet points
3. The main topic/theme in one line

Title: {title}
Description: {description[:3000]}"""
        }]
    }
    response = requests.post(GROQ_URL, headers=headers, json=payload)
    result = response.json()
    if "choices" in result:
        return result["choices"][0]["message"]["content"]
    else:
        return f"❌ Error: {result}"

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
            with st.spinner("Fetching video info and summarizing..."):
                try:
                    title, description = get_video_info(video_id)
                    if not title:
                        st.error("Could not fetch video info. Check your API key.")
                    else:
                        summary = summarize_with_groq(title, description)
                        st.success("Done!")
                        st.markdown(f"### 🎥 {title}")
                        st.markdown("## 📝 Summary")
                        st.markdown(summary)
                except Exception as e:
                    st.error(f"Error: {str(e)}")