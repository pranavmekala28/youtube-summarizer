import streamlit as st
import requests
import re
import os
import smtplib
import yt_dlp
import tempfile
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

# --- Config ---
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_WHISPER_URL = "https://api.groq.com/openai/v1/audio/transcriptions"
YOUR_EMAIL = os.environ.get("YOUR_EMAIL")
EMAIL_PASS = os.environ.get("EMAIL_APP_PASS")

st.set_page_config(
    page_title="AI YouTube Summarizer",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 🌌 HYPERSPACE BACKGROUND ---
st.markdown("""
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

.stApp {
    background: #000000;
    overflow: hidden;
}

.starfield {
    position: fixed;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
    z-index: 0;
    pointer-events: none;
    overflow: hidden;
    background: radial-gradient(ellipse at center, #001a33 0%, #000000 70%);
}

.star {
    position: absolute;
    background: white;
    border-radius: 50%;
    animation: warp linear infinite;
}

@keyframes warp {
    0% { transform: translate3d(0, 0, 0) scale(0); opacity: 0; }
    10% { opacity: 1; }
    100% { transform: translate3d(var(--tx), var(--ty), 0) scale(1); opacity: 0; }
}

.warp-core {
    position: fixed;
    top: 50%;
    left: 50%;
    width: 200px;
    height: 200px;
    transform: translate(-50%, -50%);
    background: radial-gradient(circle, rgba(100, 200, 255, 0.6) 0%, rgba(50, 100, 255, 0.3) 30%, transparent 70%);
    border-radius: 50%;
    filter: blur(40px);
    z-index: 1;
    pointer-events: none;
    animation: pulseCore 3s ease-in-out infinite;
}

@keyframes pulseCore {
    0%, 100% { opacity: 0.5; transform: translate(-50%, -50%) scale(1); }
    50% { opacity: 0.9; transform: translate(-50%, -50%) scale(1.2); }
}

.block-container {
    position: relative;
    z-index: 10;
    padding-top: 3rem;
    max-width: 900px;
}

.hero-title {
    font-size: 4.5rem;
    font-weight: 900;
    text-align: center;
    background: linear-gradient(135deg, #00d4ff 0%, #ffffff 50%, #00d4ff 100%);
    background-size: 300% 300%;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 0.5rem;
    animation: holographic 4s ease infinite;
    letter-spacing: -2px;
    filter: drop-shadow(0 0 40px rgba(0, 212, 255, 0.8));
}

@keyframes holographic {
    0%, 100% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
}

.hero-subtitle {
    text-align: center;
    color: rgba(200, 230, 255, 0.9);
    font-size: 1.2rem;
    margin-bottom: 3rem;
    font-weight: 300;
    letter-spacing: 1px;
    text-shadow: 0 0 20px rgba(0, 212, 255, 0.5);
}

.stForm {
    background: rgba(0, 10, 30, 0.7) !important;
    backdrop-filter: blur(20px) saturate(180%) !important;
    border: 1px solid rgba(0, 212, 255, 0.4) !important;
    border-radius: 24px !important;
    padding: 3rem !important;
    box-shadow: 
        0 20px 60px rgba(0, 0, 0, 0.6),
        0 0 80px rgba(0, 212, 255, 0.3) !important;
}

.stTextInput > div > div > input {
    background: rgba(0, 0, 20, 0.6) !important;
    border: 1px solid rgba(0, 212, 255, 0.2) !important;
    border-radius: 12px !important;
    color: white !important;
    padding: 1rem 1.2rem !important;
    font-size: 1rem !important;
}

.stTextInput > div > div > input:focus {
    border-color: #00d4ff !important;
    box-shadow: 0 0 0 3px rgba(0, 212, 255, 0.3) !important;
}

.stTextInput label {
    color: rgba(200, 230, 255, 0.95) !important;
    font-weight: 500 !important;
}

.stFormSubmitButton > button, .stButton > button {
    background: linear-gradient(135deg, #00d4ff 0%, #0066ff 50%, #00d4ff 100%) !important;
    background-size: 200% 200% !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 1rem 2rem !important;
    font-weight: 700 !important;
    font-size: 1.1rem !important;
    width: 100% !important;
    box-shadow: 0 10px 30px rgba(0, 212, 255, 0.5) !important;
    text-transform: uppercase !important;
    letter-spacing: 2px !important;
}

.stFormSubmitButton > button:hover, .stButton > button:hover {
    transform: translateY(-3px) scale(1.02) !important;
}

.stForm h3 {
    color: white !important;
    font-size: 1.5rem !important;
}

.summary-card {
    background: rgba(0, 10, 30, 0.7);
    backdrop-filter: blur(20px) saturate(180%);
    border: 1px solid rgba(0, 212, 255, 0.4);
    border-radius: 24px;
    padding: 3rem;
    margin-top: 2rem;
    color: white;
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.6);
}

.summary-card h2 {
    background: linear-gradient(135deg, #00d4ff 0%, #ffffff 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 1.5rem;
    font-size: 2rem;
}

.stSuccess, .stWarning, .stError {
    background: rgba(0, 10, 30, 0.7) !important;
    border-radius: 12px !important;
    color: white !important;
}

.footer-badge {
    text-align: center;
    margin-top: 4rem;
    padding: 1.5rem;
    color: rgba(200, 230, 255, 0.6);
    position: relative;
    z-index: 10;
}

.footer-badge a {
    color: #00d4ff;
    text-decoration: none;
    font-weight: 700;
}
</style>

<div class="starfield" id="starfield"></div>
<div class="warp-core"></div>

<script>
function createStarfield() {
    const starfield = document.getElementById('starfield');
    if (!starfield) return;
    starfield.innerHTML = '';
    const starCount = 400;
    const centerX = window.innerWidth / 2;
    const centerY = window.innerHeight / 2;
    
    for (let i = 0; i < starCount; i++) {
        const star = document.createElement('div');
        star.className = 'star';
        const angle = Math.random() * Math.PI * 2;
        const distance = 800 + Math.random() * 1200;
        const tx = Math.cos(angle) * distance + 'px';
        const ty = Math.sin(angle) * distance + 'px';
        const size = Math.random() * 3 + 1;
        const duration = Math.random() * 2 + 1.5;
        const delay = Math.random() * 3;
        const colorRand = Math.random();
        let color = '#ffffff';
        let glow = 'rgba(255, 255, 255, 0.8)';
        if (colorRand < 0.3) {
            color = '#00d4ff';
            glow = 'rgba(0, 212, 255, 0.8)';
        } else if (colorRand < 0.5) {
            color = '#88ddff';
            glow = 'rgba(136, 221, 255, 0.8)';
        }
        star.style.cssText = `
            left: ${centerX}px;
            top: ${centerY}px;
            width: ${size}px;
            height: ${size}px;
            background: ${color};
            box-shadow: 0 0 ${size * 4}px ${glow};
            --tx: ${tx};
            --ty: ${ty};
            animation-duration: ${duration}s;
            animation-delay: ${delay}s;
        `;
        starfield.appendChild(star);
    }
}
createStarfield();
window.addEventListener('resize', createStarfield);
setInterval(() => {
    const starfield = document.getElementById('starfield');
    if (starfield && starfield.children.length < 400) createStarfield();
}, 5000);
</script>
""", unsafe_allow_html=True)

# --- Helpers ---
def get_visitor_info():
    try:
        ip_data = requests.get("https://ipapi.co/json/", timeout=5).json()
        return {
            "ip": ip_data.get("ip", "Unknown"),
            "city": ip_data.get("city", "Unknown"),
            "region": ip_data.get("region", "Unknown"),
            "country": ip_data.get("country_name", "Unknown"),
        }
    except:
        return {"ip": "Unknown", "city": "Unknown", "region": "Unknown", "country": "Unknown"}

def notify_me(name, email, video_url, visitor_info):
    if not YOUR_EMAIL or not EMAIL_PASS:
        return
    msg = MIMEMultipart()
    msg["From"] = YOUR_EMAIL
    msg["To"] = YOUR_EMAIL
    msg["Subject"] = f"🚀 New User on QuickSummary AI — {name}"
    body = f"""
🎉 Someone just used your YouTube Summarizer!

👤 USER DETAILS
Name: {name}
Email: {email}

📍 LOCATION
City: {visitor_info['city']}
Region: {visitor_info['region']}
Country: {visitor_info['country']}
IP: {visitor_info['ip']}

🎬 VIDEO
URL: {video_url}

⏰ TIME
{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    """
    msg.attach(MIMEText(body, "plain"))
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(YOUR_EMAIL, EMAIL_PASS)
        server.send_message(msg)
        server.quit()
    except Exception as e:
        print(f"Email failed: {e}")

def extract_video_id(url):
    pattern = r"(?:v=|\/)([0-9A-Za-z_-]{11})"
    match = re.search(pattern, url)
    return match.group(1) if match else None

def download_audio(url):
    """Download audio from YouTube using yt-dlp"""
    tmpdir = tempfile.mkdtemp()
    output_template = os.path.join(tmpdir, "audio.%(ext)s")
    
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': output_template,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '64',
        }],
        'quiet': True,
        'no_warnings': True,
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    
    # Find the downloaded mp3 file
    mp3_path = os.path.join(tmpdir, "audio.mp3")
    if os.path.exists(mp3_path):
        with open(mp3_path, 'rb') as f:
            audio_bytes = f.read()
        os.remove(mp3_path)
        os.rmdir(tmpdir)
        return audio_bytes
    return None

