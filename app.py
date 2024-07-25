import io
import os
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import whisper
from pydub import AudioSegment
from flask_socketio import SocketIO, send
import qrcode
from datetime import datetime

app = Flask(__name__)
CORS(app)  # Habilita CORS para todas las rutas

app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*")

model = whisper.load_model("medium")

@app.route('/generate_qr', methods=['GET'])
def generate_qr():
    param = request.args.get('param', '')
    # Generar el código QR
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Concatenar el parámetro con el tiempo actual
    data = f'http://example.com/start_conversation?param={param}&time={current_time}'

    qr.add_data(data)  # URL para iniciar la conversación
    qr.make(fit=True)

    img = qr.make_image(fill='black', back_color='white')

    # Guardar la imagen en un objeto BytesIO
    img_io = io.BytesIO()
    img.save(img_io, 'PNG')
    img_io.seek(0)

    return send_file(img_io, mimetype='image/png')

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