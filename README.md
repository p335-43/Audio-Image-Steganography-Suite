
# Audio-Image Steganography Suite

**Audio-Image Steganography Suite** is a Flask-based web application that enables secure communication by embedding images into audio files and encoding messages within images. It supports encryption, decryption, and retrieval of hidden data with ease.

---

## 🚀 Features

- **Image Steganography**: Encode text messages into images and decode them effortlessly.
- **Audio Steganography**: Embed images within audio files without altering image pixels.
- **Secure Communication**: Protect sensitive information by hiding it in media files.
- **User-Friendly Interface**: A chat-like interface for managing media files and hidden data.
- **File Download Support**: Download encrypted media files for sharing.

---

## 🛠️ Tech Stack

- **Backend**: Python (Flask Framework)
- **Frontend**: HTML, CSS (with Flask Templates)
- **Libraries**:
  - [Pillow](https://python-pillow.org/) for image processing.
  - [NumPy](https://numpy.org/) for handling binary data.
  - [Wave](https://docs.python.org/3/library/wave.html) for audio file manipulation.
- **Database**: None (in-memory storage for chat messages).

---

## 🗂️ Project Structure
```
.
├── run.py                  # Main Flask application
├── templates/
│   ├── chat.html           # Chat interface for interaction
│   ├── decode_result.html  # Result page for decoded media
├── uploads/                # Folder for uploaded files
├── encrypted/              # Folder for encrypted files
├── audio/                  # Folder for audio files
├── requirements.txt        # Project dependencies
└── README.md               # Project documentation
```
---

## 🛠️ Setup & Installation

1. **Clone the Repository**  
   ```bash
   git clone https://github.com/p335-43/AudioImage-Stego-Suite.git
   cd Audio-Image-Stego-Suite
   ```

2. **Install Dependencies**  
   Ensure you have Python 3.7+ installed, then run:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the Application**  
   Start the Flask development server:
   ```bash
   python run.py
   ```

4. **Access the Application**  
   Open your browser and navigate to:  
   [http://localhost:5001](http://localhost:5001)

---

## 💻 Usage

### 1. Image Steganography
- **Encode a Message**: Upload an image, enter a message, and encrypt it.
- **Decode a Message**: Upload the encrypted image to retrieve the hidden message.

### 2. Audio Steganography
- **Embed an Image**: Upload an image and an audio file to embed the image into the audio.
- **Extract an Image**: Upload the stego-audio file to extract the embedded image.

---


## 🔒 Security Features

- Steganography ensures the hidden data remains undetectable to casual viewers.
- Uses a delimiter and header system for precise extraction of data.

---


## 🌟 Acknowledgments

- [Flask Documentation](https://flask.palletsprojects.com/)
- [Pillow Documentation](https://pillow.readthedocs.io/)
- [NumPy Documentation](https://numpy.org/doc/)
