import streamlit as st
import requests
from gtts import gTTS
import google.generativeai as genai
from PIL import Image
from io import BytesIO
import urllib.parse
import hashlib

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
Write a clear, emotionally engaging story suitable for children, adults, and elders.

Rules:
- Simple vocabulary
- Short sentences
- Emotional but gentle tone
- No graphic violence
- No disturbing descriptions
- Use at most 5 main characters

FORMAT EXACTLY AS:

Title:
{title}

Genre:
{genre}

Concept:
Rewrite the concept below clearly with correct grammar.

Original Concept:
{description}

Characters:
1. Name:
   One short line describing the character.

2. Name:
   One short line describing the character.

(Continue numbering if needed, max 5.)

Introduction:
(4–5 short lines)

Story:
(8–10 short lines)

Conclusion:
(3–4 short lines)

Keep under 250 words.
"""
    response = model.generate_content(prompt)
    return response.text.strip()

# --------------------------------------------------
# VISUAL PROMPT (SCENE EXTRACTION)
# --------------------------------------------------
def generate_visual_prompt(story_text):
    prompt = f"""
Extract ONE clear visual scene from the story.

Rules:
- Describe only visible elements
- Characters, environment, action
- No emotions
- No camera terms
- Max 50 words

Story:
{story_text}
"""
    response = model.generate_content(prompt)
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
def generate_image(story_text, title, genre, description):
    HF_TOKEN = st.secrets["HF_TOKEN"]

    API_URL = "https://api-inference.huggingface.co/models/runwayml/stable-diffusion-v1-5"

    headers = {
        "Authorization": f"Bearer {HF_TOKEN}"
    }

    visual_scene = generate_visual_prompt(story_text)

    payload = {
        "inputs": visual_scene
    }

    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=120)

        if response.status_code != 200:
            st.error(f"HuggingFace Error: {response.status_code}")
            return None

        return Image.open(BytesIO(response.content))

    except Exception as e:
        st.error(f"Image generation failed: {e}")
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
# MAIN
# --------------------------------------------------
if st.button("✨ Generate Story Weave"):
    if not story_title or not description:
        st.warning("Please provide title and concept.")
    else:
        with st.spinner("Generating story..."):
            st.session_state.story = generate_story(
                story_title, genre, description
            )

        with st.spinner("Creating illustration..."):
            st.session_state.image = generate_image(
                st.session_state.story,
                story_title,
                genre,
                description
            )

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
        audio = generate_audio(st.session_state.story)
        st.audio(audio)

# --------------------------------------------------
# FOOTER
# --------------------------------------------------
st.markdown("---")
st.caption("Story Weave • AI-powered Multimodal Storytelling")
st.caption("Developed by Kokala Sai Teja")
