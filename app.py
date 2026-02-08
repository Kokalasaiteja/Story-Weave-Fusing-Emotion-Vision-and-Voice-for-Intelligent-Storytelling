import streamlit as st
import requests
import os
from gtts import gTTS
import google.generativeai as genai
from PIL import Image
from io import BytesIO

# --------------------------------------------------
# 1. CONFIGURATION & SECRETS
# --------------------------------------------------
st.set_page_config(page_title="Story Weave", layout="centered")

GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
HF_TOKEN = st.secrets["HF_TOKEN"]

genai.configure(api_key=GEMINI_API_KEY)

HF_IMAGE_MODEL = "stabilityai/stable-diffusion-xl-base-1.0"
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
    model = genai.GenerativeModel("models/gemini-1.5-flash")
    prompt = f"""
    Create a vivid, engaging story with characters.
    Title: {title}
    Genre: {genre}
    Concept: {description}

    The story should be imaginative, coherent, and emotionally engaging.
    """
    response = model.generate_content(prompt)
    return response.text.strip()

# --------------------------------------------------
# 4. IMAGE GENERATION (HF INFERENCE API)
# --------------------------------------------------
def generate_image(story_text):
    image_prompt = (
        "Illustration scene from this story: "
        + story_text[:700] +
        ". cinematic, highly detailed, digital art, realistic lighting"
    )

    payload = {"inputs": image_prompt}
    response = requests.post(HF_API_URL, headers=HF_HEADERS, json=payload)

    if response.status_code != 200:
        st.error("Image generation failed.")
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
            story = generate_story(story_title, genre, description)

        st.subheader("📜 Generated Story")
        st.write(story)

        with st.spinner("Generating image aligned with story..."):
            image = generate_image(story)

        if image:
            st.subheader("🖼 Story Illustration")
            st.image(image, use_column_width=True)

        if st.button("🔊 Read Aloud Story"):
            with st.spinner("Generating voice narration..."):
                audio_file = generate_audio(story)
            st.audio(audio_file)

# --------------------------------------------------
# FOOTER
# --------------------------------------------------
st.markdown("---")
st.caption("Story Weave • AI-powered Multimodal Storytelling")
