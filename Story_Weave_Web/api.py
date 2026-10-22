import os
import time
import hashlib
import urllib.parse
from pathlib import Path
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import requests

try:
    import google.generativeai as genai
    from google.api_core.exceptions import ResourceExhausted
    HAVE_GEMINI = True
except ImportError:
    HAVE_GEMINI = False

try:
    from gtts import gTTS
    HAVE_GTTS = True
except ImportError:
    HAVE_GTTS = False

# Base directories
BASE_DIR = Path(__file__).resolve().parent
MEDIA_DIR = BASE_DIR / "media"
STATIC_DIR = BASE_DIR / "static"
MEDIA_DIR.mkdir(parents=True, exist_ok=True)
STATIC_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI(
    title="Story Weave API",
    description="Backend API for Story Weave: Multimodal Story, Vision, Voice & APK Distribution",
    version="1.0.0",
)

# Enable CORS for Flutter mobile & web clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static and media folders
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
app.mount("/media", StaticFiles(directory=str(MEDIA_DIR)), name="media")


class StoryRequest(BaseModel):
    title: str
    genre: str
    description: str
    gemini_api_key: Optional[str] = None


class AudioRequest(BaseModel):
    text: str


# Sample stories for instant preview / fallback
SAMPLES = [
    {
        "id": "sample-1",
        "title": "RBC and WBC: Defenders of the Pulse",
        "genre": "Science",
        "concept": "Explain how red and white blood cells protect the human body in an engaging story.",
        "characters": [
            {"name": "Ruby", "role": "A swift Red Blood Cell carrying vital oxygen."},
            {"name": "Warren", "role": "A courageous White Blood Cell sentinel shield."}
        ],
        "story": """Title: Defenders of the Pulse\nGenre: Science\n\nConcept: The tireless journey of bloodstream guardians protecting life within.\n\nCharacters:\n1. Ruby: Swift oxygen transporter gliding along glowing rivers.\n2. Warren: Brave immune warrior standing guard against intruders.\n\nIntroduction:\nDeep within the warm rivers of the bloodstream, Ruby spun gracefully through the arteries. Her crimson shell sparkled as she carried golden packets of oxygen to every eager tissue.\n\nStory:\nSuddenly, an alarm echoed across the vascular banks. A swarm of jagged dust microbes had slipped through a surface scratch! Ruby paused in alarm, but from behind the lymphatic bend stepped Warren, glowing with luminous white resilience. 'Stand firm, little carrier!' Warren announced, extending protective pseudopods to encircle the invading bacteria. Warren neutralized the threat with unwavering precision, dissolving the microbes into harmless mist. Ruby smiled warmly, delivering her precious breath of oxygen to heal the surrounding tissue cells. Side by side, the crimson voyager and the valiant sentinel kept the rhythm of the heart steady and safe.\n\nConclusion:\nThrough harmony and ceaseless devotion, the unseen defenders ensured the great journey of life continued without pause.""",
        "visual_prompt": "Futuristic microscopic view of glowing red blood cells and a luminous white blood cell defender surrounded by soft bioluminescent fluid, cinematic lighting, 8k render",
        "image_url": "https://image.pollinations.ai/prompt/Futuristic%20microscopic%20view%20of%20glowing%20red%20blood%20cells%20and%20luminous%20white%20blood%20cell%20defender%20bioluminescent%208k?width=512&height=512&seed=42"
    },
    {
        "id": "sample-2",
        "title": "The Clockwork Forest",
        "genre": "Fantasy",
        "concept": "A young tinkerer discovers trees made of brass and amber that sing with the morning breeze.",
        "characters": [
            {"name": "Lyra", "role": "An adventurous clockwork apprentice."},
            {"name": "Gideon", "role": "A gentle mechanical owl who guards the ancient grove."}
        ],
        "story": """Title: The Clockwork Forest\nGenre: Fantasy\n\nConcept: A harmony between living nature and enchanted mechanical wonder.\n\nCharacters:\n1. Lyra: An inventive apprentice with a golden pocket wrench.\n2. Gideon: An amber-eyed brass owl who reads the winds.\n\nIntroduction:\nAt the edge of the Whispering Ridge, the leaves did not rustle; they chimed. Lyra held her breath as she stepped beneath the brass boughs of the Clockwork Forest.\n\nStory:\nEvery branch was spun from polished bronze and warm copper, linked by smooth emerald gears that turned in rhythm with the subterranean waterfalls. High on a silver willow, Gideon the owl clicked his beak and fluttered down. 'The sunspring is overwound,' Gideon hooted with melodic resonance. Lyra stepped forward, spotting a trapped crystal pebble between the master gear teeth. Gently aligning her golden wrench, she eased the gear into free rotation. A luminous beam of sunlight struck the grove, setting thousands of brass leaves chiming in joyous symphony.\n\nConclusion:\nWith gears spinning in peaceful balance, Lyra knew that magic and machinery could live as one heart.""",
        "visual_prompt": "Enchanted forest with brass and copper mechanical trees, glowing amber leaves, a girl apprentice and a clockwork owl, soft ethereal sunlight, intricate details, cinematic 8k",
        "image_url": "https://image.pollinations.ai/prompt/Enchanted%20forest%20with%20brass%20mechanical%20trees%20glowing%20amber%20leaves%20clockwork%20owl%20cinematic%208k?width=512&height=512&seed=88"
    }
]