def transcribe_with_groq(audio_bytes):
    """Transcribe audio using Groq's Whisper API"""
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}"}
    files = {
        "file": ("audio.mp3", audio_bytes, "audio/mp3"),
        "model": (None, "whisper-large-v3-turbo"),
    }
    response = requests.post(GROQ_WHISPER_URL, headers=headers, files=files)
    result = response.json()
    if "text" in result:
        return result["text"]
    return None

def summarize_with_groq(transcript):
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
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
    return f"❌ Error: {result}"

# --- 🚀 UI ---
st.markdown('<h1 class="hero-title">🚀 AI YouTube Summarizer</h1>', unsafe_allow_html=True)
st.markdown('<p class="hero-subtitle">Warp through any YouTube video at light speed ✨</p>', unsafe_allow_html=True)

with st.form("user_info"):
    st.markdown("### 👋 Quick intro before we start")
    name = st.text_input("Your Name", placeholder="John Doe")
    email = st.text_input("Your Email", placeholder="john@example.com")
    url = st.text_input("YouTube URL", placeholder="https://www.youtube.com/watch?v=...")
    submitted = st.form_submit_button("🚀 Engage Warp Drive")

if submitted:
    if not name or not email or not url:
        st.warning("⚠️ Please fill in all fields.")
    else:
        video_id = extract_video_id(url)
        if not video_id:
            st.error("❌ Invalid YouTube URL.")
        else:
            try:
                with st.spinner("📥 Downloading audio from YouTube..."):
                    audio_bytes = download_audio(url)
                
                if not audio_bytes:
                    st.error("❌ Could not download audio.")
                else:
                    with st.spinner("🎙️ Transcribing with Whisper AI..."):
                        transcript = transcribe_with_groq(audio_bytes)
                    
                    if not transcript:
                        st.error("❌ Could not transcribe audio.")
                    else:
                        with st.spinner("🔮 Generating summary..."):
                            summary = summarize_with_groq(transcript)
                            visitor_info = get_visitor_info()
                            notify_me(name, email, url, visitor_info)
                        
                        st.success("✅ Summary ready!")
                        st.markdown(f'<div class="summary-card"><h2>📝 Summary</h2>{summary}</div>', unsafe_allow_html=True)
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")

st.markdown("""
<div class="footer-badge">
    Built with ❤️ by <a href="https://github.com/pranavmekala28" target="_blank">Pranav Mekala</a> · Powered by Groq AI + Whisper
</div>
""", unsafe_allow_html=True)
