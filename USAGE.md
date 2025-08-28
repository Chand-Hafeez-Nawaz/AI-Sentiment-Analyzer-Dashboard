# Usage Guide

## Web Dashboard
- Visit http://localhost:5000
- Enter text(s) in the input box
- Click **Analyze**
- View recent results and sentiment chart

## API Endpoints

### Analyze Text(s)
`POST /api/analyze`
```json
{
  "texts": ["I love this product!", "This is terrible."],
  "source": "api"
}
```

Response:
```json
{
  "results": [
    {"text":"I love this product!","label":"POSITIVE","score":0.998},
    {"text":"This is terrible.","label":"NEGATIVE","score":0.997}
  ]
}
```

### Get Stats
`GET /api/stats` → sentiment counts + timeline

### Get Recent
`GET /api/recent?limit=20` → latest analyzed items
