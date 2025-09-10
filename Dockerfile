# Use the official Python image.
FROM python:3.11-slim

# Set the working directory in the container.
WORKDIR /app

# Copy the Python script into the container.
COPY main.py .

# Expose the port the server listens on.
EXPOSE 7300

# Command to run the Python script.
CMD ["python", "main.py"]