def call_gemini(prompt: str, api_key: Optional[str] = None) -> Optional[str]:
    key = api_key or os.environ.get("GEMINI_API_KEY", "")
    if not key or not HAVE_GEMINI:
        return None
    try:
        genai.configure(api_key=key)
        model = genai.GenerativeModel("gemini-2.5-flash")
        for attempt in range(3):
            try:
                res = model.generate_content(prompt)
                return res.text.strip() if res else None
            except ResourceExhausted:
                if attempt < 2:
                    time.sleep(1.5 * (attempt + 1))
                else:
                    return None
            except Exception:
                return None
    except Exception:
        return None


def generate_fallback_story(title: str, genre: str, description: str) -> str:
    return f"""Title:
{title}

Genre:
{genre}

Concept:
{description}

Characters:
1. Orion: The daring explorer who seeks the truth.
2. Lyra: The compassionate guide whose wisdom lights the way.

Introduction:
The journey began where ancient horizons met the boundless sky. {title} had long been whispered among travelers, but few dared to seek its secrets.

Story:
With each measured step, Orion and Lyra traversed the untamed valleys. {description} Through trial and wonder, they unraveled the quiet mystery that linked every living creature to the starlit canopy. Challenges arose like sudden storms, yet patience and courage bridged every divide. When the final revelation dawned, it was not of power, but of deep harmony and shared purpose.

Conclusion:
United by trust and wonder, they returned to share their tale, knowing that every great journey begins with a single bold question.
"""


def extract_visual_prompt_simple(story: str, title: str) -> str:
    lines = [line.strip() for line in story.split("\n") if line.strip() and not line.startswith("Title:") and not line.startswith("Genre:")]
    summary = " ".join(lines[:4])[:180]
    return f"Cinematic digital painting of {title}. {summary}. High quality, 8k resolution, dramatic lighting, detailed atmosphere."


@app.get("/")
def read_root():
    return {
        "app": "Story Weave",
        "version": "1.0.0",
        "tagline": "Fusing Emotion, Vision & Voice for Intelligent Storytelling",
        "status": "online",
        "docs_url": "/docs",
        "download_apk_url": "/download-apk/app-arm64-v8a-release.apk"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "app": "Story Weave",
        "timestamp": time.time(),
        "gemini_available": HAVE_GEMINI and bool(os.environ.get("GEMINI_API_KEY")),
        "gtts_available": HAVE_GTTS
    }


@app.get("/api/samples")
def get_samples():
    return {"samples": SAMPLES}


