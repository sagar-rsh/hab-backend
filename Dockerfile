FROM python:3.10-slim

# Set environment variables to prevent Python from writing .pyc files
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory in the container
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy your application code into the container
COPY . .

# Expose the port the app runs on (for information only)
EXPOSE 8080

# Run Uvicorn server.
# It will listen on the port specified by the PORT environment variable,
# which Cloud Run provides automatically.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]