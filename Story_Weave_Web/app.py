import streamlit as st
import requests
from gtts import gTTS
from PIL import Image
from io import BytesIO
import urllib.parse
import hashlib
import json
import time
import os
import base64
from pathlib import Path
import streamlit.components.v1 as components

# --------------------------------------------------
# PATH CONFIG
# --------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent
MEDIA_DIR = BASE_DIR / "media"
STATIC_DIR = BASE_DIR / "static"
DATA_DIR = BASE_DIR / "data"

MEDIA_DIR.mkdir(parents=True, exist_ok=True)
STATIC_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR.mkdir(parents=True, exist_ok=True)

FAVICON_PATH = STATIC_DIR / "favicon.png"
LOGO_PATH = STATIC_DIR / "logo.png"
STORIES_FILE = DATA_DIR / "saved_stories.json"

# --------------------------------------------------
# CUSTOM VECTOR DAY / NIGHT SWITCH ART (EXACT MATCH WITH MOBILE DAYNIGHTSWITCH)
# --------------------------------------------------
DAY_SWITCH_SVG = """<svg xmlns="http://www.w3.org/2000/svg" width="68" height="36" viewBox="0 0 68 36">
  <defs>
    <linearGradient id="dayBg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#42B3F0"/>
      <stop offset="100%" stop-color="#76CEFB"/>
    </linearGradient>
    <linearGradient id="sunGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#FFD56B"/>
      <stop offset="100%" stop-color="#FFA200"/>
    </linearGradient>
  </defs>
  <rect width="68" height="36" rx="18" fill="url(#dayBg)" stroke="rgba(255,255,255,0.6)" stroke-width="1.5"/>
  <!-- Layered White Clouds on Left -->
  <circle cx="13" cy="27" r="8" fill="rgba(255,255,255,0.45)"/>
  <circle cx="23" cy="26" r="10" fill="rgba(255,255,255,0.45)"/>
  <circle cx="10" cy="29" r="7" fill="rgba(255,255,255,0.92)"/>
  <circle cx="19" cy="26" r="9" fill="rgba(255,255,255,0.92)"/>
  <circle cx="29" cy="30" r="6" fill="rgba(255,255,255,0.92)"/>
  <!-- Sun Concentric Halo Rings -->
  <circle cx="49" cy="18" r="19" fill="rgba(255,255,255,0.12)"/>
  <circle cx="49" cy="18" r="15" fill="rgba(255,255,255,0.18)"/>
  <!-- Sun Drop Shadow -->
  <circle cx="49" cy="19.5" r="12.5" fill="rgba(0,0,0,0.18)"/>
  <!-- Golden Sun Sphere -->
  <circle cx="49" cy="18" r="12.5" fill="url(#sunGrad)"/>
</svg>"""

NIGHT_SWITCH_SVG = """<svg xmlns="http://www.w3.org/2000/svg" width="68" height="36" viewBox="0 0 68 36">
  <defs>
    <linearGradient id="nightBg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#1B2338"/>
      <stop offset="100%" stop-color="#0F1424"/>
    </linearGradient>
    <linearGradient id="moonGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#F1F5F9"/>
      <stop offset="100%" stop-color="#CBD5E1"/>
    </linearGradient>
  </defs>
  <rect width="68" height="36" rx="18" fill="url(#nightBg)" stroke="rgba(0,229,255,0.55)" stroke-width="1.5"/>
  <!-- Twinkling 4-Point Stars on Right -->
  <path d="M48 8 Q48 10.5 45.5 10.5 Q48 10.5 48 13 Q48 10.5 50.5 10.5 Q48 10.5 48 8 Z" fill="#FFFFFF"/>
  <path d="M57 20 Q57 22 55 22 Q57 22 57 24 Q57 22 59 22 Q57 22 57 20 Z" fill="#FFFFFF"/>
  <path d="M41 23 Q41 24.5 39.5 24.5 Q41 24.5 41 26 Q41 24.5 42.5 24.5 Q41 24.5 41 23 Z" fill="#FFE599"/>
  <!-- Tiny Sparkle Dots -->
  <circle cx="56" cy="9" r="1" fill="#FFFFFF"/>
  <circle cx="43" cy="13" r="1" fill="#FFFFFF"/>
  <circle cx="51" cy="28" r="0.9" fill="#FFFFFF"/>
  <!-- Moon Drop Shadow -->
  <circle cx="19" cy="19.5" r="12.5" fill="rgba(0,0,0,0.35)"/>
  <!-- Silvery Moon Sphere -->
  <circle cx="19" cy="18" r="12.5" fill="url(#moonGrad)"/>
  <!-- Lunar Craters -->
  <circle cx="15.5" cy="15" r="2.7" fill="rgba(148,163,184,0.55)"/>
  <circle cx="21.5" cy="20.5" r="3.3" fill="rgba(148,163,184,0.55)"/>
  <circle cx="17" cy="22" r="2" fill="rgba(148,163,184,0.55)"/>
</svg>"""

DAY_SWITCH_B64 = f"data:image/svg+xml;base64,{base64.b64encode(DAY_SWITCH_SVG.strip().encode('utf-8')).decode('utf-8')}"
NIGHT_SWITCH_B64 = f"data:image/svg+xml;base64,{base64.b64encode(NIGHT_SWITCH_SVG.strip().encode('utf-8')).decode('utf-8')}"

# --------------------------------------------------
# PERSISTENT STORIES STORAGE (JSON DATABASE)
# --------------------------------------------------
DEFAULT_STORIES = [
    {
        "id": "story_rbc_wbc",
        "title": "RBC and WBC: Defenders of the Pulse",
        "genre": "Science",
        "concept": "Explain how red and white blood cells protect the human body in an engaging story.",
        "story": """Title:
RBC and WBC: Defenders of the Pulse

Genre:
Science

Concept:
How red and white blood cells protect the human body with courage and harmony.

Characters:
1. Ruby: A swift crimson voyager transporting life-giving oxygen.
2. Warren: A brave immune sentinel shielding the bloodstream.

Introduction:
Deep within the warm rivers of the human bloodstream, billions of tiny sentinels journeyed without pause. Among them, Ruby spun gracefully through the glowing arteries.

Story:
With each heartbeat, Ruby carried her golden cargo of oxygen to thirsty tissue cells. Suddenly, an alarm echoed across the vascular banks—dust microbes had slipped through a surface scratch! Ruby paused in alarm, but Warren stepped forward with calm resolve, expanding his luminous white pseudopods. With steady courage, Warren engulfed the invaders, neutralizing the threat into harmless mist. Ruby smiled warmly, delivering healing oxygen to repair the boundary. Together, hand in hand, the red voyager and white defender kept the rhythm of life beating strong.

Conclusion:
United by duty and harmony, the microscopic heroes returned to their ceaseless patrol, proud protectors of the human pulse.""",
        "visual_prompt": "Cinematic digital painting of a glowing red blood cell and white blood cell defender floating in bioluminescent fluid, 8k resolution, volumetric lighting.",
        "image_url": "https://image.pollinations.ai/prompt/Cinematic%20digital%20painting%20of%20a%20glowing%20red%20blood%20cell%20and%20white%20blood%20cell%20defender%20bioluminescent%208k?width=512&height=512&seed=42",
        "created_at": "2026-10-21 17:30"
    },
    {
        "id": "story_clockwork",
        "title": "The Clockwork Forest",
        "genre": "Fantasy",
        "concept": "A young tinkerer discovers trees made of brass and amber that chime in the morning breeze.",
        "story": """Title:
The Clockwork Forest

Genre:
Fantasy

Concept:
A harmony between mechanical artistry and living ancient nature.

Characters:
1. Lyra: An inventive apprentice with a golden pocket wrench.
2. Gideon: A gentle amber-eyed brass owl who reads the winds.

Introduction:
At the edge of the Whispering Ridge, the leaves did not rustle; they chimed. Lyra held her breath as she stepped beneath the brass boughs of the Clockwork Forest.

Story:
Every branch was spun from polished bronze and warm copper, linked by smooth emerald gears that turned in rhythm with the subterranean waterfalls. High on a silver willow, Gideon the owl clicked his beak and fluttered down. 'The sunspring is overwound,' Gideon hooted with melodic resonance. Lyra stepped forward, spotting a trapped crystal pebble between the master gear teeth. Gently aligning her golden wrench, she eased the gear into free rotation. A luminous beam of sunlight struck the grove, setting thousands of brass leaves chiming in joyous symphony.

Conclusion:
With gears spinning in peaceful balance, Lyra knew that magic and machinery could live as one heart.""",
        "visual_prompt": "Enchanted forest with brass and copper mechanical trees, glowing amber leaves, clockwork owl, cinematic 8k render, soft ethereal lighting.",
        "image_url": "https://image.pollinations.ai/prompt/Enchanted%20forest%20with%20brass%20mechanical%20trees%20glowing%20amber%20leaves%20clockwork%20owl%20cinematic%208k?width=512&height=512&seed=88",
        "created_at": "2026-10-21 17:32"
    }
]

