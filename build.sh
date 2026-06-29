#!/usr/bin/env bash
# build.sh - Simple build for Render

set -o errexit
set -o pipefail

echo "========================================="
echo "Building AI Resume Analyzer..."
echo "========================================="

# Install dependencies
echo "📦 Installing Python packages..."
pip install --upgrade pip
pip install -r requirements.txt

# Verify installation
echo "✅ Verifying installation..."
python -c "from fastapi import FastAPI; print('FastAPI OK')"
python -c "from google import generativeai; print('Gemini SDK OK')"
python -c "from sqlalchemy import create_engine; print('SQLAlchemy OK')"

echo "========================================="
echo "✅ Build successful!"
echo "========================================="