# 📖 Story Weave

**Story Weave** is an AI-powered multimodal storytelling app that fuses **text, visuals, and voice** to create engaging stories in a few clicks. Users can provide a story title, genre, and concept, and the app generates a short story, a cinematic illustration, and a narration of the story.  

---

## 🌟 Features

- **Story Generation:** AI-generated stories in three sections: Introduction, Story, and Conclusion.
- **Image Generation:** Cinematic illustrations extracted from the story using AI.
- **Audio Narration:** Text-to-speech (TTS) conversion for immersive storytelling.
- **Interactive UI:** Simple Streamlit interface with session state handling for smooth experience.
- **Multi-Genre Support:** Fantasy, Science, Education, Mythology, Sci-Fi, Drama.

---

## 🚀 Live Demo

Try the app live here: [Story Weave Live](https://ai-story-generator-with-image.streamlit.app/)  

---

## 🛠 Technology Stack

- **Frontend & UI:** Streamlit  
- **Story Generation:** Google Gemini 2.5 Generative AI  
- **Image Generation:** Pollinations AI (Stable Diffusion-based)  
- **Audio Generation:** gTTS (Google Text-to-Speech)  
- **Image Processing:** PIL (Python Imaging Library)  
- **HTTP Requests:** Requests library for API calls  

---

## 📦 Installation & Usage

1. **Clone the repository:**
    ```bash
    git clone https://github.com/yourusername/story-weave.git
    cd story-weave
    ```

2. **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3. **Set your secrets:**
    - Add your Gemini API key in `secrets.toml` or Streamlit secrets:
    ```toml
    [general]
    GEMINI_API_KEY = "your_gemini_api_key_here"
    HF_API_KEY = "your_huggingface_api_key_here"

    Note: Never hardcode API keys in your code. Use Streamlit secrets or environment variables.
    ```

4. **Run the app locally:**
    ```bash
    streamlit run app.py
    ```

5. **Open in your browser** at `http://localhost:8501` and enjoy storytelling.

---

## 📝 Usage Guide

1. Enter **Story Title**.  
2. Select a **Genre** from the dropdown.  
3. Write your **Story Description / Concept**.  
4. Click **✨ Generate Story Weave**.  
5. View the generated **story** and **illustration**.  
6. Click **🔊 Read Aloud Story** to listen to the narration.

---

## 🧑‍💻 Developer

Developed by **Kokala Sai Teja**  
- Email: kokalasaiteja@gmail.com  
- LinkedIn: [linkedin.com/in/kokalasaiteja](https://www.linkedin.com/in/sai-teja-kokala-245a12299/)

---

## ⚡ Future Enhancements

- Customizable voice options for narration.  
- Multiple illustration styles (cartoon, watercolor, cinematic).  
- Multi-language support for stories and audio.  
- Save stories and images to a personal gallery.  

---

## 📜 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## 🖼 Sample Output

Below is an example of what **Story Weave** generates:

<img width="350" height="450" alt="image" src="https://github.com/user-attachments/assets/9d7d3eaa-0469-47d0-9faf-64b189a1b317" />
<img width="350" height="450" alt="image" src="https://github.com/user-attachments/assets/564842a3-671d-468c-81a7-ff6e1cc6df39" />
<img width="250" height="180" alt="image" src="https://github.com/user-attachments/assets/af6416c7-ae33-435e-9357-fe6021c1cd52" />

