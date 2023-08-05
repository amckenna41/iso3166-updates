# Use the official Python image.
FROM python:3.8

# Allow statements and log messages to immediately appear in the logs
ENV PYTHONUNBUFFERED True

# Adding trusting keys to apt for repositories
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -

# Adding Google Chrome to the repositories
RUN sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'

# Updating apt to see
RUN apt-get -y update

# Install Google Chrome
RUN apt-get install -y google-chrome-stable

# Installing Unzip
RUN apt-get install -yqq unzip

# Download the latest release of Chrome Driver
RUN wget -O /tmp/chromedriver.zip http://chromedriver.storage.googleapis.com/`curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE`/chromedriver_linux64.zip

# Unzip the Chrome Driver into /usr/lib/bin directory
RUN unzip /tmp/chromedriver.zip chromedriver -d /usr/lib/bin/

# Set display port as an environment variable
ENV DISPLAY=:99

# copy app data and set working directory
COPY . /app
WORKDIR /app

# upgrade pip package manager
RUN pip install --upgrade pip

# install all required Python dependancies
RUN pip install -r requirements.txt

# execute gunicorn webserver and run main app using one worker process and 8 threads
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 check_for_updates:app