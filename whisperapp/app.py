from flask import Flask, render_template, send_from_directory, url_for
from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField
from werkzeug.utils import secure_filename
import os
from wtforms.validators import InputRequired
import subprocess
import torch

app = Flask(__name__)

app.config['SECRET_KEY'] = 'mysecretkey'
app.config['UPLOAD_FOLDER'] = 'static/files'

class MyForm(FlaskForm):
    file = FileField('File', validators=[InputRequired()])
    submit = SubmitField('Submit')

@app.route('/', methods=['GET', 'POST'])
def index():
    form = MyForm()
    transcript_file = None
    if form.validate_on_submit():
        file = form.file.data
        filename = secure_filename(file.filename).replace("\\", "")
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

        # Ensure the upload folder exists
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

        file.save(file_path)
        print(f'Processing {filename}')
        
        # Define the output directory
        output_dir = app.config['UPLOAD_FOLDER']
        
        # Determine if CUDA is available and set device accordingly
        device = 'cuda' if torch.cuda.is_available() else 'cpu'
        print(f'Using device: {device}')
        
        # Run the whisper command with appropriate device
        try:
            subprocess.run(['whisper', file_path, '--model', 'small', '--device', device, '--output_dir', output_dir, '--output_format', 'txt'], check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error occurred: {e}. Falling back to CPU.")
            subprocess.run(['whisper', file_path, '--model', 'small', '--device', 'cpu', '--output_dir', output_dir, '--output_format', 'txt'], check=True)
        
        # Define the transcript file name
        base_filename = os.path.splitext(filename)[0]  # remove the extension
        transcript_file = f'{base_filename}.txt'
        transcript_file_path = os.path.join(output_dir, transcript_file)
        
        # Debugging information
        print(f'Transcript file path: {transcript_file_path}')
        if os.path.exists(transcript_file_path):
            print(f'Transcript file created successfully: {transcript_file_path}')
        else:
            print('Transcript file not found')
            transcript_file = None
        
    return render_template('index.html', form=form, transcript_file=transcript_file)

@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    print(f'Requested download for file: {filename}')
    directory = os.path.abspath(app.config['UPLOAD_FOLDER'])
    print(f'Serving from directory: {directory}')
    return send_from_directory(directory, filename, as_attachment=True)

if __name__ == '__main__':
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0  # Disable caching of static files
    app.run(host='0.0.0.0', debug=True)
