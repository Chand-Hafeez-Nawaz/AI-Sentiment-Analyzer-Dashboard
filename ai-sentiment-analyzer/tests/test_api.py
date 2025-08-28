import json
from app import create_app

def test_analyze_single(monkeypatch):
    app = create_app()
    client = app.test_client()

    # Mock Mongo insert to avoid needing a DB during test
    monkeypatch.setenv("MONGO_URI", "mongodb://localhost:27017")

    res = client.post("/api/analyze", json={"text": "I love this product!"})
    assert res.status_code == 200
    data = res.get_json()
    assert "results" in data
    assert data["results"][0]["label"] in {"POSITIVE", "NEGATIVE", "NEUTRAL"}