@app.post("/api/generate")
def generate_all(req: StoryRequest):
    # 1. Story generation
    story_prompt = f"""Write a clear, emotionally engaging story suitable for all ages.
Rules:
- Simple vocabulary, short sentences, gentle emotional tone
- Use at most 5 characters
FORMAT:
Title: {req.title}
Genre: {req.genre}
Concept: Rewrite clearly based on: {req.description}
Characters:
1. Name: short line
2. Name: short line
Introduction: (4-5 lines)
Story: (15-20 lines)
Conclusion: (3-4 lines)
Keep under 450 words.
"""
    story_text = call_gemini(story_prompt, req.gemini_api_key)
    if not story_text:
        story_text = generate_fallback_story(req.title, req.genre, req.description)

    # 2. Visual prompt extraction
    visual_gen_prompt = f"Extract ONE clear visual scene from this story. Describe only visible elements (characters, scene, lighting). Max 35 words:\n{story_text}"
    visual_prompt = call_gemini(visual_gen_prompt, req.gemini_api_key)
    if not visual_prompt:
        visual_prompt = extract_visual_prompt_simple(story_text, req.title)

    # 3. Image URL from Pollinations AI
    clean_prompt = visual_prompt[:220]
    encoded_prompt = urllib.parse.quote(f"{clean_prompt} --no blurry, low quality, watermark, text")
    image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=512&height=512&seed=42"

    # 4. Audio generation
    audio_path = None
    audio_url = None
    if HAVE_GTTS and story_text:
        try:
            file_hash = hashlib.md5(story_text.encode()).hexdigest()[:12]
            audio_filename = f"audio_{file_hash}.mp3"
            full_path = MEDIA_DIR / audio_filename
            if not full_path.exists():
                tts = gTTS(story_text)
                tts.save(str(full_path))
            audio_url = f"/media/{audio_filename}"
        except Exception:
            audio_url = None

    return {
        "title": req.title,
        "genre": req.genre,
        "story": story_text,
        "visual_prompt": visual_prompt,
        "image_url": image_url,
        "audio_url": audio_url
    }


@app.post("/api/generate_audio")
def generate_audio(req: AudioRequest):
    if not HAVE_GTTS:
        raise HTTPException(status_code=500, detail="gTTS engine is not available on this server.")
    try:
        file_hash = hashlib.md5(req.text.encode()).hexdigest()[:12]
        audio_filename = f"audio_{file_hash}.mp3"
        full_path = MEDIA_DIR / audio_filename
        if not full_path.exists():
            tts = gTTS(req.text)
            tts.save(str(full_path))
        return {"audio_url": f"/media/{audio_filename}", "filename": audio_filename}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/apk-info")
def get_apk_info():
    apk_files = {
        "arm64-v8a": "app-arm64-v8a-release.apk",
        "armeabi-v7a": "app-armeabi-v7a-release.apk",
        "x86_64": "app-x86_64-release.apk",
        "universal": "app-release.apk"
    }
    builds = []
    for abi, fname in apk_files.items():
        apk_path = MEDIA_DIR / fname
        exists = apk_path.exists()
        size_bytes = apk_path.stat().st_size if exists else 0
        size_mb = round(size_bytes / (1024 * 1024), 2)
        builds.append({
            "abi": abi,
            "filename": fname,
            "download_url": f"/download-apk/{fname}",
            "available": exists,
            "size_mb": size_mb
        })
    return {
        "version": "1.0.0",
        "app_name": "Story Weave",
        "builds": builds,
        "recommended": "app-arm64-v8a-release.apk"
    }


@app.get("/download-apk/{filename}")
def download_apk(filename: str):
    # Security check: only allow valid apk filenames
    allowed = [
        "app-arm64-v8a-release.apk",
        "app-armeabi-v7a-release.apk",
        "app-x86_64-release.apk",
        "app-release.apk"
    ]
    if filename not in allowed:
        raise HTTPException(status_code=400, detail="Invalid APK artifact requested.")

    file_path = MEDIA_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail=f"Build artifact '{filename}' not yet compiled. Run 'flutter build apk --split-per-abi' first.")

    return FileResponse(
        path=str(file_path),
        media_type="application/vnd.android.package-archive",
        filename=filename,
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Cache-Control": "no-cache"
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
