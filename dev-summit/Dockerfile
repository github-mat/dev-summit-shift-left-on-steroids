FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY src/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./

# Start the Python application
CMD ["python", "app.py"]