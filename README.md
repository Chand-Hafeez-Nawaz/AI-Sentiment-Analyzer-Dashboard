# AI-Based Sentiment Analyzer

Analyze social media posts or product reviews to determine user sentiment (positive/negative/neutral), store results in MongoDB, and view a simple dashboard with charts.

## Stack
- **Python** (Flask)
- **Hugging Face Transformers** (default: `distilbert-base-uncased-finetuned-sst-2-english`)
- **MongoDB**
- **Chart.js** for visualization

## Quick Start

### 1) Dependencies
- Python 3.10+ recommended
- MongoDB running locally (or a cloud URI)

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2) Environment
Create a `.env` file (or use system env vars):

```
MONGO_URI=mongodb://localhost:27017
MONGO_DB=sentiment_db
MONGO_COLLECTION=analyses
# Optional: a 3-class model (POSITIVE/NEGATIVE/NEUTRAL) like:
# HF_MODEL_NAME=cardiffnlp/twitter-roberta-base-sentiment-latest
```

### 3) Run
```bash
python app.py
# open http://localhost:5000
```

### 4) API

**POST /api/analyze**

```json
{
  "texts": ["I love this!", "This is terrible."],
  "source": "api"
}
```

Response:
```json
{
  "results": [
    {"_id":"...","text":"I love this!","label":"POSITIVE","score":0.999,"created_at":"...Z","source":"api"},
    {"_id":"...","text":"This is terrible.","label":"NEGATIVE","score":0.998,"created_at":"...Z","source":"api"}
  ]
}
```

**GET /api/stats** → sentiment counts and daily timeline

**GET /api/recent?limit=20** → recent analyzed texts

## Docker (optional)

A simple `docker-compose.yml` is included to run the Flask app + MongoDB together.

```bash
docker compose up --build
# open http://localhost:5000
```

## Notes
- Default model is binary (positive/negative). To include neutral, set `HF_MODEL_NAME` to a 3-class model like `cardiffnlp/twitter-roberta-base-sentiment-latest`.
- GPU is optional; `torch` CPU will work but may be slower.
- This project stores each analysis record with `text`, `label`, `score`, `created_at`, and `source` in MongoDB.
