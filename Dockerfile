# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /usr/src/app

# Copy the current directory contents
COPY . ./

# Install any needed packages specified in requirements.txt
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Make port 8000 available to the world outside this container
EXPOSE 8002

# Run app.py when the container launches
CMD ["gunicorn", "--config", "/usr/src/app/ws/gunicorn_config.py", "--worker-class", "eventlet", "-w", "1", "app:app_instance", "-b", "0.0.0.0:8002"]