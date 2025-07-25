# Use an official Python runtime as a parent image
FROM python:3.10-slim-buster

# Set the working directory inside the container
WORKDIR /app

# Copy your entire project directory into the container at /app
COPY . /app

# Install Python dependencies from requirements.txt
# Ensure requirements.txt exists and lists all your dependencies (chainlit, openai, python-dotenv, etc.)
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port that Chainlit runs on
EXPOSE 8000

# Define the command to run your Chainlit app
# Replace 'main.py' with the actual name of your Chainlit application file if it's different.
CMD ["chainlit", "run", "main.py", "--host", "0.0.0.0", "--port", "8000"]