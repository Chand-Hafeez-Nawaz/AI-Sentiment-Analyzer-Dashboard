from transformers import pipeline

_supported_neutral_models = {
    # Add HF model ids here that output NEUTRAL (e.g., twitter-roberta-base-sentiment-latest)
    "cardiffnlp/twitter-roberta-base-sentiment-latest": True,
    "finiteautomata/bertweet-base-sentiment-analysis": True
}

def get_sentiment_pipeline(model_name: str = "distilbert-base-uncased-finetuned-sst-2-english"):
    """Return a cached HuggingFace sentiment-analysis pipeline."""
    task = "sentiment-analysis"
    if model_name in _supported_neutral_models:
        # These models already output POSITIVE/NEGATIVE/NEUTRAL labels
        return pipeline(task, model=model_name, tokenizer=model_name, top_k=None)
    else:
        # Classic binary SST-2 model
        return pipeline(task, model=model_name, tokenizer=model_name)

def analyze_texts(nlp, texts):
    """Analyze a list of texts and return standardized results.

    Ensures labels are in {POSITIVE, NEGATIVE, NEUTRAL} where possible.

    """
    outputs = nlp(texts)
    results = []
    for out in outputs:
        if isinstance(out, list):
            # Some pipelines return list per example; pick top
            out = sorted(out, key=lambda x: x.get('score', 0), reverse=True)[0]

        label = out["label"].upper()
        score = float(out["score"])

        # Normalize label to POSITIVE/NEGATIVE/NEUTRAL if needed
        if label not in {"POSITIVE", "NEGATIVE", "NEUTRAL"}:
            # Map binary to POSITIVE/NEGATIVE
            if "POS" in label or label.startswith("5") or label == "LABEL_1":
                label = "POSITIVE"
            elif "NEG" in label or label.startswith("1") or label == "LABEL_0":
                label = "NEGATIVE"
            else:
                label = "NEUTRAL"

        results.append({"label": label, "score": score})
    return results
