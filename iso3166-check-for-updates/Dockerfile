# Use the official Python image.
FROM python:3.9

# Allow statements and log messages to immediately appear in the logs
ENV PYTHONUNBUFFERED True

# Adding trusting keys to apt for repositories
RUN curl -sS -o - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -

# Update list of available packages
RUN apt-get update -y

# Install latest release of Chrome WebDriver, unzip and create symlink to executable
RUN CHROMEDRIVER_VERSION=`curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE` && \
    mkdir -p /opt/chromedriver-$CHROMEDRIVER_VERSION && \
    curl -sS -o /tmp/chromedriver_linux64.zip http://chromedriver.storage.googleapis.com/$CHROMEDRIVER_VERSION/chromedriver_linux64.zip && \
    unzip -qq /tmp/chromedriver_linux64.zip -d /opt/chromedriver-$CHROMEDRIVER_VERSION && \
    rm /tmp/chromedriver_linux64.zip && \
    chmod +x /opt/chromedriver-$CHROMEDRIVER_VERSION/chromedriver && \
    ln -fs /opt/chromedriver-$CHROMEDRIVER_VERSION/chromedriver /usr/local/bin/chromedriver

# Check available versions here: https://www.ubuntuupdates.org/package/google_chrome/stable/main/base/google-chrome-stable
# Download latest stable release of Google Chrome
ARG CHROME_VERSION="114.0.5735.198-1"
RUN wget --no-verbose -O /tmp/chrome.deb https://dl.google.com/linux/chrome/deb/pool/main/g/google-chrome-stable/google-chrome-stable_${CHROME_VERSION}_amd64.deb \
  && apt install -y /tmp/chrome.deb \
  && rm /tmp/chrome.deb

# Set display port as an environment variable
ENV DISPLAY=:99

# Copy app data and set working directory
COPY . /app
WORKDIR /app

# Upgrade pip package manager
RUN pip install --upgrade pip

# Install all required Python dependancies
RUN pip install -r requirements.txt

# Execute gunicorn webserver and run main app using one worker process and 8 threads
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 check_for_updates:app

#List of Chrome and Chromedriver versions: https://googlechromelabs.github.io/chrome-for-testing/known-good-versions-with-downloads.json
#List of google-chrome-stable versions: https://www.ubuntuupdates.org/package/google_chrome/stable/main/base/google-chrome-stable
#Gist for installing chrome & chromedriver: https://gist.github.com/varyonic/dea40abcf3dd891d204ef235c6e8dd79
#Common Chromedriver issue: https://stackoverflow.com/questions/69024209/chromedriver-executable-path-not-found-in-docker-container