def load_saved_stories():
    if not STORIES_FILE.exists():
        save_all_stories(DEFAULT_STORIES)
        return DEFAULT_STORIES
    try:
        with open(STORIES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return DEFAULT_STORIES

def save_all_stories(stories_list):
    try:
        with open(STORIES_FILE, "w", encoding="utf-8") as f:
            json.dump(stories_list, f, indent=2)
    except Exception:
        pass

def add_saved_story(story_dict):
    stories = load_saved_stories()
    stories = [s for s in stories if s.get("id") != story_dict.get("id")]
    stories.insert(0, story_dict)
    save_all_stories(stories)

def delete_saved_story(story_id):
    stories = load_saved_stories()
    stories = [s for s in stories if s.get("id") != story_id]
    save_all_stories(stories)

def delete_saved_stories(story_ids):
    stories = load_saved_stories()
    ids_set = set(story_ids)
    stories = [s for s in stories if s.get("id") not in ids_set]
    save_all_stories(stories)

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------
st.set_page_config(
    page_title="Story Weave • AI Storytelling",
    page_icon=str(FAVICON_PATH) if FAVICON_PATH.exists() else "📖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --------------------------------------------------
# SESSION STATE INITIALIZATION
# --------------------------------------------------
if "theme" not in st.session_state:
    st.session_state.theme = "dark"
if "current_nav" not in st.session_state:
    st.session_state.current_nav = "Weave"
if "story" not in st.session_state:
    st.session_state.story = ""
if "image" not in st.session_state:
    st.session_state.image = None
if "visual_prompt" not in st.session_state:
    st.session_state.visual_prompt = ""
if "audio_path" not in st.session_state:
    st.session_state.audio_path = None
if "current_title" not in st.session_state:
    st.session_state.current_title = ""
if "current_desc" not in st.session_state:
    st.session_state.current_desc = ""
if "selected_story_ids" not in st.session_state:
    st.session_state.selected_story_ids = set()

# --------------------------------------------------
# SECRETS / GEMINI CONFIG
# --------------------------------------------------
gemini_key = None
try:
    if hasattr(st, "secrets") and "GEMINI_API_KEY" in st.secrets:
        gemini_key = st.secrets["GEMINI_API_KEY"]
except Exception:
    pass

if not gemini_key:
    gemini_key = os.environ.get("GEMINI_API_KEY")

try:
    import google.generativeai as genai
    from google.api_core.exceptions import ResourceExhausted
    HAVE_GEMINI_LIB = True
except ImportError:
    HAVE_GEMINI_LIB = False

# --------------------------------------------------
# DYNAMIC THEME STYLING (DARK & LIGHT MODE)
# --------------------------------------------------
is_dark = st.session_state.theme == "dark"

bg_gradient = "radial-gradient(circle at 50% 0%, #161D31 0%, #080B12 60%, #04060A 100%)" if is_dark else "linear-gradient(180deg, #F8FAFC 0%, #EFF6FF 100%)"
text_color = "#E2E8F0" if is_dark else "#0F172A"
card_bg = "rgba(18, 24, 40, 0.75)" if is_dark else "rgba(255, 255, 255, 0.95)"
card_border = "rgba(0, 229, 255, 0.25)" if is_dark else "rgba(2, 132, 199, 0.25)"
card_shadow = "0 10px 30px rgba(0, 0, 0, 0.45)" if is_dark else "0 10px 25px rgba(15, 23, 42, 0.08)"
input_bg = "rgba(14, 20, 34, 0.9)" if is_dark else "#FFFFFF"
input_text = "#F8FAFC" if is_dark else "#0F172A"
input_border = "rgba(255, 255, 255, 0.16)" if is_dark else "#CBD5E1"
active_key_suffix = {"Weave": "weave", "Library": "lib", "About": "abt"}.get(st.session_state.get("current_nav", "Weave"), "weave")

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=Space+Grotesk:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"], .stApp {{
    font-family: 'Outfit', -apple-system, BlinkMacSystemFont, sans-serif !important;
}}

/* Full app container background & text with smooth 1s transition */
.stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"], .main {{
    background: {bg_gradient} !important;
    color: {text_color} !important;
    transition: background 1.0s ease, color 1.0s ease !important;
}}

/* All text typography */
.stApp p, .stApp span, .stApp label, .stApp div, .stApp h1, .stApp h2, .stApp h3, .stApp h4 {{
    color: {text_color};
}}

/* Fix Image 2: Perfectly Centered Hamburger Icon */
[data-testid="stExpandSidebarButton"] {{
    background: {'rgba(18, 24, 40, 0.95)' if is_dark else '#FFFFFF'} !important;
    border: 2px solid {'#00E5FF' if is_dark else '#0284C7'} !important;
    border-radius: 14px !important;
    width: 46px !important;
    height: 46px !important;
    min-width: 46px !important;
    min-height: 46px !important;
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
    box-shadow: {'0 4px 16px rgba(0, 229, 255, 0.4)' if is_dark else '0 4px 14px rgba(2, 132, 199, 0.25)'} !important;
    transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1) !important;
    cursor: pointer !important;
    position: relative !important;
    padding: 0 !important;
    margin: 0 !important;
    overflow: hidden !important;
}}

[data-testid="stExpandSidebarButton"]:hover {{
    transform: scale(1.1) rotate(3deg) !important;
    box-shadow: {'0 6px 24px rgba(0, 229, 255, 0.6), 0 0 12px rgba(213, 0, 249, 0.45)' if is_dark else '0 6px 20px rgba(2, 132, 199, 0.45)'} !important;
    border-color: {'#D500F9' if is_dark else '#9333EA'} !important;
}}

/* Hide all default child spans/icons in expand button */
[data-testid="stExpandSidebarButton"] * {{
    display: none !important;
}}

/* Centered 3 Rounded Multi-color Glowing Bars for Hamburger */
[data-testid="stExpandSidebarButton"]::before {{
    content: "" !important;
    display: block !important;
    width: 22px !important;
    height: 3.5px !important;
    border-radius: 4px !important;
    background: linear-gradient(90deg, #00E5FF, #D500F9) !important;
    box-shadow: 0 7px 0 {'#FFD600' if is_dark else '#F59E0B'}, 0 14px 0 {'#00E5FF' if is_dark else '#0284C7'} !important;
    transform: translateY(-7px) !important;
    margin: 0 auto !important;
}}

/* Fix Image 1: Clean Single Centered Close "X" without double rendering or border clipping */
div[data-testid="stSidebarCollapseButton"] {{
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    padding: 0 !important;
    margin: 0 !important;
}}

div[data-testid="stSidebarCollapseButton"]::before {{
    display: none !important;
    content: "" !important;
}}

div[data-testid="stSidebarCollapseButton"] button {{
    background: {'rgba(18, 24, 40, 0.95)' if is_dark else '#FFFFFF'} !important;
    border: 2px solid {'#D500F9' if is_dark else '#9333EA'} !important;
    border-radius: 14px !important;
    width: 42px !important;
    height: 42px !important;
    min-width: 42px !important;
    min-height: 42px !important;
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
    box-shadow: {'0 4px 16px rgba(213, 0, 249, 0.4)' if is_dark else '0 4px 14px rgba(147, 51, 234, 0.25)'} !important;
    transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1) !important;
    cursor: pointer !important;
    padding: 0 !important;
    position: relative !important;
    overflow: hidden !important;
}}

div[data-testid="stSidebarCollapseButton"] button:hover {{
    transform: scale(1.1) rotate(-90deg) !important;
    border-color: {'#00E5FF' if is_dark else '#0284C7'} !important;
    box-shadow: {'0 6px 24px rgba(213, 0, 249, 0.6)' if is_dark else '0 6px 20px rgba(147, 51, 234, 0.45)'} !important;
}}

div[data-testid="stSidebarCollapseButton"] button * {{
    display: none !important;
}}

div[data-testid="stSidebarCollapseButton"] button::before {{
    content: "✕" !important;
    font-family: 'Space Grotesk', -apple-system, sans-serif !important;
    font-size: 20px !important;
    font-weight: 900 !important;
    background: linear-gradient(135deg, {'#D500F9, #00E5FF' if is_dark else '#9333EA, #0284C7'}) !important;
    -webkit-background-clip: text !important;
    -webkit-text-fill-color: transparent !important;
    line-height: 1 !important;
    margin: 0 !important;
}}

/* (Theme toggle button styled below after secondary buttons) */

/* Brand Titles */
.brand-title {{
    font-family: 'Space Grotesk', sans-serif;
    font-size: 2.2rem;
    font-weight: 800;
    background: linear-gradient(135deg, {'#00E5FF 0%, #D500F9 100%' if is_dark else '#0284C7 0%, #9333EA 100%'});
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 0;
    line-height: 1.2;
}}

.brand-subtitle {{
    color: {'#94A3B8' if is_dark else '#64748B'};
    font-size: 0.95rem;
    font-weight: 400;
    margin-top: 4px;
}}

/* Light & Dark Mode Input & Select Styling - Robust White Background in Light Mode */
div[data-testid="stSelectbox"],
div[data-testid="stSelectbox"] > div:first-child,
div[data-baseweb="select"] {{
    border: none !important;
    background: transparent !important;
    box-shadow: none !important;
}}

