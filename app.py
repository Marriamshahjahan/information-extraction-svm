from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from collections import defaultdict
import warnings
import os
import re
import pickle

# ─────────────────────────────
# SETUP
# ─────────────────────────────
warnings.filterwarnings("ignore")

app = FastAPI()
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ─────────────────────────────
# CORS
# ─────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─────────────────────────────
# STATIC FILES
# ─────────────────────────────
static_path = os.path.join(BASE_DIR, "static")
if os.path.exists(static_path):
    app.mount("/static", StaticFiles(directory=static_path), name="static")

# ─────────────────────────────
# LOAD MODEL (SVM + VECTORIZER)
# ─────────────────────────────
try:
    with open(os.path.join(BASE_DIR, "svm_ner_model.pkl"), "rb") as f:
        model = pickle.load(f)

    with open(os.path.join(BASE_DIR, "vectorizer.pkl"), "rb") as f:
        vectorizer = pickle.load(f)

    print("Model and vectorizer loaded successfully")

except Exception as e:
    model = None
    vectorizer = None
    print("Model load failed:", e)

# ─────────────────────────────
# HOME ROUTE
# ─────────────────────────────
@app.get("/", response_class=HTMLResponse)
def home():
    file_path = os.path.join(BASE_DIR, "templates", "index.html")

    if not os.path.exists(file_path):
        return "<h2>index.html not found</h2>"

    with open(file_path, encoding="utf-8") as f:
        return f.read()

# ─────────────────────────────
# ENTITY EXTRACTION
# ─────────────────────────────
def extract_entities(text):

    entities = defaultdict(set)

    # ───── SVM MODEL ─────
    if model and vectorizer:
        try:
            # Transform text → numeric features
            X = vectorizer.transform([text])

            # Predict
            prediction = model.predict(X)

            # Store result
            for pred in prediction:
                entities["Prediction"].add(str(pred))

        except Exception as e:
            print("Model error:", e)

    # ───── REGEX ─────

    # Dates
    patterns = [
        r'\b\d{1,2}/\d{1,2}/\d{2,4}\b',
        r'\b\d{1,4}-\d{1,2}-\d{1,4}\b',
        r'\b\d{1,2}\s(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s\d{4}\b'
    ]
    for p in patterns:
        for match in re.findall(p, text):
            entities["Date"].add(match)

    # Money
    for m in re.findall(r'[$₹€]\s?\d+(?:,\d{3})*(?:\.\d+)?', text):
        entities["Money"].add(m)

    # Time
    for t in re.findall(r'\b(?:[01]?\d|2[0-3]):[0-5]\d\b', text):
        entities["Time"].add(t)

    # Percentage
    for p in re.findall(r'\b\d+(?:\.\d+)?%', text):
        entities["Percentage"].add(p)

    # Email
    for e in re.findall(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', text):
        entities["Email"].add(e)

    # ───── RETURN JSON ─────
    return {k: sorted(list(v)) for k, v in entities.items()}

# ─────────────────────────────
# API ROUTE
# ─────────────────────────────
@app.post("/extract")
def extract(data: dict):

    text = data.get("text", "").strip()

    if not text:
        return {"entities": {}}

    return {"entities": extract_entities(text)}
