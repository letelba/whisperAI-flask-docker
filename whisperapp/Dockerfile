FROM ubuntu:20.04
ARG DEBIAN_FRONTEND=noninteractive

WORKDIR /whisperapp

# Install system dependencies
RUN apt-get -y update && apt-get install -y python3.9 \
    ffmpeg \
    python3-pip

# Copy requirements.txt and install Python dependencies
COPY requirements.txt requirements.txt
RUN pip3 install --no-cache-dir -r requirements.txt

# Install Whisper
RUN pip3 install git+https://github.com/openai/whisper.git

# Copy the rest of the application code
COPY . .

# Expose port 5000
EXPOSE 5000

# Command to run the Flask application
CMD [ "python3", "-m", "flask", "run", "--host=0.0.0.0"]
