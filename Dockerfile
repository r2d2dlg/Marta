
# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Define environment variables (can be overridden)
ENV FLASK_APP=marta_core/crm_api.py
ENV FLASK_RUN_HOST=0.0.0.0

# Run the command to start the Flask server
CMD ["flask", "run"]
