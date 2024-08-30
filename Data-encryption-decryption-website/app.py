from flask import Flask, request, render_template, send_from_directory, flash, redirect, url_for
from cryptography.fernet import Fernet
import os

app = Flask(__name__)
app.secret_key = 'supersecretkey'  
UPLOAD_FOLDER = 'uploads'
KEY_FILE = 'Secret.key'

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def generate_key():
    key = Fernet.generate_key()
    with open(KEY_FILE, "wb") as key_file:
        key_file.write(key)
    return key

def load_key():
    return open(KEY_FILE, "rb").read()

def encrypt_file(file_path, key):
    f = Fernet(key)
    with open(file_path, "rb") as file:
        file_data = file.read()
    encrypted_data = f.encrypt(file_data)
    with open(file_path, "wb") as file:
        file.write(encrypted_data)

def decrypt_file(file_path, key):
    f = Fernet(key)
    with open(file_path, "rb") as file:
        encrypted_data = file.read()
    decrypted_data = f.decrypt(encrypted_data)
    with open(file_path, "wb") as file:
        file.write(decrypted_data)

@app.route('/')
def index():
    # Delete the key file if it exists
    if os.path.exists(KEY_FILE):
        os.remove(KEY_FILE)
    return render_template('index.html')

@app.route('/encrypt', methods=['POST'])
def encrypt():
    if 'file' not in request.files:
        flash('No file part', 'error')
        return redirect(url_for('index'))
    file = request.files['file']
    if file.filename == '':
        flash('No selected file', 'error')
        return redirect(url_for('index'))
    if file:
        key = generate_key()
        filename = file.filename
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)
        encrypt_file(file_path, key)
        flash('File encrypted successfully!', 'success')
        return render_template('index.html', encrypted_filepath=filename, key=key.decode())

@app.route('/decrypt', methods=['POST'])
def decrypt():
    if 'file' not in request.files or 'key' not in request.form:
        flash('Missing file or key', 'error')
        return redirect(url_for('index'))
    file = request.files['file']
    key = request.form['key'].encode()
    if file.filename == '':
        flash('No selected file', 'error')
        return redirect(url_for('index'))
    if file:
        filename = file.filename
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)
        try:
            decrypt_file(file_path, key)
            flash('File decrypted successfully!', 'success')
            return render_template('index.html', decrypted_filepath=filename)
        except Exception as e:
            flash('Invalid key or file', 'error')
            return redirect(url_for('index'))

@app.route('/uploads/<filename>')
def download_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

if __name__ == '__main__':
    app.run(debug=True)
