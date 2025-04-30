FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install dependencies
RUN apt-get update && apt-get install -y \
    curl \
    pandoc \
    git \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# Install Quarto CLI
RUN curl -L https://quarto.org/download/latest/quarto-linux-amd64.deb -o quarto.deb \
    && apt-get update && apt-get install -y ./quarto.deb \
    && rm quarto.deb

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the code
COPY . .

# Environment & Port for Render
ENV PORT=8080
EXPOSE 8080

# Start FastAPI with Gunicorn
CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "app:app", "--bind", "0.0.0.0:8080", "--timeout", "300"]


