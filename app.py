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
# SESSION STATE INIT
# --------------------------------------------------
if "story" not in st.session_state:
    st.session_state.story = ""

if "image" not in st.session_state:
    st.session_state.image = None

# --------------------------------------------------
# CONFIGURATION & SECRETS
# --------------------------------------------------
GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=GEMINI_API_KEY)

# Create model ONCE (best practice)
model = genai.GenerativeModel("gemini-2.5-flash")

# --------------------------------------------------
# UI
# --------------------------------------------------
st.title("📖 Story Weave")
st.caption("Fusing Emotion, Vision & Voice for Intelligent Storytelling")

story_title = st.text_input("Story Title", placeholder="A Wanted Man")

genre = st.selectbox(
    "Genre",
    ["Fantasy", "Science", "Education", "Mythology", "Sci-Fi", "Drama"]
)

description = st.text_area(
    "Story Description / Concept",
    placeholder=(
        "A troubled man becomes a wanted criminal after a tragic past love "
        "and life events slowly break his mental balance."
    )
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
- No graphic violence
- No disturbing descriptions
- Emotional but gentle tone

FORMAT EXACTLY AS:

Title:
{title}

Genre:
{genre}

Concept:
Rewrite the concept below clearly with correct grammar and better clarity.

Original Concept:
{description}

Characters:
(List main characters with 1-line description each)

Introduction:
(4–5 lines)

Story:
(8–10 lines)

Conclusion:
(3–4 lines)

Keep the entire story under 250 words.
"""
    response = model.generate_content(prompt)
    return response.text.strip()

# --------------------------------------------------
# VISUAL PROMPT GENERATION
# --------------------------------------------------
def generate_visual_prompt(story_text, title, genre):
    prompt = f"""
Extract ONE clear visual scene from the story.

Rules:
- Describe only visible elements
- Characters, clothing, environment, action
- No emotions
- No camera or lighting terms
- Max 50 words

Story:
{story_text}
"""
    response = model.generate_content(prompt)
    return response.text.strip()

# --------------------------------------------------
# IMAGE GENERATION
# --------------------------------------------------
def generate_image(story_text, title, genre, description):
    visual_scene = generate_visual_prompt(story_text, title, genre)

    # Fallback protection
    if not visual_scene or len(visual_scene) < 20:
        visual_scene = f"{title}, {genre}, {description}"

    # Genre-aware style hint (not forced)
    style_hint = {
        "Drama": "realistic cinematic style",
        "Fantasy": "illustrated fantasy style",
        "Sci-Fi": "cinematic sci-fi or futuristic style",
        "Mythology": "mythological illustration",
        "Education": "clear realistic illustration",
        "Science": "scientific realistic visualization"
    }.get(genre, "best suitable style")

    prompt = f"""
High quality detailed image.
Clear anatomy and correct proportions.
No blur.

Scene:
{visual_scene}

Style:
{style_hint},
cartoon, anime, cgi, or illustration allowed if suitable,
sharp focus,
clean edges,
balanced composition,
accurate anatomy,
consistent character appearance
"""

    negative_prompt = """
blurry, pixelated, low resolution,
distorted anatomy, deformed body,
extra limbs, extra fingers,
missing limbs, broken face,
melted features, unnatural proportions
"""

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
    file_hash = hashlib.md5(text.encode()).hexdigest()
    audio_path = f"story_audio_{file_hash}.mp3"
    tts = gTTS(text)
    tts.save(audio_path)
    return audio_path

# --------------------------------------------------
# MAIN PIPELINE
# --------------------------------------------------
if st.button("✨ Generate Story Weave"):
    if not story_title or not description:
        st.warning("Please provide story title and concept.")
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
    st.image(
        st.session_state.image,
        caption=story_title,
        width=420
    )

if st.session_state.story:
    if st.button("🔊 Read Aloud Story"):
        with st.spinner("Generating narration..."):
            audio_file = generate_audio(st.session_state.story)
        st.audio(audio_file)

# --------------------------------------------------
# FOOTER
# --------------------------------------------------
st.markdown("---")
st.caption("Story Weave • AI-powered Multimodal Storytelling")
st.caption("Developed by Kokala Sai Teja")
