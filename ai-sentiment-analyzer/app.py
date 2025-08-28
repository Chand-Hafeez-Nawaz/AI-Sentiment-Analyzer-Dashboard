import os
import datetime
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv
from pymongo import MongoClient
from bson import ObjectId

from models.sentiment import get_sentiment_pipeline, analyze_texts

load_dotenv()

def create_app():
    app = Flask(__name__)
    app.config["MONGO_URI"] = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    app.config["MONGO_DB"] = os.getenv("MONGO_DB", "sentiment_db")
    app.config["COLLECTION"] = os.getenv("MONGO_COLLECTION", "analyses")
    app.config["HF_MODEL_NAME"] = os.getenv("HF_MODEL_NAME", "distilbert-base-uncased-finetuned-sst-2-english")

    client = MongoClient(app.config["MONGO_URI"])
    db = client[app.config["MONGO_DB"]]
    collection = db[app.config["COLLECTION"]]

    # Ensure index on created_at for faster timelines
    collection.create_index("created_at")

    # Initialize model pipeline once
    nlp = get_sentiment_pipeline(app.config["HF_MODEL_NAME"])

    @app.route("/", methods=["GET"])
    def home():
        return render_template("dashboard.html")

    @app.route("/api/analyze", methods=["POST"])
    def analyze():
        payload = request.get_json(silent=True) or {}
        texts = payload.get("texts")
        source = payload.get("source", "api")
        if texts is None:
            text = payload.get("text")
            if text is None:
                return jsonify({"error": "Provide 'text' or 'texts' in JSON body"}), 400
            texts = [text]

        results = analyze_texts(nlp, texts)
        docs = []
        now = datetime.datetime.utcnow()
        for t, r in zip(texts, results):
            doc = {
                "text": t,
                "label": r["label"],
                "score": float(r["score"]),
                "created_at": now,
                "source": source,
            }
            docs.append(doc)

        if docs:
            collection.insert_many(docs)

        # Convert ObjectIds and datetimes to strings for JSON response
        def _serialize(doc):
            d = dict(doc)
            if "_id" in d:
                d["_id"] = str(d["_id"])
            if isinstance(d.get("created_at"), datetime.datetime):
                d["created_at"] = d["created_at"].isoformat() + "Z"
            return d

        return jsonify({"results": [_serialize(d) for d in docs]})

    @app.route("/api/stats", methods=["GET"])
    def stats():
        # Aggregate sentiment counts and timeline
        pipeline = [
            {"$group": {"_id": "$label", "count": {"$sum": 1}}}
        ]
        counts = list(collection.aggregate(pipeline))

        # Timeline by day
        timeline_pipeline = [
            {"$group": {
                "_id": {
                    "y": {"$year": "$created_at"},
                    "m": {"$month": "$created_at"},
                    "d": {"$dayOfMonth": "$created_at"}
                },
                "pos": {"$sum": {"$cond": [{"$eq": ["$label", "POSITIVE"]}, 1, 0]}},
                "neg": {"$sum": {"$cond": [{"$eq": ["$label", "NEGATIVE"]}, 1, 0]}},
                "neu": {"$sum": {"$cond": [{"$eq": ["$label", "NEUTRAL"]}, 1, 0]}},
                "total": {"$sum": 1}
            }},
            {"$sort": {"_id": 1}}
        ]

        timeline_raw = list(collection.aggregate(timeline_pipeline))
        timeline = []
        for row in timeline_raw:
            dt = datetime.date(row["_id"]["y"], row["_id"]["m"], row["_id"]["d"]).isoformat()
            timeline.append({
                "date": dt,
                "positive": row.get("pos", 0),
                "negative": row.get("neg", 0),
                "neutral": row.get("neu", 0),
                "total": row.get("total", 0)
            })

        return jsonify({
            "counts": counts,
            "timeline": timeline
        })

    @app.route("/api/recent", methods=["GET"])
    def recent():
        limit = int(request.args.get("limit", 20))
        docs = list(collection.find().sort("created_at", -1).limit(limit))
        out = []
        for d in docs:
            out.append({
                "_id": str(d["_id"]),
                "text": d["text"],
                "label": d["label"],
                "score": float(d["score"]),
                "created_at": d["created_at"].isoformat() + "Z",
                "source": d.get("source", "api")
            })
        return jsonify({"items": out})

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)), debug=True)
