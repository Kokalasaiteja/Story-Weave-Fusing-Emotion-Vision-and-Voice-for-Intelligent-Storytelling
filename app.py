import streamlit as st
import requests
from gtts import gTTS
import google.generativeai as genai
from PIL import Image
from io import BytesIO
import urllib.parse

# --------------------------------------------------
# SESSION STATE INIT (VERY IMPORTANT)
# --------------------------------------------------
if "story" not in st.session_state:
    st.session_state.story = ""

if "image" not in st.session_state:
    st.session_state.image = None

# --------------------------------------------------
# CONFIGURATION & SECRETS
# --------------------------------------------------
st.set_page_config(page_title="Story Weave", layout="centered")

GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=GEMINI_API_KEY)

# --------------------------------------------------
# UI
# --------------------------------------------------
st.title("📖 Story Weave")
st.caption("Fusing Emotion, Vision & Voice for Intelligent Storytelling")

story_title = st.text_input("Story Title")
genre = st.selectbox(
    "Genre",
    ["Fantasy", "Science", "Education", "Mythology", "Sci-Fi", "Drama"]
)
description = st.text_area("Story Description / Concept")

# --------------------------------------------------
# STORY GENERATION (GEMINI 2.5)
# --------------------------------------------------
def generate_story(title, genre, description):
    model = genai.GenerativeModel("gemini-2.5-flash")

    prompt = f"""
    Write a short, engaging story in THREE sections.

    Format EXACTLY as:
    Introduction:
    (4–5 lines)

    Story:
    (8–10 lines)

    Conclusion:
    (3–4 lines)

    Title: {title}
    Genre: {genre}
    Concept: {description}

    Keep under 250 words.
    """

    response = model.generate_content(prompt)
    return response.text.strip()

# --------------------------------------------------
# VISUAL PROMPT GENERATION (KEY FIX 🔥)
# --------------------------------------------------
def generate_visual_prompt(story_text, title, genre):
    model = genai.GenerativeModel("gemini-2.5-flash")

    prompt = f"""
    Extract ONE cinematic visual scene from the story.

    Rules:
    - Describe only visible elements
    - Mention characters, environment, action
    - No narration or emotions
    - No camera terms
    - Max 50 words

    Genre: {genre}
    Title: {title}

    Story:
    {story_text}
    """

    response = model.generate_content(prompt)
    return response.text.strip()

# --------------------------------------------------
# IMAGE GENERATION (FREE + STABLE)
# --------------------------------------------------
def generate_image(story_text, title, genre):
    # Extract only the core scene
    try:
        story_part = story_text.split("Story:")[1][:200]
    except:
        story_part = story_text[:200]

    prompt = (
        "Ultra-realistic African lions, natural anatomy, "
        "real lion mane, muscular body, realistic fur texture, "
        "walking on cracked dry savanna ground, "
        "cinematic lighting, wildlife photography style, "
        "National Geographic, 8k detail. "
        f"Scene context: {story_part}"
    )

    negative_prompt = (
        "fantasy creature, mythical animal, cartoon, cgi, monster, "
        "human-like face, extra limbs, distorted anatomy, blurry"
    )

    encoded_prompt = urllib.parse.quote(prompt + " --no " + negative_prompt)

    image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}"

    response = requests.get(image_url, timeout=60)

    if response.status_code != 200:
        st.error("❌ Image generation failed.")
        return None

    return Image.open(BytesIO(response.content))

# --------------------------------------------------
# AUDIO GENERATION
# --------------------------------------------------
def generate_audio(text):
    tts = gTTS(text)
    audio_path = "story_audio.mp3"
    tts.save(audio_path)
    return audio_path

# --------------------------------------------------
# MAIN PIPELINE
# --------------------------------------------------
if st.button("✨ Generate Story Weave"):
    if not story_title or not description:
        st.warning("Please provide story title and description.")
    else:
        with st.spinner("Generating story..."):
            st.session_state.story = generate_story(
                story_title, genre, description
            )

        with st.spinner("Creating illustration..."):
            st.session_state.image = generate_image(
                st.session_state.story,
                story_title,
                genre
            )

# --------------------------------------------------
# DISPLAY
# --------------------------------------------------
if st.session_state.story:
    st.subheader("📜 Generated Story")
    st.write(st.session_state.story)

if st.session_state.image:
    st.subheader("🖼 Generated Image")
    st.image(
    st.session_state.image,
    caption=story_title,
    width=400
)

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
st.caption("Developed by Kokala Sai Teja")
