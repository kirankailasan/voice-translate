from flask import Flask, request, jsonify, send_file
import os
import tempfile
import whisper
from gtts import gTTS
import requests

app = Flask(__name__)

# Load Whisper model (small model for performance)
model = whisper.load_model("small")

# LibreTranslate API for translation
LIBRETRANSLATE_URL = "https://libretranslate.de/translate"

# Speech-to-Text using Whisper
def speech_to_text(audio_path):
    result = model.transcribe(audio_path)
    return result["text"]

# Translate text using LibreTranslate
def translate_text(text, source_lang, target_lang):
    payload = {
        "q": text,
        "source": source_lang,
        "target": target_lang,
        "format": "text"
    }
    response = requests.post(LIBRETRANSLATE_URL, data=payload)
    return response.json().get("translatedText", "")

# Convert text to speech using gTTS
def text_to_speech(text, lang):
    tts = gTTS(text=text, lang=lang)
    temp_audio = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    tts.save(temp_audio.name)
    return temp_audio.name

@app.route("/translate", methods=["POST"])
def translate_audio():
    if 'audio' not in request.files:
        return jsonify({"error": "No audio file uploaded"}), 400
    
    audio_file = request.files['audio']
    temp_audio = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    audio_file.save(temp_audio.name)
    
    source_lang = request.form.get("source_lang", "auto")
    target_lang = request.form.get("target_lang")
    
    if not target_lang:
        return jsonify({"error": "Target language is required"}), 400
    
    text = speech_to_text(temp_audio.name)
    translated_text = translate_text(text, source_lang, target_lang)
    audio_output = text_to_speech(translated_text, target_lang)
    
    return send_file(audio_output, as_attachment=True, download_name="translated_audio.mp3", mimetype="audio/mpeg")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
