import io
import os
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import whisper
from pydub import AudioSegment
from flask_socketio import SocketIO, send

app = Flask(__name__)
CORS(app)  # Habilita CORS para todas las rutas

app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*")

model = whisper.load_model("medium")


@app.route('/transcribe', methods=['POST'])
def transcribe():
    if 'audio' not in request.files:
        return jsonify({'error': 'No audio file provided'}), 400

    audio_file = request.files['audio']
    
    # Guardar el archivo de audio temporalmente
    temp_audio_path = "temp_audio.mp3"
    audio_data = io.BytesIO(audio_file.read())
    audio = AudioSegment.from_file(audio_data)
    audio.export(temp_audio_path, format="mp3")
    
    # Utilizar la función load_audio de whisper para cargar y convertir el audio
    audio = whisper.load_audio(temp_audio_path)
    
    # Transcribir el audio
    result = model.transcribe(audio)
    
    # Eliminar el archivo de audio temporal
    os.remove(temp_audio_path)
    
    print(result['text'])

    return jsonify({'text': result['text']})

@socketio.on('message')
def handle_message(msg):
    print('Message: ' + msg)
    send(msg, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, debug=True)