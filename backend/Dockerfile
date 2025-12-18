FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    git \
    libmagic1 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Skip spacy for minimal test

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p data uploads temp

# Copy startup script and make it executable (before user switch)
COPY start.sh .
RUN chmod +x start.sh

# Create non-root user for security
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Health check disabled for debugging
# HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
#     CMD curl -f http://localhost:8000/health || exit 1

# Set environment variables for debugging
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Run the application using startup script
CMD ["./start.sh"]