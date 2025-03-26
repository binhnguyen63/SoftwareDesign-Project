# Use an official Python runtime as a parent image
FROM python:3.11

# Set the working directory in the container
WORKDIR /app

# Copy project files into the container
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the .env file
COPY .env /app/.env

# # Use the PORT from the .env file (Docker itself does not parse .env automatically)
# ARG PORT
# ENV PORT=$PORT

# # Expose the port dynamically (for documentation, not mandatory)
# EXPOSE $PORT

# Run the app dynamically with the correct port
CMD ["sh", "-c", "python app.py"]
