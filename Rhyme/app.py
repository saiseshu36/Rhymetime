from __future__ import annotations

import json
import math
import re
from collections import Counter
from pathlib import Path
from typing import Any

from flask import Flask, jsonify, render_template, request

BASE_DIR = Path(__file__).resolve().parent
CORPUS_PATH = BASE_DIR / "rhymes.json"
app = Flask(__name__)


def load_rhymes() -> list[dict[str, Any]]:
    with CORPUS_PATH.open(encoding="utf-8") as file:
        return json.load(file)


RHYMES = load_rhymes()

# Human performances are configured here and stored locally for reliable playback.
HUMAN_VOCALS = {
    "wheels": {
        "filename": "wheels-human.mp3",
        "video": False,
        "label": "Human singing by Matt",
        "credit": "Matt / Dream English - educational use, © Dream English",
        "source": "https://www.dreamenglish.com/wheelsonthebus",
    },
    "twinkle": {
        "filename": "twinkle-human.ogg",
        "video": False,
        "label": "Human woman singing",
        "credit": "Dcoetzee - CC0 1.0",
        "source": "https://commons.wikimedia.org/wiki/File:Twinkle_Twinkle_Little_Star_-_sung_with_full_lyrics.ogg",
    },
    "mary": {
        "filename": "mary-human.ogg",
        "video": False,
        "label": "Human singing",
        "credit": "Celestianpower - Public domain",
        "source": "https://commons.wikimedia.org/wiki/File:Mary_Had_a_Little_Lamb.ogg",
    },
    "oldmacdonald": {
        "filename": "oldmacdonald-human.mp3",
        "video": False,
        "label": "Human singing",
        "credit": "Original recording © FreeABCSongs.com - personal use",
        "source": "https://www.freeabcsongs.com/oldmacdonald",
    },
    "rowboat": {
        "filename": "rowboat-human.mp3",
        "video": False,
        "label": "Human singing",
        "credit": "Original recording © FreeABCSongs.com - personal use",
        "source": "https://www.freeabcsongs.com/rowyourboat",
    },
    "itsybitsy": {
        "filename": "itsybitsy-human.mp3",
        "video": False,
        "label": "Human singing",
        "credit": "Original recording © FreeABCSongs.com - personal use",
        "source": "https://www.freeabcsongs.com/eencyweencyspider",
    },
}


def tokenize(text: str) -> list[str]:
    return re.findall(r"[a-z0-9']+", text.lower())


# Lightweight, local retrieval: TF-IDF scores match a child's button/query to
# rhyme titles, themes, and lyrics without sending anything to an external API.
DOCUMENTS = [
    " ".join([r["title"], r["theme"], r["description"], r["lyrics"]])
    for r in RHYMES
]
DOC_TOKENS = [tokenize(doc) for doc in DOCUMENTS]
DF = Counter(token for tokens in DOC_TOKENS for token in set(tokens))
N_DOCS = max(1, len(DOC_TOKENS))
IDF = {term: math.log(1 + N_DOCS / (1 + count)) for term, count in DF.items()}
VECTORS: list[dict[str, float]] = []
for tokens in DOC_TOKENS:
    counts = Counter(tokens)
    VECTORS.append({term: (1 + math.log(freq)) * IDF.get(term, 0.0) for term, freq in counts.items()})


def retrieve(query: str) -> dict[str, Any] | None:
    terms = set(tokenize(query))
    if not terms:
        return None
    query_vector = {term: IDF.get(term, 1.0) for term in terms}
    query_norm = math.sqrt(sum(value * value for value in query_vector.values())) or 1.0
    best_index, best_score = 0, -1.0
    for index, vector in enumerate(VECTORS):
        dot = sum(query_vector.get(term, 0.0) * weight for term, weight in vector.items())
        norm = math.sqrt(sum(weight * weight for weight in vector.values())) or 1.0
        score = dot / (query_norm * norm)
        if score > best_score:
            best_index, best_score = index, score
    return RHYMES[best_index]


def serialize_rhyme(rhyme: dict[str, Any]) -> dict[str, Any]:
    result = dict(rhyme)
    audio_dir = BASE_DIR / "static" / "audio"
    # Only use the instrumental files. Synthetic speech tracks sounded robotic
    # and should never be presented as human singing.
    candidates = [
        (f"{rhyme['id']}.mp3", False),
        (f"{rhyme['id']}.wav", False),
        (f"{rhyme['id']}.ogg", False),
        (f"{rhyme['id']}.m4a", False),
    ]
    human_vocal = HUMAN_VOCALS.get(rhyme["id"])
    if human_vocal:
        filename = human_vocal["filename"]
        version = (audio_dir / filename).stat().st_mtime_ns
        result["audio_url"] = f"/static/audio/{filename}?v={version}"
        result["vocal_track"] = True
        result["vocal_video"] = human_vocal.get("video", False)
        result["vocal_label"] = human_vocal.get("label", "Human singing")
        result["vocal_credit"] = human_vocal["credit"]
        result["vocal_source"] = human_vocal["source"]
        return result

    for filename, _ in candidates:
        if (audio_dir / filename).is_file():
            version = (audio_dir / filename).stat().st_mtime_ns
            result["audio_url"] = f"/static/audio/{filename}?v={version}"
            result["vocal_track"] = False
            break
    else:
        result["audio_url"] = None
        result["vocal_track"] = False
    return result

@app.get("/")
def home():
    return render_template("index.html", rhymes=RHYMES)


@app.get("/api/rhymes")
def list_rhymes():
    return jsonify([serialize_rhyme(rhyme) for rhyme in RHYMES])


@app.post("/api/play")
def play_rhyme():
    body = request.get_json(silent=True) or {}
    query = str(body.get("query", ""))[:200]
    rhyme = retrieve(query)
    if rhyme is None:
        return jsonify({"error": "Choose a rhyme to get started!"}), 400
    return jsonify(serialize_rhyme(rhyme))


if __name__ == "__main__":
    app.run(debug=True, port=5000)
