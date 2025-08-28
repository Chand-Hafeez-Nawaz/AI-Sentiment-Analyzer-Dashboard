# Installation Guide

## Prerequisites
- Python 3.10+
- MongoDB running locally or via cloud (MongoDB Atlas)
- Git

## Steps (Local Setup)
```bash
git clone https:/Chand-Hafeez-Nawaz/github.com//ai-sentiment-analyzer.git
cd ai-sentiment-analyzer

# Create virtual environment
python -m venv .venv

# Activate (Windows PowerShell)
.venv\Scripts\Activate.ps1

# Activate (Linux/Mac)
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy env file
cp .env.example .env

# Start app
python app.py
```

## Docker Setup
```bash
docker compose up --build
```
