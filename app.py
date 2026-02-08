import streamlit as st
import requests
import os
from gtts import gTTS
import google.generativeai as genai
from PIL import Image
from io import BytesIO

if "story" not in st.session_state:
    st.session_state.story = ""

if "image" not in st.session_state:
    st.session_state.image = None

# --------------------------------------------------
# 1. CONFIGURATION & SECRETS
# --------------------------------------------------
st.set_page_config(page_title="Story Weave", layout="centered")

GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
HF_TOKEN = st.secrets["HF_TOKEN"]

genai.configure(api_key=GEMINI_API_KEY)

HF_IMAGE_MODEL = "runwayml/stable-diffusion-v1-5"
HF_API_URL = f"https://api-inference.huggingface.co/models/{HF_IMAGE_MODEL}"
HF_HEADERS = {"Authorization": f"Bearer {HF_TOKEN}"}

# --------------------------------------------------
# 2. UI
# --------------------------------------------------
st.title("📖 Story Weave")
st.caption("Fusing Emotion, Vision & Voice for Intelligent Storytelling")

story_title = st.text_input("Story Title")
genre = st.selectbox("Genre", ["Fantasy", "Science", "Education", "Mythology", "Sci-Fi", "Drama"])
description = st.text_area("Story Description / Concept")

# --------------------------------------------------
# 3. STORY GENERATION (GEMINI)
# --------------------------------------------------
def generate_story(title, genre, description):
    model = genai.GenerativeModel("gemini-2.5-flash")

    prompt = f"""
    Write a short, well-structured story in THREE sections only.

    Format strictly as:
    Introduction:
    (4–5 lines)

    Story:
    (8–10 lines)

    Conclusion:
    (3–4 lines)

    Title: {title}
    Genre: {genre}
    Concept: {description}

    Keep total length under 250 words.
    """

    response = model.generate_content(prompt)
    return response.text.strip()

# --------------------------------------------------
# 4. IMAGE GENERATION (HF INFERENCE API)
# --------------------------------------------------
def generate_image(story_text):
    try:
        story_part = story_text.split("Story:")[1][:350]
    except:
        story_part = story_text[:350]

    image_prompt = (
        "High quality illustration for this story scene: "
        + story_part +
        ". cinematic lighting, digital art, detailed, realistic"
    )

    payload = {"inputs": image_prompt}
    response = requests.post(
        HF_API_URL,
        headers=HF_HEADERS,
        json=payload,
        timeout=120
    )

    if response.status_code != 200:
        st.warning("Image model is loading. Please click Generate again.")
        return None

    return Image.open(BytesIO(response.content))

# --------------------------------------------------
# 5. AUDIO GENERATION
# --------------------------------------------------
def generate_audio(text):
    tts = gTTS(text)
    audio_path = "story_audio.mp3"
    tts.save(audio_path)
    return audio_path

# --------------------------------------------------
# 6. MAIN PIPELINE
# --------------------------------------------------
if st.button("✨ Generate Story Weave"):
    if not story_title or not description:
        st.warning("Please provide story title and description.")
    else:
        with st.spinner("Generating story..."):
            st.session_state.story = generate_story(story_title, genre, description)

        with st.spinner("Generating image aligned with story..."):
            st.session_state.image = generate_image(st.session_state.story)

# ---------------- DISPLAY ----------------
if st.session_state.story:
    st.subheader("📜 Generated Story")
    st.write(st.session_state.story)

if "image" in st.session_state and st.session_state.image:
    st.subheader("🖼 Story Illustration")
    st.image(st.session_state.image, use_column_width=True)

if st.session_state.story:
    if st.button("🔊 Read Aloud Story"):
        with st.spinner("Generating voice narration..."):
            audio_file = generate_audio(st.session_state.story)
        st.audio(audio_file)

# --------------------------------------------------
# FOOTER
# --------------------------------------------------
st.markdown("---")
st.caption("Story Weave • AI-powered Multimodal Storytelling")
