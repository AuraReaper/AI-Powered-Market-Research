#!/bin/bash

# Render startup script for Streamlit app

echo "🚀 Starting AI Market Researcher..."

# Ensure environment variables are loaded
export PYTHONPATH="${PYTHONPATH}:./src/marketresearcher"

# Create output directory if it doesn't exist
mkdir -p output/reports output/logs output/temp

# Start Streamlit
streamlit run app.py \
    --server.port=$PORT \
    --server.address=0.0.0.0 \
    --server.headless=true \
    --server.fileWatcherType=none \
    --browser.gatherUsageStats=false