/* Text Input and Text Area Container & Border Styling: Flawless Rounded Corners Touching Seamlessly */
div[data-testid="stTextInputRootElement"],
div[data-testid="stTextInputRootElement"] > div,
div[data-testid="stTextAreaRootElement"],
div[data-testid="stTextAreaRootElement"] > div,
div[data-testid="stSelectbox"] > div,
div[data-testid="stSelectbox"] > div > div,
div[data-baseweb="input"],
div[data-baseweb="base-input"],
div[data-baseweb="textarea"],
div[data-baseweb="select"],
div[data-baseweb="select"] > div {{
    background: {input_bg} !important;
    background-color: {input_bg} !important;
    border: 1px solid {input_border} !important;
    border-radius: 12px !important;
    overflow: hidden !important;
    box-shadow: none !important;
    transition: border-color 0.25s ease, box-shadow 0.25s ease !important;
}}

div[data-testid="stTextInputRootElement"]:focus-within,
div[data-testid="stTextInputRootElement"] > div:focus-within,
div[data-testid="stTextAreaRootElement"]:focus-within,
div[data-testid="stTextAreaRootElement"] > div:focus-within,
div[data-testid="stSelectbox"] > div > div:focus-within,
div[data-baseweb="input"]:focus-within,
div[data-baseweb="textarea"]:focus-within,
div[data-baseweb="select"] > div:focus-within,
div[data-baseweb="select"] > div[aria-expanded="true"] {{
    border: 1.5px solid {'#00E5FF' if is_dark else '#0284C7'} !important;
    box-shadow: 0 0 14px {'rgba(0, 229, 255, 0.45)' if is_dark else 'rgba(2, 132, 199, 0.35)'} !important;
}}

/* Ensure inner input/textarea has no rogue borders, no corner gap, matches rounded container */
div[data-testid="stTextInputRootElement"] input,
div[data-testid="stTextAreaRootElement"] textarea,
div[data-baseweb="textarea"] textarea,
.stTextInput input,
.stTextArea textarea {{
    border: none !important;
    outline: none !important;
    box-shadow: none !important;
    border-radius: 12px !important;
    background: transparent !important;
    background-color: transparent !important;
    color: {input_text} !important;
    -webkit-text-fill-color: {input_text} !important;
    padding: 10px 14px !important;
    resize: none !important;
    overflow: auto !important;
}}

input,
textarea,
div[data-baseweb="input"] input,
div[data-baseweb="textarea"] textarea,
textarea[data-testid="stTextArea"] {{
    font-family: 'Outfit', sans-serif !important;
    font-size: 1rem !important;
}}

/* Form Labels: Bold and clearly spaced */
div[data-testid="stTextInput"] label,
div[data-testid="stTextInput"] label p,
div[data-testid="stSelectbox"] label,
div[data-testid="stSelectbox"] label p,
div[data-testid="stTextArea"] label,
div[data-testid="stTextArea"] label p {{
    font-weight: 700 !important;
    font-size: 1.02rem !important;
    letter-spacing: 0.25px !important;
    color: {text_color} !important;
    margin-bottom: 6px !important;
}}

/* Ensure Genre Selectbox value ('Science', etc.) is clearly visible in Light and Dark Mode */
div[data-baseweb="select"],
div[data-baseweb="select"] *,
div[data-baseweb="select"] span,
div[data-baseweb="select"] div,
div[data-testid="stSelectbox"] div,
div[data-testid="stSelectbox"] span,
div[data-baseweb="select"] [aria-selected="true"] {{
    font-family: 'Outfit', sans-serif !important;
    font-size: 1rem !important;
    color: {input_text} !important;
    -webkit-text-fill-color: {input_text} !important;
    font-weight: 500 !important;
}}

div[data-baseweb="select"] svg {{
    fill: {'#94A3B8' if is_dark else '#334155'} !important;
    color: {'#94A3B8' if is_dark else '#334155'} !important;
}}

/* Selectbox Dropdown Menu Options (BaseWeb Popover, Listbox, Option Items) */
div[data-baseweb="popover"],
div[data-baseweb="popover"] > div,
div[data-baseweb="popover"] ul,
div[data-baseweb="popover"] li,
div[data-baseweb="popover"] [role="listbox"],
div[data-baseweb="popover"] [role="option"],
div[data-baseweb="popover"] div,
div[data-baseweb="popover"] span,
div[data-baseweb="menu"],
li[data-baseweb="menu-item"],
ul[role="listbox"],
ul[role="listbox"] *,
li[role="option"],
li[role="option"] *,
div[data-testid="stSelectboxVirtualDropdown"],
div[data-testid="stSelectboxVirtualDropdown"] * {{
    background: {'#0E1422' if is_dark else '#FFFFFF'} !important;
    background-color: {'#0E1422' if is_dark else '#FFFFFF'} !important;
    color: {'#F8FAFC' if is_dark else '#0F172A'} !important;
    -webkit-text-fill-color: {'#F8FAFC' if is_dark else '#0F172A'} !important;
}}

/* Option Item Hover / Highlighted / Selected State */
li[role="option"]:hover,
li[role="option"]:hover *,
li[role="option"][aria-selected="true"],
li[role="option"][aria-selected="true"] *,
li[role="option"][data-highlighted="true"],
li[role="option"][data-highlighted="true"] *,
ul[role="listbox"] li:hover,
ul[role="listbox"] li:hover * {{
    background: {'rgba(0, 229, 255, 0.22)' if is_dark else '#E0F2FE'} !important;
    background-color: {'rgba(0, 229, 255, 0.22)' if is_dark else '#E0F2FE'} !important;
    color: {'#00E5FF' if is_dark else '#0284C7'} !important;
    -webkit-text-fill-color: {'#00E5FF' if is_dark else '#0284C7'} !important;
    font-weight: 700 !important;
}}

input::placeholder,
textarea::placeholder {{
    color: {'#64748B' if is_dark else '#94A3B8'} !important;
    -webkit-text-fill-color: {'#64748B' if is_dark else '#94A3B8'} !important;
}}

/* Fix Image 4: Transparent Background for Inline Code Tags in Light Mode */
code,
.stMarkdown code,
[data-testid="stMarkdownContainer"] code,
div[data-testid="stMarkdownContainer"] pre code {{
    background: transparent !important;
    background-color: transparent !important;
    color: {'#00E5FF' if is_dark else '#0284C7'} !important;
    font-weight: 600 !important;
    font-family: 'Space Grotesk', monospace !important;
    border: 1px solid {'rgba(0, 229, 255, 0.3)' if is_dark else 'rgba(2, 132, 199, 0.3)'} !important;
    border-radius: 6px !important;
    padding: 2px 6px !important;
}}

/* Top Navigation Bar Pill Buttons with High Contrast & Hover Bounce */
div[data-testid="stHorizontalBlock"] div.stButton > button {{
    padding: 8px 14px !important;
    font-size: 0.95rem !important;
    font-weight: 700 !important;
    border-radius: 14px !important;
    white-space: nowrap !important;
    transition: all 0.25s cubic-bezier(0.34, 1.56, 0.64, 1) !important;
    letter-spacing: 0.3px !important;
}}

/* Active Nav Pill */
.st-key-btn_top_{active_key_suffix} button {{
    background: {'linear-gradient(135deg, #00E5FF, #D500F9)' if is_dark else 'linear-gradient(135deg, #0284C7, #9333EA)'} !important;
    color: {'#050811' if is_dark else '#FFFFFF'} !important;
    border: none !important;
    font-weight: 800 !important;
    box-shadow: 0 4px 18px {'rgba(0, 229, 255, 0.5)' if is_dark else 'rgba(2, 132, 199, 0.4)'} !important;
    transform: translateY(-2px) scale(1.04) !important;
}}

/* Inactive Nav Pills */
.st-key-btn_top_weave:not(.st-key-btn_top_{active_key_suffix}) button,
.st-key-btn_top_lib:not(.st-key-btn_top_{active_key_suffix}) button,
.st-key-btn_top_abt:not(.st-key-btn_top_{active_key_suffix}) button {{
    background: {'rgba(16, 23, 42, 0.85)' if is_dark else '#FFFFFF'} !important;
    color: {'#E2E8F0' if is_dark else '#1E293B'} !important;
    border: 1.5px solid {'rgba(255, 255, 255, 0.16)' if is_dark else '#CBD5E1'} !important;
    font-weight: 700 !important;
}}

.st-key-btn_top_weave:not(.st-key-btn_top_{active_key_suffix}) button:hover,
.st-key-btn_top_lib:not(.st-key-btn_top_{active_key_suffix}) button:hover,
.st-key-btn_top_abt:not(.st-key-btn_top_{active_key_suffix}) button:hover {{
    color: {'#00E5FF' if is_dark else '#0284C7'} !important;
    border-color: {'#00E5FF' if is_dark else '#0284C7'} !important;
    background: {'rgba(0, 229, 255, 0.12)' if is_dark else '#F0F9FF'} !important;
    transform: translateY(-2px) scale(1.03) !important;
}}

/* Secondary Buttons */
button[data-testid="baseButton-secondary"],
button[kind="secondary"] {{
    background: {'rgba(20, 28, 51, 0.9)' if is_dark else '#FFFFFF'} !important;
    color: {'#FFFFFF' if is_dark else '#0F172A'} !important;
    border: 1.5px solid {'rgba(255, 255, 255, 0.18)' if is_dark else '#CBD5E1'} !important;
    font-weight: 700 !important;
    border-radius: 12px !important;
    transition: all 0.25s ease !important;
}}

