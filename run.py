from flask import Flask, request, render_template, send_file, redirect, url_for
from werkzeug.utils import secure_filename
from PIL import Image
import os
import uuid
import wave
import numpy as np

app = Flask(__name__)

# Folder setup
UPLOAD_FOLDER = 'uploads/'
ENCRYPTED_FOLDER = 'encrypted/'
AUDIO_FOLDER = 'audio/'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(ENCRYPTED_FOLDER, exist_ok=True)
os.makedirs(AUDIO_FOLDER, exist_ok=True)

chat_messages = []

class AudioImageStego:
    def __init__(self):
        self.bits_per_byte = 8
        self.delimiter = b'EOI'  
    
    def embed_image(self, audio_path, image_path, output_path):
        """Embed image data into audio file without altering image pixels"""
       
        with wave.open(audio_path, 'rb') as audio:
            params = audio.getparams()
            frames = audio.readframes(audio.getnframes())
            audio_data = np.frombuffer(frames, dtype=np.int16)
        
        
        with Image.open(image_path) as img:
            img_bytes = img.tobytes()
            img_size = len(img_bytes)
            img_width, img_height = img.size
            img_mode = img.mode
        
      
        header = f"{img_width},{img_height},{img_mode},{img_size}".encode()
        total_data = header + b'|' + img_bytes + self.delimiter
        
        if len(total_data) * 8 > len(audio_data):
            raise ValueError("Audio file too small to hold image data")
        
       
        binary_data = ''.join([format(byte, '08b') for byte in total_data])
        

        modified_audio = audio_data.copy()
        for i, bit in enumerate(binary_data):
            modified_audio[i] = (modified_audio[i] & ~1) | int(bit)
        
      
        with wave.open(output_path, 'wb') as output:
            output.setparams(params)
            output.writeframes(modified_audio.tobytes())
        
        return output_path
    
    def extract_image(self, stego_audio_path, output_image_path):
        """Extract hidden image from audio file"""
      
        with wave.open(stego_audio_path, 'rb') as audio:
            frames = audio.readframes(audio.getnframes())
            audio_data = np.frombuffer(frames, dtype=np.int16)
        
    
        binary_data = ''.join([str(sample & 1) for sample in audio_data])
        
     
        extracted_bytes = bytearray()
        for i in range(0, len(binary_data), 8):
            byte = int(binary_data[i:i+8], 2)
            extracted_bytes.append(byte)
        
      
        data = bytes(extracted_bytes)
        header_end = data.find(b'|')
        if header_end == -1:
            raise ValueError("Invalid stego file: no header found")
        
        
        header = data[:header_end].decode()
        width, height, mode, size = header.split(',')
        width, height, size = int(width), int(height), int(size)
        
        
        img_start = header_end + 1
        img_data = data[img_start:img_start+size]
        
       
        img = Image.frombytes(mode, (width, height), img_data)
        img.save(output_image_path)
        
        return output_image_path


def encode_message_in_image(image_file, message):
    org_img = Image.open(image_file)
    if org_img.mode != 'RGB':
        org_img = org_img.convert('RGB')
    
    pixel_map = org_img.load()
    enc_img = Image.new(org_img.mode, org_img.size)
    enc_pixel_map = enc_img.load()

    msg_len = len(message)
    msg_index = 0

    
    for row in range(org_img.size[0]):
        for col in range(org_img.size[1]):
            r, g, b = pixel_map[row, col]
            if row == 0 and col == 0:
                enc_pixel_map[row, col] = (msg_len, g, b)
            elif msg_index < msg_len:
                ascii_val = ord(message[msg_index])
                enc_pixel_map[row, col] = (ascii_val, g, b)
                msg_index += 1
            else:
                enc_pixel_map[row, col] = (r, g, b)

    encrypted_filename = f"encrypted_image_{uuid.uuid4().hex}.png"
    encrypted_path = os.path.join(ENCRYPTED_FOLDER, encrypted_filename)
    enc_img.save(encrypted_path)
    return encrypted_path, encrypted_filename


