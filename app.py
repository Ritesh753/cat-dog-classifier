from flask import Flask, request, jsonify, render_template
from tensorflow.keras.models import load_model
from huggingface_hub import hf_hub_download
import numpy as np
import cv2
import os

app = Flask(__name__)

# Download the model from Hugging Face (only downloads once, then uses the cached copy)
MODEL_PATH = hf_hub_download(
    repo_id="Ritesh753/cat-dog-classifier",
    filename="cat_dog_model.keras"
    # If your repo is private, add: token=True
)
model = load_model(MODEL_PATH)
print("Model loaded successfully!")


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/predict', methods=['POST'])
def predict():
    if 'image' not in request.files:
        return jsonify({'error': 'No image uploaded'}), 400

    file = request.files['image']

    if file.filename == '':
        return jsonify({'error': 'No image selected'}), 400

    npimg = np.frombuffer(file.read(), np.uint8)
    img = cv2.imdecode(npimg, cv2.IMREAD_COLOR)

    if img is None:
        return jsonify({'error': 'Invalid image file'}), 400

    # Resize and normalize to match how the model was trained
    img = cv2.resize(img, (256, 256))
    img = img.reshape((1, 256, 256, 3)) / 255.0

    # Model output is a number between 0 and 1: closer to 1 = Dog, closer to 0 = Cat
    prediction = model.predict(img)[0][0]

    if prediction > 0.5:
        result = "Dog 🐶"
        confidence = prediction
    else:
        result = "Cat 🐱"
        confidence = 1 - prediction

    # Sending confidence as a raw fraction (e.g. 0.9896). The frontend multiplies by 100.
    return jsonify({'result': result, 'confidence': round(float(confidence), 4)})


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug_mode = os.environ.get('FLASK_ENV') != 'production'
    app.run(debug=debug_mode, host='0.0.0.0', port=port)