# Use a slim Python base image
FROM python:3.11-slim

# Set working directory
WORKDIR /usr/src/app

# Copy and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose the port (optional, for documentation)
EXPOSE 80

# Use FastAPI's built‑in dev server
CMD ["fastapi", "dev", "main.py", "--host", "0.0.0.0", "--port", "80"]