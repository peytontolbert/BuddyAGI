# Use a base image with Python and a desktop environment
FROM python:3.8-slim

# Install dependencies for Chrome, ChromeDriver, and a VNC server
RUN apt-get update && apt-get install -y \
    wget \
    xvfb \
    x11vnc \
    fluxbox \
    google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

# Set display environment variable
ENV DISPLAY=:99

# Install ChromeDriver
RUN wget https://chromedriver.storage.googleapis.com/2.41/chromedriver_linux64.zip \
    && unzip chromedriver_linux64.zip -d /usr/local/bin/ \
    && rm chromedriver_linux64.zip

# Set up VNC server (set a password for security)
RUN x11vnc -storepasswd yourVNCpassword /etc/x11vnc.pass

# Copy your WebBrowserAgent's Python script into the container
COPY . /app
WORKDIR /app

# Install Python dependencies (like selenium)
RUN pip install -r requirements.txt

# Expose VNC port
EXPOSE 5900

# Start Xvfb, Fluxbox, and x11vnc, then run your Python script
CMD Xvfb :99 -screen 0 1024x768x16 & \
    fluxbox & \
    x11vnc -display :99 -nopw -listen localhost -xkb -forever & \
    python main.py