def decode_message_from_image(encrypted_image_file):
    enc_img = Image.open(encrypted_image_file)
    pixel_map = enc_img.load()

    message = ""
    msg_len = pixel_map[0, 0][0]  
    msg_index = 0

    for row in range(enc_img.size[0]):
        for col in range(enc_img.size[1]):
            if row == 0 and col == 0:
                continue  
            if msg_index < msg_len:
                r = pixel_map[row, col][0]
                message += chr(r)
                msg_index += 1

    return message


audio_stego = AudioImageStego()

@app.route('/chat', methods=['GET', 'POST'])
def chat():
    if request.method == 'POST':
        
        message = request.form.get('message')
        if message:
            chat_messages.append({'type': 'text', 'content': message})

        
        image = request.files.get('image')
        encode_message = request.form.get('encode_message')
        audio = request.files.get('audio')

        if image and encode_message:
            
            image_path, encrypted_filename = encode_message_in_image(image, encode_message)
            
            
            if audio:
                
                audio_filename = f"input_audio_{uuid.uuid4().hex}.wav"
                audio_path = os.path.join(AUDIO_FOLDER, audio_filename)
                audio.save(audio_path)
                
               
                stego_audio_filename = f"stego_audio_{uuid.uuid4().hex}.wav"
                stego_audio_path = os.path.join(AUDIO_FOLDER, stego_audio_filename)
                
                try:
                    audio_stego.embed_image(audio_path, image_path, stego_audio_path)
                    chat_messages.append({
                        'type': 'audio', 
                        'content': stego_audio_filename,
                        'original_image': encrypted_filename
                    })
                except Exception as e:
                    chat_messages.append({'type': 'error', 'content': str(e)})
            else:
                
                chat_messages.append({'type': 'image', 'content': encrypted_filename})

        return redirect(url_for('chat'))

    return render_template('chat.html', messages=chat_messages)


@app.route('/decode', methods=['POST'])
def decode():
    if 'encrypted_image' not in request.files:
        return 'No file provided for decoding', 400

    encrypted_image = request.files['encrypted_image']
    filename = secure_filename(encrypted_image.filename)
    encrypted_path = os.path.join(UPLOAD_FOLDER, filename)
    encrypted_image.save(encrypted_path)

    
    decoded_message = decode_message_from_image(encrypted_path)

    
    return f"The hidden message is: {decoded_message}"


@app.route('/decode_audio', methods=['POST'])
def decode_audio():
    if 'stego_audio' not in request.files:
        return 'No audio file provided for decoding', 400

    stego_audio = request.files['stego_audio']
    filename = secure_filename(stego_audio.filename)
    audio_path = os.path.join(UPLOAD_FOLDER, filename)
    stego_audio.save(audio_path)

    try:
       
        extracted_image_filename = f"extracted_image_{uuid.uuid4().hex}.png"
        extracted_image_path = os.path.join(ENCRYPTED_FOLDER, extracted_image_filename)
        audio_stego.extract_image(audio_path, extracted_image_path)

      
        decoded_message = decode_message_from_image(extracted_image_path)

        return render_template('decode_result.html', 
                               extracted_image=extracted_image_filename, 
                               decoded_message=decoded_message)
    except Exception as e:
        return f"Error decoding audio: {str(e)}"


@app.route('/download/<filename>')
def download(filename):
    file_path = os.path.join(ENCRYPTED_FOLDER, filename)
    if not os.path.exists(file_path):
        return "File not found", 404
    return send_file(file_path, as_attachment=True)


@app.route('/download_audio/<filename>')
def download_audio(filename):
    file_path = os.path.join(AUDIO_FOLDER, filename)
    if not os.path.exists(file_path):
        return "File not found", 404
    return send_file(file_path, as_attachment=True)


@app.route('/')
def index():
    return redirect(url_for('chat'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, ssl_context='adhoc', debug=True)