button[data-testid="baseButton-secondary"]:hover,
button[kind="secondary"]:hover {{
    color: {'#00E5FF' if is_dark else '#0284C7'} !important;
    border-color: {'#00E5FF' if is_dark else '#0284C7'} !important;
    background: {'rgba(0, 229, 255, 0.12)' if is_dark else '#F0F9FF'} !important;
    transform: translateY(-1px) !important;
}}

/* Select All Button Pill with Background Color */
.st-key-btn_toggle_select_all button {{
    background: {'linear-gradient(135deg, rgba(0, 229, 255, 0.22), rgba(213, 0, 249, 0.22))' if is_dark else 'linear-gradient(135deg, #E0F2FE, #EDE9FE)'} !important;
    border: 1.5px solid {'#00E5FF' if is_dark else '#0284C7'} !important;
    color: {'#00E5FF' if is_dark else '#0369A1'} !important;
    -webkit-text-fill-color: {'#00E5FF' if is_dark else '#0369A1'} !important;
    font-weight: 700 !important;
    border-radius: 12px !important;
    box-shadow: 0 2px 10px {'rgba(0, 229, 255, 0.2)' if is_dark else 'rgba(2, 132, 199, 0.15)'} !important;
    transition: all 0.25s ease !important;
}}
.st-key-btn_toggle_select_all button:hover {{
    transform: translateY(-2px) !important;
    background: {'linear-gradient(135deg, rgba(0, 229, 255, 0.35), rgba(213, 0, 249, 0.35))' if is_dark else 'linear-gradient(135deg, #BAE6FD, #DDD6FE)'} !important;
    box-shadow: 0 4px 16px {'rgba(0, 229, 255, 0.35)' if is_dark else 'rgba(2, 132, 199, 0.25)'} !important;
}}
.st-key-btn_toggle_select_all button * {{
    color: {'#00E5FF' if is_dark else '#0369A1'} !important;
    -webkit-text-fill-color: {'#00E5FF' if is_dark else '#0369A1'} !important;
    font-weight: 700 !important;
}}

/* Delete Selected Button with Background Color */
.st-key-btn_batch_delete button {{
    background: linear-gradient(135deg, #EF4444, #DC2626) !important;
    border: 1.5px solid #EF4444 !important;
    color: #FFFFFF !important;
    -webkit-text-fill-color: #FFFFFF !important;
    font-weight: 700 !important;
    border-radius: 12px !important;
    box-shadow: 0 3px 12px rgba(239, 68, 68, 0.4) !important;
    transition: all 0.25s ease !important;
}}
.st-key-btn_batch_delete button:hover:not(:disabled) {{
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 20px rgba(239, 68, 68, 0.6) !important;
}}
.st-key-btn_batch_delete button:disabled {{
    background: {'rgba(239, 68, 68, 0.15)' if is_dark else 'rgba(239, 68, 68, 0.08)'} !important;
    border: 1.5px solid {'rgba(239, 68, 68, 0.35)' if is_dark else 'rgba(239, 68, 68, 0.2)'} !important;
    color: {'rgba(248, 113, 113, 0.7)' if is_dark else 'rgba(220, 38, 38, 0.6)'} !important;
    -webkit-text-fill-color: {'rgba(248, 113, 113, 0.7)' if is_dark else 'rgba(220, 38, 38, 0.6)'} !important;
    box-shadow: none !important;
    cursor: not-allowed !important;
    opacity: 0.75 !important;
}}
.st-key-btn_batch_delete button * {{
    font-weight: 700 !important;
}}

/* Checkbox Column Alignment with Story Expander Card */
div[data-testid="column"]:has([data-testid="stCheckbox"]) {{
    display: flex !important;
    align-items: flex-start !important;
    justify-content: center !important;
    padding-top: 13px !important;
}}

div[data-testid="stCheckbox"] {{
    margin: 0 !important;
    padding: 0 !important;
    min-height: auto !important;
    line-height: 1 !important;
}}

div[data-testid="stCheckbox"] label {{
    margin: 0 !important;
    padding: 0 !important;
    align-items: center !important;
}}

/* Unselected Checkbox Indicator: Clean Pure White in Light Mode, Sleek Slate in Dark Mode */
div[data-testid="stCheckbox"] label > div:first-of-type,
div[data-testid="stCheckbox"] div[class*="e1ap2qgk5"],
div[data-baseweb="checkbox"] div {{
    background: {'#1E293B' if is_dark else '#FFFFFF'} !important;
    background-color: {'#1E293B' if is_dark else '#FFFFFF'} !important;
    border: 1.8px solid {'rgba(0, 229, 255, 0.5)' if is_dark else '#CBD5E1'} !important;
    border-radius: 6px !important;
    width: 20px !important;
    height: 20px !important;
    box-sizing: border-box !important;
    box-shadow: {'0 2px 6px rgba(0,0,0,0.3)' if is_dark else '0 1px 3px rgba(0,0,0,0.06)'} !important;
    transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
}}

/* Checked state */
div[data-testid="stCheckbox"]:has(input:checked) label > div:first-of-type,
div[data-testid="stCheckbox"]:has(input:checked) div[class*="e1ap2qgk5"],
div[data-baseweb="checkbox"]:has(input:checked) div {{
    background: {'linear-gradient(135deg, #00E5FF, #D500F9)' if is_dark else '#0284C7'} !important;
    background-color: {'#00E5FF' if is_dark else '#0284C7'} !important;
    border-color: {'#00E5FF' if is_dark else '#0284C7'} !important;
    box-shadow: 0 0 10px {'rgba(0, 229, 255, 0.5)' if is_dark else 'rgba(2, 132, 199, 0.35)'} !important;
}}

/* Checkbox Hover */
div[data-testid="stCheckbox"] label:hover > div:first-of-type,
div[data-testid="stCheckbox"] label:hover div[class*="e1ap2qgk5"] {{
    border-color: {'#00E5FF' if is_dark else '#0284C7'} !important;
    box-shadow: 0 0 8px {'rgba(0, 229, 255, 0.45)' if is_dark else 'rgba(2, 132, 199, 0.25)'} !important;
}}

/* Straight Header and Nav Alignment */
div[data-testid="column"]:has(.brand-title) {{
    display: flex !important;
    align-items: center !important;
}}
div[data-testid="column"]:has(.st-key-btn_top_weave) {{
    display: flex !important;
    align-items: center !important;
}}
div[data-testid="column"]:has(.brand-subtitle) {{
    display: flex !important;
    align-items: center !important;
}}
div[data-testid="column"]:has(.st-key-btn_top_theme) {{
    display: flex !important;
    align-items: center !important;
    justify-content: flex-end !important;
}}
.st-key-btn_top_theme {{
    display: flex !important;
    justify-content: flex-end !important;
    width: 100% !important;
}}

/* Custom-Coded Day / Night Switch: Vector Sun & Moon (Exact UI/UX Match with Mobile DayNightSwitch) */
.st-key-btn_side_theme button,
.st-key-btn_side_theme button[data-testid="baseButton-secondary"],
.st-key-btn_side_theme button[kind="secondary"],
.st-key-btn_top_theme button,
.st-key-btn_top_theme button[data-testid="baseButton-secondary"],
.st-key-btn_top_theme button[kind="secondary"] {{
    background: url('{NIGHT_SWITCH_B64 if is_dark else DAY_SWITCH_B64}') center center / contain no-repeat !important;
    background-image: url('{NIGHT_SWITCH_B64 if is_dark else DAY_SWITCH_B64}') !important;
    background-size: 100% 100% !important;
    background-position: center !important;
    background-repeat: no-repeat !important;
    border-radius: 20px !important;
    width: 68px !important;
    height: 36px !important;
    min-height: 36px !important;
    border: none !important;
    box-shadow: 0 4px 14px {'rgba(0, 229, 255, 0.45)' if is_dark else 'rgba(66, 179, 240, 0.45)'} !important;
    color: transparent !important;
    font-size: 0 !important;
    padding: 0 !important;
    cursor: pointer !important;
    transition: transform 1.0s cubic-bezier(0.34, 1.56, 0.64, 1), box-shadow 1.0s ease, background 1.0s ease !important;
}}

.st-key-btn_side_theme button:hover,
.st-key-btn_top_theme button:hover {{
    transform: scale(1.08) !important;
    box-shadow: 0 6px 20px {'rgba(0, 229, 255, 0.65)' if is_dark else 'rgba(66, 179, 240, 0.65)'} !important;
}}

.st-key-btn_side_theme button:active,
.st-key-btn_top_theme button:active {{
    transform: scale(0.95) !important;
}}

.st-key-btn_side_theme button *,
.st-key-btn_top_theme button * {{
    display: none !important;
}}

/* Primary Action Buttons (Generate Story Weave - Bold Pure White Text Like Mobile) */
button[data-testid="baseButton-primary"],
button[kind="primary"],
.st-key-btn_generate_story button {{
    background: linear-gradient(135deg, #00E5FF 0%, #D500F9 100%) !important;
    color: #FFFFFF !important;
    -webkit-text-fill-color: #FFFFFF !important;
    font-family: 'Space Grotesk', sans-serif !important;
    font-weight: 800 !important;
    font-size: 1.05rem !important;
    border: none !important;
    border-radius: 14px !important;
    padding: 12px 24px !important;
    box-shadow: 0 4px 18px rgba(0, 229, 255, 0.45) !important;
    transition: all 0.25s ease !important;
    text-shadow: 0 1px 3px rgba(0, 0, 0, 0.45) !important;
}}

button[data-testid="baseButton-primary"] *,
button[kind="primary"] *,
.st-key-btn_generate_story button * {{
    color: #FFFFFF !important;
    -webkit-text-fill-color: #FFFFFF !important;
    font-weight: 800 !important;
}}

button[data-testid="baseButton-primary"]:hover,
button[kind="primary"]:hover,
.st-key-btn_generate_story button:hover {{
    transform: translateY(-2px) scale(1.02) !important;
    box-shadow: 0 8px 26px rgba(213, 0, 249, 0.65) !important;
    color: #FFFFFF !important;
    -webkit-text-fill-color: #FFFFFF !important;
}}

/* Fix Image 3: Mobile-like Developer Contact Buttons */
.btn-contact-linkedin {{
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 10px;
    background-color: #0077B5 !important;
    color: #FFFFFF !important;
    font-weight: 700 !important;
    font-size: 0.95rem !important;
    padding: 11px 22px !important;
    border-radius: 12px !important;
    text-decoration: none !important;
    box-shadow: 0 4px 14px rgba(0, 119, 181, 0.4) !important;
    transition: all 0.25s ease !important;
}}
.btn-contact-linkedin:hover {{
    background-color: #005F92 !important;
    color: #FFFFFF !important;
    transform: translateY(-2px);
    box-shadow: 0 6px 18px rgba(0, 119, 181, 0.6) !important;
}}

.btn-contact-email {{
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 10px;
    background-color: #EA4335 !important;
    color: #FFFFFF !important;
    font-weight: 700 !important;
    font-size: 0.95rem !important;
    padding: 11px 22px !important;
    border-radius: 12px !important;
    text-decoration: none !important;
    box-shadow: 0 4px 14px rgba(234, 67, 53, 0.4) !important;
    transition: all 0.25s ease !important;
}}
.btn-contact-email:hover {{
    background-color: #C5221F !important;
    color: #FFFFFF !important;
    transform: translateY(-2px);
    box-shadow: 0 6px 18px rgba(234, 67, 53, 0.6) !important;
}}

/* Sidebar Base Styling */
section[data-testid="stSidebar"] {{
    background-color: {'#0A0E18' if is_dark else '#FFFFFF'} !important;
    border-right: 1px solid {card_border} !important;
}}

section[data-testid="stSidebar"] [data-testid="stSidebarUserContent"] {{
    padding-bottom: 55px !important;
}}

section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] span,
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] div,
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3,
section[data-testid="stSidebar"] h4 {{
    color: {text_color} !important;
}}

