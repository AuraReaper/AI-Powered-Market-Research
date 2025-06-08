FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies for enhanced error handling and PDF generation
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    git \
    unzip \
    # Core dependencies for PDF generation
    pandoc \
    texlive-latex-base \
    texlive-fonts-recommended \
    texlive-fonts-extra \
    texlive-latex-extra \
    # Dependencies for Playwright (PDF generation fallback)
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libgtk-3-0 \
    libgbm1 \
    libasound2 \
    # Dependencies for wkhtmltopdf (alternative PDF generation)
    wkhtmltopdf \
    xvfb \
    # Clean up
    && rm -rf /var/lib/apt/lists/*

# Install Quarto CLI
RUN curl -L https://quarto.org/download/latest/quarto-linux-amd64.deb -o quarto.deb \
    && apt-get update && apt-get install -y ./quarto.deb \
    && rm quarto.deb

# Install TinyTeX via official script
RUN wget -qO- "https://yihui.org/tinytex/install-unx.sh" | sh

# Add TinyTeX binaries to PATH manually
ENV PATH="/root/.TinyTeX/bin/x86_64-linux:$PATH"

# Install Node.js for Playwright (if needed)
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs

# Copy Python dependency files
COPY requirements.txt .
COPY pyproject.toml .

# Install Python dependencies with enhanced error handling support
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir \
        # Enhanced error handling dependencies
        playwright>=1.40.0 \
        # Additional FastAPI dependencies for better error responses
        pydantic>=2.0.0 \
        # Logging and monitoring
        python-json-logger>=2.0.0 \
        # Performance monitoring
        prometheus-client>=0.19.0

# Install Playwright browsers (for PDF generation fallback)
RUN playwright install chromium --with-deps

# Create necessary directories for enhanced error handling
RUN mkdir -p /app/outputs /app/logs /app/temp

# Copy the application code
COPY . .

# Set proper permissions for output directories
RUN chmod 755 /app/outputs /app/logs /app/temp

# Environment variables for enhanced error handling
ENV PORT=8080
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV OUTPUTS_DIR=/app/outputs
ENV LOGS_DIR=/app/logs
ENV TEMP_DIR=/app/temp
# Enhanced error handling configuration
ENV ERROR_HANDLING_ENABLED=true
ENV PDF_GENERATION_TIMEOUT=120
ENV MAX_COMPANY_NAME_LENGTH=100
# Playwright configuration
ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright

EXPOSE 8080

# Health check for better container monitoring
HEALTHCHECK --interval=30s --timeout=30s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Start FastAPI with Gunicorn and enhanced configuration
CMD ["gunicorn", \
     "-k", "uvicorn.workers.UvicornWorker", \
     "app:app", \
     "--bind", "0.0.0.0:8080", \
     "--timeout", "300", \
     "--worker-connections", "1000", \
     "--max-requests", "1000", \
     "--max-requests-jitter", "100", \
     "--access-logfile", "/app/logs/access.log", \
     "--error-logfile", "/app/logs/error.log", \
     "--log-level", "info"]
