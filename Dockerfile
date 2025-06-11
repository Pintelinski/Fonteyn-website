FROM python:3.13-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create static directory
RUN mkdir -p /app/static

# Copy application files
COPY app.py config.py hotel.ini hotel_api.yml ./
COPY templates/ ./templates/
COPY static/ ./static/
COPY api.py ./

# Set environment variables
ENV FLASK_APP=app.py
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Expose the port
EXPOSE 8080

# Start the application
CMD ["python", "app.py"]