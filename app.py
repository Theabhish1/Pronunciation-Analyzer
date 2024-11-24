from flask import Flask, render_template, request
import speech_recognition as sr
from pydub import AudioSegment
import base64
from io import BytesIO
import nltk
from nltk.corpus import words

# Download the words corpus (run once)
nltk.download('words')

# Load English words
english_words = set(words.words())

# Initialize Flask app
app = Flask(__name__)

# Function to validate if a word exists in the dictionary
def is_valid_word(word):
    return word.lower() in english_words

# Function to calculate pronunciation mistakes
def calculate_pronunciation_mistakes(student_text):
    if student_text:
        student_words = student_text.lower().split()
        mistakes = [word for word in student_words if not is_valid_word(word)]
        return len(mistakes), mistakes
    return 0, []

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')


@app.route('/recognize', methods=['POST'])
def recognize():
    audio_data_base64 = request.form.get('audio')
    if not audio_data_base64:
        return render_template('results.html', text="No audio data received", mistakes=0, mistake_words=[])

    try:
        # Decode Base64 to binary audio data
        audio_data = base64.b64decode(audio_data_base64)
        audio_file = BytesIO(audio_data)

        # Convert WebM to WAV using pydub
        try:
            webm_audio = AudioSegment.from_file(audio_file, format="webm")
        except Exception as e:
            return render_template('results.html', text=f"Error in decoding audio: {e}", mistakes=0, mistake_words=[])

        wav_audio = BytesIO()
        webm_audio.export(wav_audio, format="wav")
        wav_audio.seek(0)

        recognizer = sr.Recognizer()

        # Perform speech recognition
        with sr.AudioFile(wav_audio) as source:
            audio_content = recognizer.record(source)
            recognized_text = recognizer.recognize_google(audio_content)

            # Calculate pronunciation mistakes
            mistakes, mistake_words = calculate_pronunciation_mistakes(recognized_text)

            return render_template('results.html', text=recognized_text, mistakes=mistakes, mistake_words=mistake_words)

    except sr.UnknownValueError:
        return render_template('results.html', text="Could not understand the audio", mistakes=0, mistake_words=[])
    except Exception as e:
        return render_template('results.html', text=f"Error: {e}", mistakes=0, mistake_words=[])

if __name__ == '__main__':
    app.run()  # Remove debug=True)
