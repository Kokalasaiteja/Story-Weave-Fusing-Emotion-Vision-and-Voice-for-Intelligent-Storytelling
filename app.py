import streamlit as st
import requests
from gtts import gTTS
import google.generativeai as genai
from google.api_core.exceptions import ResourceExhausted
from PIL import Image
from io import BytesIO
import urllib.parse
import hashlib
import time

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------
st.set_page_config(page_title="Story Weave", layout="centered")

# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------
if "story" not in st.session_state:
    st.session_state.story = ""

if "image" not in st.session_state:
    st.session_state.image = None

# --------------------------------------------------
# CONFIG
# --------------------------------------------------
GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=GEMINI_API_KEY)

model = genai.GenerativeModel("gemini-2.5-flash")

# --------------------------------------------------
# SAFE GEMINI CALL (Retry + Backoff)
# --------------------------------------------------
def safe_generate(prompt, retries=3, delay=2):
    for attempt in range(retries):
        try:
            return model.generate_content(prompt)
        except ResourceExhausted:
            if attempt < retries - 1:
                time.sleep(delay * (attempt + 1))
            else:
                st.error("⚠ API quota exceeded. Please try again later.")
                return None
        except Exception as e:
            st.error(f"Unexpected error: {e}")
            return None

# --------------------------------------------------
# UI
# --------------------------------------------------
st.title("📖 Story Weave")
st.caption("Fusing Emotion, Vision & Voice for Intelligent Storytelling")

story_title = st.text_input("Story Title", placeholder="RBC and WBC")

genre = st.selectbox(
    "Genre",
    ["Fantasy", "Science", "Education", "Mythology", "Sci-Fi", "Drama"]
)

description = st.text_area(
    "Story Description / Concept",
    placeholder="Explain how red and white blood cells protect the human body."
)

# --------------------------------------------------
# STORY GENERATION
# --------------------------------------------------
def generate_story(title, genre, description):
    prompt = f"""
Write a clear, emotionally engaging story suitable for all ages.

Rules:
- Simple vocabulary
- Short sentences
- Gentle emotional tone
- No graphic violence
- Use at most 5 characters

FORMAT:

Title:
{title}

Genre:
{genre}

Concept:
Rewrite clearly.

Original Concept:
{description}

Characters:
1. Name: one short line
2. Name: one short line

Introduction:
(4–5 lines)

Story:
(8–10 lines)

Conclusion:
(3–4 lines)

Keep under 200 words.
"""

    response = safe_generate(prompt)
    if response is None:
        return None

    return response.text.strip()

# --------------------------------------------------
# VISUAL SCENE EXTRACTION
# --------------------------------------------------
def generate_visual_prompt(story_text):
    prompt = f"""
Extract ONE clear visual scene from the story.

Rules:
- Describe only visible elements
- Characters, environment, action
- No emotions
- Max 40 words

Story:
{story_text}
"""

    response = safe_generate(prompt)
    if response is None:
        return None

    return response.text.strip()

# --------------------------------------------------
# VISUAL CATEGORY DETECTION
# --------------------------------------------------
def detect_visual_category(title, story):
    t = (title + " " + story).lower()

    if any(w in t for w in ["rbc", "wbc", "cell", "cells", "blood", "bacteria"]):
        return "cells"
    if any(w in t for w in ["man", "woman", "boy", "girl", "wanted", "person", "criminal"]):
        return "human"
    if any(w in t for w in ["plant", "tree", "flower", "rainbow", "forest", "garden"]):
        return "nature"
    if any(w in t for w in ["animal", "bird", "lion", "dog", "cat", "creature"]):
        return "animal"

    return "environment"

# --------------------------------------------------
# IMAGE GENERATION
# --------------------------------------------------
def generate_image(story_text, title):
    visual_scene = generate_visual_prompt(story_text)

    if not visual_scene:
        return None

    visual_scene = visual_scene[:200]

    base_negative = "blurry, low resolution, distorted, extra limbs, text, watermark"

    prompt = f"""
High quality detailed illustration.
Sharp focus.
Scene: {visual_scene}
"""

    encoded_prompt = urllib.parse.quote(prompt + " --no " + base_negative)

    image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=512&height=512&seed=42"

    try:
        response = requests.get(image_url, timeout=60)
        if response.status_code == 200:
            return Image.open(BytesIO(response.content))
        else:
            st.error(f"Image generation failed. Code: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Image request error: {e}")
        return None

# --------------------------------------------------
# AUDIO
# --------------------------------------------------
def generate_audio(text):
    file_hash = hashlib.md5(text.encode()).hexdigest()
    audio_path = f"story_audio_{file_hash}.mp3"
    gTTS(text).save(audio_path)
    return audio_path

# --------------------------------------------------
# MAIN PIPELINE
# --------------------------------------------------
if st.button("✨ Generate Story Weave"):
    if not story_title or not description:
        st.warning("Please provide title and concept.")
    else:
        with st.spinner("Generating story..."):
            story = generate_story(story_title, genre, description)
            st.session_state.story = story

        if story:
            with st.spinner("Creating illustration..."):
                st.session_state.image = generate_image(story, story_title)

# --------------------------------------------------
# DISPLAY
# --------------------------------------------------
if st.session_state.story:
    st.subheader("📜 Generated Story")
    st.write(st.session_state.story)

if st.session_state.image:
    st.subheader("🖼 Generated Image")
    st.image(st.session_state.image, caption=story_title, width=420)

if st.session_state.story:
    if st.button("🔊 Read Aloud Story"):
        audio_file = generate_audio(st.session_state.story)
        st.audio(audio_file)

# --------------------------------------------------
# FOOTER
# --------------------------------------------------
st.markdown("---")
st.caption("Story Weave • AI-powered Multimodal Storytelling")
st.caption("Developed by Kokala Sai Teja")
