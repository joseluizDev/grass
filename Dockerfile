# Use an official Alpine Linux image
FROM alpine:3.19

# Install required packages: Python, Chromium, and pip
RUN apk add --update --no-cache python3 py3-pip chromium chromium-chromedriver unzip && \
    ln -sf python3 /usr/bin/python

# Set working directory
WORKDIR /usr/src/app

# Copy application code to container
COPY src .

# Install Python dependencies from requirements.txt
RUN pip install --no-cache-dir -r ./requirements.txt --break-system-packages

# Set environment variables (example values; change as needed)
ENV GRASS_USER=lui_zzzz@hotmail.com
ENV GRASS_PASS=Burro12@
ENV ALLOW_DEBUG=False

# Expose port 80 to access the app
EXPOSE 80

# Run the application
CMD ["python", "./main.py"]
