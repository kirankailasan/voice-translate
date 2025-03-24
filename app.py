from flask import Flask, request, jsonify
from gradio_client import Client
import os

app = Flask(__name__)

client = Client("https://coqui-xtts.hf.space/--replicas/n38lq/") #use the exact url that you found.

@app.route('/generate', methods=['POST'])
def generate():
    data = request.get_json()
    text = data['text']
    audio_url = data['audio_url'] #the url of the audio file.

    try:
        result = client.predict(
            text,
            "en,en",  # Language. Adapt if needed.
            audio_url,
            audio_url,
            True,
            True,
            True,
            True,
            fn_index=1,
        )

        audio_output = result[1] #get the second item from the returned tuple, which is the audio file.
        return jsonify({'audio_output_url': audio_output}) #return the url of the generated audio.

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