/* Responsive Sidebar Footer: Moves and Resizes with Sidebar Nav */
.sidebar-fixed-footer {{
    position: relative !important;
    width: 100% !important;
    max-width: 100% !important;
    box-sizing: border-box !important;
    padding: 12px 14px 8px 14px !important;
    margin-top: 14px !important;
    margin-bottom: 0px !important;
    background: {'rgba(255, 255, 255, 0.03)' if is_dark else 'rgba(0, 0, 0, 0.02)'} !important;
    border-top: 1px solid {'rgba(255, 255, 255, 0.08)' if is_dark else 'rgba(0, 0, 0, 0.06)'} !important;
    border-radius: 8px !important;
    text-align: center !important;
    color: {'#94A3B8' if is_dark else '#64748B'} !important;
    box-shadow: none !important;
    overflow: hidden !important;
}}

/* When sidebar is collapsed, minimized, or closed, hide sidebar footer completely */
section[data-testid="stSidebar"][aria-expanded="false"] .sidebar-fixed-footer,
[data-testid="stSidebarCollapsedControl"] ~ section[data-testid="stSidebar"] .sidebar-fixed-footer {{
    display: none !important;
    visibility: hidden !important;
    opacity: 0 !important;
}}

/* Perfectly parallel alignment for Library story item checkbox & expander header */
div[data-testid="column"]:has(div[class*="st-key-chk_story_"]) {{
    display: flex !important;
    align-items: flex-start !important;
    justify-content: center !important;
}}

div[class*="st-key-chk_story_"] {{
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    min-height: 48px !important;
    height: 48px !important;
}}

div[class*="st-key-chk_story_"] div[data-testid="stCheckbox"] {{
    margin: 0 !important;
    padding: 0 !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
}}

div[class*="st-key-chk_story_"] div[data-testid="stCheckbox"] label {{
    margin: 0 !important;
    padding: 0 !important;
    min-height: unset !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
}}

/* Expander Styling in Library: Clean Pure White in Light Mode, Sleek Obsidian in Dark Mode */
div[data-testid="stExpander"] {{
    background: {'rgba(18, 24, 40, 0.85)' if is_dark else '#FFFFFF'} !important;
    background-color: {'rgba(18, 24, 40, 0.85)' if is_dark else '#FFFFFF'} !important;
    border: 1px solid {card_border} !important;
    border-radius: 14px !important;
    box-shadow: {card_shadow} !important;
    overflow: hidden !important;
}}

div[data-testid="stExpander"] details,
div[data-testid="stExpander"] summary,
div[data-testid="stExpander"] details summary,
div[data-testid="stExpander"] details[open] summary,
div[data-testid="stExpander"] details summary:focus,
div[data-testid="stExpander"] details summary:active {{
    background: {'rgba(18, 24, 40, 0.85)' if is_dark else '#FFFFFF'} !important;
    background-color: {'rgba(18, 24, 40, 0.85)' if is_dark else '#FFFFFF'} !important;
    color: {text_color} !important;
    border-radius: 12px !important;
    border: none !important;
}}

div[data-testid="stExpander"] summary:hover,
div[data-testid="stExpander"] details summary:hover {{
    background-color: {'rgba(255, 255, 255, 0.05)' if is_dark else 'rgba(2, 132, 199, 0.06)'} !important;
}}

div[data-testid="stExpander"] summary *,
div[data-testid="stExpander"] details summary *,
div[data-testid="stExpander"] summary p,
div[data-testid="stExpander"] summary span {{
    color: {text_color} !important;
    -webkit-text-fill-color: {text_color} !important;
    font-weight: 600 !important;
}}

div[data-testid="stExpander"] summary svg,
div[data-testid="stExpander"] details summary svg {{
    fill: {'#00E5FF' if is_dark else '#0284C7'} !important;
    color: {'#00E5FF' if is_dark else '#0284C7'} !important;
}}

div[data-testid="stExpander"] div[data-testid="stExpanderDetails"] {{
    background: {'rgba(14, 20, 36, 0.95)' if is_dark else '#FFFFFF'} !important;
    background-color: {'rgba(14, 20, 36, 0.95)' if is_dark else '#FFFFFF'} !important;
    border-top: 1px solid {'rgba(255, 255, 255, 0.06)' if is_dark else 'rgba(0, 0, 0, 0.06)'} !important;
    border-radius: 0 0 14px 14px !important;
}}

/* Main Container & Footer Spacing: Pinned to bottom with zero dead space below footer */
html, body, .stApp, [data-testid="stAppViewContainer"], section[data-testid="stMain"] {{
    min-height: 100vh !important;
}}

[data-testid="stAppViewContainer"] > section.main {{
    display: flex !important;
    flex-direction: column !important;
    min-height: 100vh !important;
    padding-bottom: 0px !important;
    margin-bottom: 0px !important;
}}

.block-container,
[data-testid="stAppViewBlockContainer"],
.main .block-container {{
    padding-top: 2.2rem !important;
    padding-bottom: 16px !important;
    margin-bottom: 0px !important;
    min-height: calc(100vh - 3.5rem) !important;
    display: flex !important;
    flex-direction: column !important;
    flex-grow: 1 !important;
    box-sizing: border-box !important;
}}

/* Ensure parent vertical block expands cleanly so margin-top: auto pushes footer to bottom without cropping */
.block-container > div[data-testid="stVerticalBlock"]:first-child {{
    display: flex !important;
    flex-direction: column !important;
    flex-grow: 1 !important;
    min-height: calc(100vh - 6.5rem) !important;
}}

