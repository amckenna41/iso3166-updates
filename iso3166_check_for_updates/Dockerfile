FROM python:3.10-slim

#install dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget unzip curl gnupg ca-certificates \
    fonts-liberation libnss3 libxss1 libasound2 libatk-bridge2.0-0 libcups2 libgtk-3-0 \
    xdg-utils xvfb && \
    rm -rf /var/lib/apt/lists/*

#download and install specific version of Chrome (124.0.6367.207)
RUN wget https://dl.google.com/linux/chrome/deb/pool/main/g/google-chrome-stable/google-chrome-stable_124.0.6367.207-1_amd64.deb && \
    apt-get update && \
    apt-get install -y ./google-chrome-stable_124.0.6367.207-1_amd64.deb && \
    rm google-chrome-stable_124.0.6367.207-1_amd64.deb

#install matching ChromeDriver
RUN set -ex && \
    DRIVER_VERSION=124.0.6367.207 && \
    wget -O /tmp/chromedriver.zip "https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/${DRIVER_VERSION}/linux64/chromedriver-linux64.zip" && \
    unzip /tmp/chromedriver.zip -d /tmp/ && \
    mv /tmp/chromedriver-linux64/chromedriver /usr/local/bin/chromedriver && \
    chmod +x /usr/local/bin/chromedriver && \
    rm -rf /tmp/chromedriver.zip /tmp/chromedriver-linux64

#copy requirements.txt to working directory
COPY requirements.txt .

#install Python dependencies
RUN pip install --no-cache-dir selenium -r requirements.txt

#set headless display variable
ENV DISPLAY=:99

#set working directory of container
COPY . /app
WORKDIR /app

#run main file on container start
CMD ["python3", "check_for_updates.py"]

#export port 8080 to html traffic
EXPOSE 8080