/* Push footer block to bottom, placing all remaining vertical space ABOVE the APK download section */
div[data-testid="stVerticalBlock"] > div:has(.st-key-footer_block),
div[data-testid="stVerticalBlock"] > div:has(.footer-container),
div[data-testid="stVerticalBlock"] > div:has(#-download-story-weave-android-mobile-app),
.st-key-footer_block,
div[class*="st-key-footer_block"] {{
    margin-top: auto !important;
    margin-bottom: 0px !important;
    padding-bottom: 0px !important;
    width: 100% !important;
}}

div.element-container:has(.footer-container),
div.stMarkdown:has(.footer-container) {{
    margin-bottom: 0px !important;
    overflow: visible !important;
}}

[data-testid="stBottom"],
[data-testid="stBottom"] > div {{
    display: none !important;
    height: 0px !important;
    padding: 0px !important;
    margin: 0px !important;
}}

footer, [data-testid="stFooter"] {{
    display: none !important;
}}

.footer-container {{
    text-align: center;
    width: 100% !important;
    max-width: 100% !important;
    box-sizing: border-box !important;
    padding: 10px 16px 14px 16px !important;
    margin-top: 10px !important;
    margin-bottom: 0px !important;
    border-top: 1px solid {'rgba(255, 255, 255, 0.08)' if is_dark else 'rgba(0, 0, 0, 0.08)'};
    color: {'#94A3B8' if is_dark else '#334155'};
    font-size: 0.92rem;
    overflow: visible !important;
    transition: all 0.3s ease !important;
}}

.footer-container a {{
    color: {'#00E5FF' if is_dark else '#0284C7'} !important;
    text-decoration: underline !important;
    font-weight: 700 !important;
    transition: all 0.2s ease !important;
}}

.footer-container a:hover {{
    color: {'#D500F9' if is_dark else '#0369A1'} !important;
}}

@media (max-width: 768px) {{
    .brand-title {{
        font-size: 1.8rem !important;
    }}
    .footer-container {{
        font-size: 0.82rem !important;
        padding: 16px 8px 4px 8px !important;
    }}
}}
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# JAVASCRIPT: AUTO-CLOSE SIDEBAR ON TOP NAV CLICKS
# --------------------------------------------------
should_close_sidebar = st.session_state.pop("close_sidebar_now", False)
close_js_flag = "true" if should_close_sidebar else "false"

components.html(f"""
<script>
(function() {{
    const doc = window.parent.document;
    function collapseIfOpen() {{
        const collapseBtn = doc.querySelector('div[data-testid="stSidebarCollapseButton"] button')
            || doc.querySelector('button[aria-label="Collapse sidebar"]');
        if (collapseBtn) {{
            collapseBtn.click();
        }}
    }}

    if ({close_js_flag}) {{
        collapseIfOpen();
    }}

    function attachNavListeners() {{
        const selectors = ['.st-key-btn_top_weave button', '.st-key-btn_top_lib button', '.st-key-btn_top_abt button'];
        selectors.forEach(function(sel) {{
            const btn = doc.querySelector(sel);
            if (btn && !btn.dataset.sidebarAttached) {{
                btn.dataset.sidebarAttached = "true";
                btn.addEventListener('click', function() {{
                    collapseIfOpen();
                }});
            }}
        }});
    }}
    attachNavListeners();
    setTimeout(attachNavListeners, 400);
    setTimeout(attachNavListeners, 1000);

    function pinFooterToBottom() {{
        const el = doc.querySelector('.st-key-footer_block');
        if (!el) return;
        let directChild = el;
        while (directChild && directChild.parentElement && directChild.parentElement.getAttribute('data-testid') !== 'stVerticalBlock') {{
            directChild = directChild.parentElement;
        }}
        if (directChild && directChild.style) {{
            directChild.style.setProperty('margin-top', 'auto', 'important');
        }}
    }}
    pinFooterToBottom();
    setTimeout(pinFooterToBottom, 100);
    setTimeout(pinFooterToBottom, 400);
    setTimeout(pinFooterToBottom, 1000);
    window.addEventListener('resize', pinFooterToBottom);
}})();
</script>
""", height=0, width=0)

# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------
with st.sidebar:
    st.image(str(LOGO_PATH) if LOGO_PATH.exists() else "https://via.placeholder.com/150", width=120)
    st.markdown("### 📖 Story Weave")
    st.caption("Fusing Emotion, Vision & Voice")

    st.markdown("---")

    # Custom Vector Day / Night Switch in Sidebar
    st.markdown("#### 🌓 Theme Mode")
    if st.button(" ", key="btn_side_theme"):
        st.session_state.theme = "light" if is_dark else "dark"
        time.sleep(1.0)
        st.rerun()

    st.markdown("---")

    # Quick Presets (Always visible in Sidebar Navigation)
    st.markdown("#### 💡 Quick Presets")
    c1, c2 = st.columns(2)
    if c1.button("🩸 RBC & WBC", use_container_width=True):
        st.session_state.current_title = "RBC and WBC: Defenders of the Pulse"
        st.session_state.current_desc = "Explain how red and white blood cells protect the human body in an engaging story."
        st.session_state.current_nav = "Weave"
        st.rerun()
    if c2.button("🌲 Clockwork", use_container_width=True):
        st.session_state.current_title = "The Clockwork Forest"
        st.session_state.current_desc = "A young tinkerer discovers trees made of brass and amber that chime in the morning breeze."
        st.session_state.current_nav = "Weave"
        st.rerun()
    st.markdown("---")

    # Download Latest APK (v8a) right above Footer
    st.markdown("#### 📱 Android Companion")
    apk_v8_file = MEDIA_DIR / "app-arm64-v8a-release.apk"
    if apk_v8_file.exists():
        with open(apk_v8_file, "rb") as f_v8:
            st.download_button(
                label="📱 Download Latest APK (v8a • 35.6 MB)",
                data=f_v8.read(),
                file_name="StoryWeave-arm64-v8a-release.apk",
                mime="application/vnd.android.package-archive",
                use_container_width=True,
                help="Download the latest v8a Android release APK (35.6 MB)"
            )

    st.markdown("---")
    # Sidebar Footer (Responsive, moves and collapses with navigation)
    st.markdown("""
    <div class="sidebar-fixed-footer">
        <div style="font-weight: 700; font-size: 0.85rem; letter-spacing: 0.3px;">Story Weave v1.0.0</div>
        <div style="font-weight: 500; font-size: 0.78rem; opacity: 0.85; margin-top: 2px;">Developed by Kokala Sai Teja</div>
    </div>
    """, unsafe_allow_html=True)

# --------------------------------------------------
# TOP NAV / HEADER (AUTO CLOSES SIDEBAR ON CLICK)
# --------------------------------------------------
c_head, c_nav = st.columns([4.2, 5.8], vertical_alignment="center")
with c_head:
    st.markdown("""
    <div style="padding: 0;">
        <h1 class="brand-title" style="margin: 0; line-height: 1.15;">Story Weave</h1>
    </div>
    """, unsafe_allow_html=True)

with c_nav:
    t1, t2, t3 = st.columns(3, vertical_alignment="center")
    with t1:
        if st.button("✨ Story Creator", key="btn_top_weave", use_container_width=True):
            st.session_state.current_nav = "Weave"
            st.session_state.close_sidebar_now = True
            st.rerun()
    with t2:
        if st.button("📚 Story Library", key="btn_top_lib", use_container_width=True):
            st.session_state.current_nav = "Library"
            st.session_state.close_sidebar_now = True
            st.rerun()
    with t3:
        if st.button("🌟 Motive & Vision", key="btn_top_abt", use_container_width=True):
            st.session_state.current_nav = "About"
            st.session_state.close_sidebar_now = True
            st.rerun()

# Subtitle Row (Left: Subtitle, Right-most: Day / Night Theme Toggle Switch Pill)
c_sub, c_toggle = st.columns([8.2, 1.8], vertical_alignment="center")
with c_sub:
    st.markdown("""
    <div style="padding: 0;">
        <p class="brand-subtitle" style="margin: 0; line-height: 1.2;">Fusing Emotion, Vision & Voice for Intelligent Storytelling</p>
    </div>
    """, unsafe_allow_html=True)

with c_toggle:
    if st.button(" ", key="btn_top_theme"):
        st.session_state.theme = "light" if is_dark else "dark"
        time.sleep(1.0)
        st.rerun()

# Spacious gap below subtitle row before main interactive cards
st.markdown('<div class="brand-subtitle-spacer" style="margin-bottom: 26px;"></div>', unsafe_allow_html=True)

# --------------------------------------------------
# STORY GENERATION ENGINE
# --------------------------------------------------
def safe_generate_story(title, genre, description, key):
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
(18–20 lines)

Conclusion:
(3–4 lines)

Keep under 500 words.
"""
    if HAVE_GEMINI_LIB and key:
        try:
            genai.configure(api_key=key)
            model = genai.GenerativeModel("gemini-2.5-flash")
            for attempt in range(3):
                try:
                    res = model.generate_content(prompt)
                    if res and res.text:
                        return res.text.strip()
                except ResourceExhausted:
                    time.sleep(1.5 * (attempt + 1))
                except Exception:
                    pass
        except Exception:
            pass

    # High quality fallback matching exact repo template format
    return f"""Title:
{title}

Genre:
{genre}

Concept:
How courageous champions unite to protect vitality, harmony, and peace.

Original Concept:
{description}

Characters:
1. Ruby: Swift crimson voyager carrying life-giving oxygen through the rivers.
2. Warren: Valiant white blood cell sentinel shielding the boundary.

Introduction:
Deep within the warm rivers of the human bloodstream, billions of tiny sentinels journeyed without pause. Ruby spun gracefully through the arteries, her crimson coat gleaming with vital energy.

Story:
With each measured heartbeat, Ruby carried her precious cargo to every eager tissue cell. Suddenly, an alarm echoed across the vascular banks—dust microbes had slipped through a surface scratch! Ruby paused in alarm, but Warren stepped forward with calm resolve, expanding his luminous white pseudopods. With steady courage, Warren encircled the invading bacteria, neutralizing the threat into harmless mist. Ruby smiled warmly, delivering her golden oxygen to repair the boundary. Side by side, the crimson voyager and the valiant sentinel kept the rhythm of life beating strong.

Conclusion:
United by duty and unwavering harmony, the microscopic defenders returned to their quiet watch, proud guardians of an unending journey."""

def generate_visual_prompt(story_text, title, key):
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
    if HAVE_GEMINI_LIB and key:
        try:
            genai.configure(api_key=key)
            model = genai.GenerativeModel("gemini-2.5-flash")
            res = model.generate_content(prompt)
            if res and res.text:
                return res.text.strip()
        except Exception:
            pass

    return f"Cinematic digital painting of {title}. Bioluminescent atmosphere, detailed characters, volumetric lighting, 8k render."

def generate_image(story_text, title, key):
    visual_scene = generate_visual_prompt(story_text, title, key)
    st.session_state.visual_prompt = visual_scene
    visual_scene = visual_scene[:200]
    base_negative = "blurry, low resolution, distorted, extra limbs, text, watermark"
    prompt = f"High quality detailed illustration. Sharp focus. Scene: {visual_scene}"
    encoded_prompt = urllib.parse.quote(prompt + " --no " + base_negative)
    image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=512&height=512&seed=42"

    try:
        response = requests.get(image_url, timeout=45)
        if response.status_code == 200:
            return Image.open(BytesIO(response.content))
    except Exception:
        pass
    return None

def generate_audio(text):
    file_hash = hashlib.md5(text.encode()).hexdigest()[:12]
    audio_path = MEDIA_DIR / f"story_audio_{file_hash}.mp3"
    if not audio_path.exists():
        tts = gTTS(text)
        tts.save(str(audio_path))
    return str(audio_path)

# ==================================================
# SCREEN 1: WEAVE / STORY CREATOR
# ==================================================
if st.session_state.current_nav == "Weave":
    # Clean space above Story Title & Genre
    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
    c_in1, c_in2 = st.columns([3, 1])
    with c_in1:
        story_title = st.text_input(
            "Story Title",
            value=st.session_state.current_title,
            placeholder="RBC and WBC: Defenders of the Pulse"
        )
    with c_in2:
        genre = st.selectbox(
            "Genre",
            ["Science", "Fantasy", "Education", "Mythology", "Sci-Fi", "Drama"]
        )

    description = st.text_area(
        "Story Description / Concept",
        value=st.session_state.current_desc,
        placeholder="Explain how red and white blood cells protect the human body in an engaging story.",
        height=210
    )

    col_btn, col_spacer = st.columns([1, 1])
    with col_btn:
        generate_clicked = st.button("✨ Generate Story Weave", key="btn_generate_story", type="primary", use_container_width=True)

    if generate_clicked:
        if not story_title.strip() or not description.strip():
            st.warning("⚠️ Please provide both a Story Title and a Story Concept.")
        else:
            with st.spinner("🧠 Weaving your narrative with AI..."):
                story = safe_generate_story(story_title, genre, description, gemini_key)
                st.session_state.story = story

            if story:
                with st.spinner("🎨 Creating cinematic visual illustration..."):
                    st.session_state.image = generate_image(story, story_title, gemini_key)
                
                # Save to persistent JSON library
                story_id = f"story_{int(time.time())}"
                add_saved_story({
                    "id": story_id,
                    "title": story_title,
                    "genre": genre,
                    "concept": description,
                    "story": story,
                    "visual_prompt": st.session_state.visual_prompt,
                    "image_url": f"https://image.pollinations.ai/prompt/{urllib.parse.quote(st.session_state.visual_prompt[:180])}?width=512&height=512&seed=42",
                    "created_at": time.strftime("%Y-%m-%d %H:%M")
                })
                st.success("🎉 Story and illustration woven and saved to persistent library!")

    # Display Results
    if st.session_state.story:
        st.markdown("---")
        c_res_text, c_res_media = st.columns([3, 2])

        with c_res_text:
            st.subheader("📜 Generated Narrative")
            st.markdown(f"**Title:** {story_title} &nbsp;|&nbsp; **Genre:** `{genre}`")
            st.text_area("Story Output", value=st.session_state.story, height=470, label_visibility="collapsed")

            st.markdown("#### 🔊 Audio Narration")
            if st.button("🎙️ Generate & Play Narration"):
                with st.spinner("Synthesizing narration audio..."):
                    try:
                        audio_file = generate_audio(st.session_state.story)
                        st.session_state.audio_path = audio_file
                    except Exception as e:
                        st.error(f"Voice synthesis error: {e}")

            if st.session_state.audio_path and os.path.exists(st.session_state.audio_path):
                st.audio(st.session_state.audio_path)
                with open(st.session_state.audio_path, "rb") as af:
                    st.download_button(
                        label="⬇️ Download Narration (.mp3)",
                        data=af.read(),
                        file_name="story_narration.mp3",
                        mime="audio/mp3"
                    )

        with c_res_media:
            st.subheader("🖼 Visual Scene")
            if st.session_state.image:
                st.image(st.session_state.image, caption=f"AI Illustration for: {story_title}", use_container_width=True)
                if st.session_state.visual_prompt:
                    st.caption(f"**Visual Prompt:** {st.session_state.visual_prompt}")
            else:
                st.info("Visual render will appear here once generated.")

# ==================================================
# SCREEN 2: SAVED STORIES LIBRARY (BATCH DELETE & COMPACT SPACING)
# ==================================================
elif st.session_state.current_nav == "Library":
    st.subheader("📚 Saved Stories Library")
    st.caption("All generated stories are persisted in local JSON storage (`data/saved_stories.json`). They persist across page reloads!")

    saved_stories = load_saved_stories()

    c_search, c_filter = st.columns([3, 1])
    with c_search:
        search_query = st.text_input("Search Stories", placeholder="Filter by title or concept...", label_visibility="collapsed")
    with c_filter:
        selected_genre = st.selectbox("Genre Filter", ["All", "Science", "Fantasy", "Education", "Mythology", "Sci-Fi", "Drama"], label_visibility="collapsed")

    filtered = [
        s for s in saved_stories
        if (search_query.lower() in s.get("title", "").lower() or search_query.lower() in s.get("concept", "").lower())
        and (selected_genre == "All" or s.get("genre") == selected_genre)
    ]

    if not filtered:
        st.info("No saved stories match your search criteria. Generate one in the Creator!")
    else:
        # Batch Selection Toolbar
        all_ids = [s.get("id") for s in filtered if s.get("id")]
        is_all_selected = len(all_ids) > 0 and all(i in st.session_state.selected_story_ids for i in all_ids)
        num_selected = len(st.session_state.selected_story_ids.intersection(set(all_ids)))

        c_bulk1, c_bulk2, c_bulk3 = st.columns([1.6, 2.2, 4.2], vertical_alignment="center")
        with c_bulk1:
            if st.button("◻️ Deselect All" if is_all_selected else " ✅ Select All", key="btn_toggle_select_all", use_container_width=True):
                if is_all_selected:
                    st.session_state.selected_story_ids.clear()
                    for s_id_item in all_ids:
                        st.session_state[f"chk_story_{s_id_item}"] = False
                else:
                    st.session_state.selected_story_ids.update(all_ids)
                    for s_id_item in all_ids:
                        st.session_state[f"chk_story_{s_id_item}"] = True
                st.rerun()

        with c_bulk2:
            if st.button(f"🗑️ Delete Selected ({num_selected})", key="btn_batch_delete", disabled=(num_selected == 0), type="secondary" if num_selected == 0 else "primary", use_container_width=True):
                delete_saved_stories(st.session_state.selected_story_ids)
                for s_id_del in list(st.session_state.selected_story_ids):
                    st.session_state.pop(f"chk_story_{s_id_del}", None)
                st.session_state.selected_story_ids.clear()
                st.success(f"Successfully deleted {num_selected} selected stories!")
                st.rerun()

        with c_bulk3:
            st.markdown(f"""
            <div style="display: flex; justify-content: flex-end; align-items: center; width: 100%; text-align: right; font-size: 0.92rem; font-weight: 500; opacity: 0.85;">
                Showing {len(filtered)} saved stories ({num_selected} selected)
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

        for item in filtered:
            s_id = item.get("id")
            is_checked = s_id in st.session_state.selected_story_ids

            if f"chk_story_{s_id}" not in st.session_state:
                st.session_state[f"chk_story_{s_id}"] = is_checked

            c_chk, c_card = st.columns([0.05, 0.95])
            with c_chk:
                new_chk = st.checkbox("Select", value=is_checked, key=f"chk_story_{s_id}", label_visibility="collapsed")
                if new_chk != is_checked:
                    if new_chk:
                        st.session_state.selected_story_ids.add(s_id)
                    else:
                        st.session_state.selected_story_ids.discard(s_id)
                    st.rerun()

            with c_card:
                with st.expander(f"📖 {item.get('title')} ({item.get('genre')}) • {item.get('created_at', '')}"):
                    c_card_text, c_card_img = st.columns([3, 2])
                    with c_card_text:
                        # Fix Concept Spacing: Clean compact div without large divider gap
                        st.markdown(f"""
                        <div style="margin-bottom: 10px; line-height: 1.5;">
                            <strong style="color: {'#00E5FF' if is_dark else '#0284C7'};">Concept:</strong> 
                            <span style="color: {text_color}; margin-left: 6px;">{item.get('concept', '')}</span>
                        </div>
                        """, unsafe_allow_html=True)

                        st.text_area("Story", value=item.get("story", ""), height=470, key=f"txt_{s_id}", label_visibility="collapsed")
                        
                        # Audio Playback & Single Delete Option
                        st.markdown("##### 🎙️ Voice Narration Audio")
                        try:
                            saved_audio_file = generate_audio(item.get("story", ""))
                            if saved_audio_file and os.path.exists(saved_audio_file):
                                st.audio(saved_audio_file)
                                c_dl, c_del = st.columns([2, 1])
                                with c_dl:
                                    with open(saved_audio_file, "rb") as saf:
                                        st.download_button(
                                            label="⬇️ Download Narration (.mp3)",
                                            data=saf.read(),
                                            file_name=f"{item.get('title', 'story').replace(' ', '_')}_audio.mp3",
                                            mime="audio/mp3",
                                            key=f"dl_saved_{s_id}"
                                        )
                                with c_del:
                                    if st.button("🗑️ Delete Story", key=f"btn_single_del_{s_id}", use_container_width=True):
                                        delete_saved_story(s_id)
                                        st.session_state.selected_story_ids.discard(s_id)
                                        st.success(f"Deleted '{item.get('title')}'")
                                        st.rerun()
                        except Exception as ea:
                            st.caption(f"Audio playback note: {ea}")

                    with c_card_img:
                        if item.get("image_url"):
                            st.image(item.get("image_url"), caption=item.get("title"), use_container_width=True)

# ==================================================
# SCREEN 3: MOTIVE & VISION (PROJECT INSPIRATION)
# ==================================================
elif st.session_state.current_nav == "About":
    st.markdown("## 🌟 Project Motive & Vision")
    
    st.markdown("""
    ### 🌈 Why Story Weave Was Made
    Every child, student, and lifelong learner deserves to experience stories not just as flat text on a screen, but as **living, breathing worlds**. 
    
    **Story Weave** was born from a passion to unite the warmth of childhood bedtime storytelling with the magic of modern artificial intelligence. Too often, educational and creative storytelling tools are fragmented—text in one app, pictures in another, and audio nowhere to be found. 
    
    Our motive is to provide an **all-in-one multimodal sanctuary**:
    - **Empowering Young Imaginations**: Transforming simple ideas into rich, structured narratives across science, fantasy, mythology, and education.
    - **Visualizing Dreams**: Generating high-fidelity cinematic illustrations so characters and settings come to life.
    - **Voicing Every Word**: Reading stories aloud with clear, natural speech synthesis to enhance reading comprehension and accessibility.
    """)

    st.markdown("---")

    c_f1, c_f2 = st.columns(2)
    with c_f1:
        st.markdown("""
        ### 🚀 Current Features (v1.0.0)
        - 🧠 **Structured Narrative Engine**: Built with Google Gemini 2.5 Flash to write gentle, age-appropriate stories across 6 genres under 500 words.
        - 🎨 **8K Cinematic Visual Scenes**: Automatic visual moment extraction rendered via Pollinations AI.
        - 🎙️ **Voice Narration (gTTS)**: In-app real-time text-to-speech audio synthesis and MP3 export.
        - 📚 **Zero-Database Persistence**: Stories safely saved to disk in `data/saved_stories.json` (Web) and Android `SharedPreferences` (Mobile).
        - 🌓 **Day & Night Themes**: Dynamic Obsidian-Neon and Pearl-Day aesthetics with smooth animated toggling.
        """)
    with c_f2:
        st.markdown("""
        ### ✨ Newly Updated & Roadmap Features
        - 🎧 **Direct Library Audio Playback**: Listen to voice narration for every saved story in your library.
        - 📱 **Companion Mobile Monorepo**: Complete native Flutter Android app mirroring web features with zero server dependency.
        - 📤 **Multimodal One-Tap Share**: Share story text, cover artwork, and narration audio simultaneously.
        - 📦 **Direct Standalone APK Distribution**: Pre-compiled release builds for all Android ABIs (ARM64-v8a, ARMv7a, x86_64, Universal).
        - 🌐 **Offline Resilient Mode**: Seamless client-side generation when offline or during cloud cold-starts.
        """)

    st.markdown("---")
    st.markdown("### 🧑‍💻 Developer & Contact")
    st.markdown("**Kokala Sai Teja** — Full-Stack & Mobile AI Developer")

    # Fix Image 3: Vibrant Mobile-matching LinkedIn (#0077B5) and Email (#EA4335) buttons
    st.markdown("""
    <div style="display: flex; gap: 16px; margin-top: 14px; flex-wrap: wrap;">
        <a href="https://www.linkedin.com/in/sai-teja-kokala-245a12299?utm_source=share_via&utm_content=profile&utm_medium=member_android" target="_blank" class="btn-contact-linkedin">
            <svg style="width: 18px; height: 18px; fill: currentColor;" viewBox="0 0 24 24"><path d="M19 3a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h14m-.5 15.5v-5.3a3.26 3.26 0 0 0-3.26-3.26c-.85 0-1.84.52-2.28 1.3v-1.11h-2.79v8.37h2.79v-4.93c0-.77.62-1.4 1.39-1.4a1.4 1.4 0 0 1 1.4 1.4v4.93h2.75M6.46 10.9v8.37H9.2V10.9H6.46M7.83 6.3a1.64 1.64 0 1 0 0 3.28 1.64 1.64 0 0 0 0-3.28Z"/></svg>
            LinkedIn Profile
        </a>
        <a href="mailto:kokalasaiteja@gmail.com?subject=Story%20Weave%20Inquiry" class="btn-contact-email">
            <svg style="width: 18px; height: 18px; fill: currentColor;" viewBox="0 0 24 24"><path d="M20 4H4c-1.1 0-1.99.9-1.99 2L2 18c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm0 4-8 5-8-5V6l8 5 8-5v2z"/></svg>
            Email Developer
        </a>
    </div>
    """, unsafe_allow_html=True)

# --------------------------------------------------
# FOOTER (ALL APKS & DEVELOPER CONTACT WITH ZERO DEAD SPACE)
# --------------------------------------------------
footer_block = st.container(key="footer_block")
with footer_block:
    st.markdown("---")
    st.markdown("#### 📦 Download Story Weave Android Mobile App")
    st.caption("Standalone offline release APKs for all Android hardware architectures (Freshly compiled Flutter release builds):")
    col_apk1, col_apk2, col_apk3, col_apk4 = st.columns(4)

    with col_apk1:
        p1 = MEDIA_DIR / "app-arm64-v8a-release.apk"
        if p1.exists():
            with open(p1, "rb") as f1:
                st.download_button("📱 ARM64-v8a (35.6 MB)", f1.read(), "StoryWeave-arm64-v8a.apk", "application/vnd.android.package-archive", use_container_width=True, key="ft_apk_v8")

    with col_apk2:
        p2 = MEDIA_DIR / "app-armeabi-v7a-release.apk"
        if p2.exists():
            with open(p2, "rb") as f2:
                st.download_button("📱 ARMv7a (33.1 MB)", f2.read(), "StoryWeave-armeabi-v7a.apk", "application/vnd.android.package-archive", use_container_width=True, key="ft_apk_v7")

    with col_apk3:
        p3 = MEDIA_DIR / "app-x86_64-release.apk"
        if p3.exists():
            with open(p3, "rb") as f3:
                st.download_button("💻 x86_64 (37.1 MB)", f3.read(), "StoryWeave-x86_64.apk", "application/vnd.android.package-archive", use_container_width=True, key="ft_apk_x86")

    with col_apk4:
        p4 = MEDIA_DIR / "app-release.apk"
        if p4.exists():
            with open(p4, "rb") as f4:
                st.download_button("📦 Universal Fat APK (70.5 MB)", f4.read(), "StoryWeave-Universal.apk", "application/vnd.android.package-archive", use_container_width=True, key="ft_apk_fat")

    st.markdown("""
    <div class="footer-container">
        <p style="margin-bottom: 4px;"><b>Story Weave</b> • Fusing Emotion, Vision & Voice for Intelligent Storytelling</p>
        <p style="margin-bottom: 0px;">Developed by <b>Kokala Sai Teja</b> &nbsp;|&nbsp; 
           <a href="https://www.linkedin.com/in/sai-teja-kokala-245a12299?utm_source=share_via&utm_content=profile&utm_medium=member_android" target="_blank">LinkedIn Profile</a> &nbsp;•&nbsp; 
           <a href="mailto:kokalasaiteja@gmail.com?subject=Story%20Weave%20Inquiry">Email: kokalasaiteja@gmail.com</a>
        </p>
    </div>
    """, unsafe_allow_html=True)
