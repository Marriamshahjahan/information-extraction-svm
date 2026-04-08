from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from transformers import pipeline
from collections import defaultdict
import re
import warnings
import torch

warnings.filterwarnings("ignore")

torch.set_num_threads(1)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ner = load_model('svm_ner_model.plk')

@app.get("/")
def home():
    return {"message": "News Entity Extraction API running"}

def extract_entities(text):

    results = ner(text)
    entities = defaultdict(set)

    for r in results:

        label = r.get("entity_group", "").upper()
        word = r.get("word", "").replace("##", "").strip()

        if not word:
            continue

        if "PER" in label:
            entities["Person"].add(word)

        elif "ORG" in label:
            entities["Organization"].add(word)

        elif "LOC" in label:
            entities["Location"].add(word)

    # ─────────────────────
    # REGEX (EXTRA ENTITIES)
    # ─────────────────────

    # TEXT DATE (March 15, 2024)
    text_dates = re.findall(
        r'\b(?:January|February|March|April|May|June|July|August|'
        r'September|October|November|December)\s\d{1,2},?\s\d{4}\b',
        text
    )
    
    # SLASH DATE (15/03/2024 or 03/15/2024)
    slash_dates = re.findall(
        r'\b\d{1,2}/\d{1,2}/\d{2,4}\b',
        text
    )
    
    # DASH DATE (2024-03-15 or 15-03-2024)
    dash_dates = re.findall(
        r'\b\d{1,4}-\d{1,2}-\d{1,4}\b',
        text
    )
    
    # SHORT TEXT DATE (15 Mar 2024)
    short_dates = re.findall(
        r'\b\d{1,2}\s(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s\d{4}\b',
        text
    )
    
    for d in text_dates + slash_dates + dash_dates + short_dates:
        entities["Date"].add(d)

    # Money
    money = re.findall(
        r'[$₹€]\s?\d+(?:\.\d+)?\s?(?:million|billion|lakh|crore)?',
        text
    )
    for m in money:
        entities["Money"].add(m)

    # Time (12-hour + 24-hour formats)
    times = re.findall(
        r'\b(?:[01]?\d|2[0-3]):[0-5]\d(?:\s?[APap][Mm])?\b|\b(?:1[0-2]|0?[1-9])\s?[APap][Mm]\b',
        text
    )

    for t in times:
        entities["Time"].add(t)

    days = re.findall(
        r'\b(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)\b',
        text
    )
    
    for d in days:
        entities["Day"].add(d)
    
    #  Percentage
    perc = re.findall(r'\b\d+%', text)
    for p in perc:
        entities["Percentage"].add(p)
        
    output = ""

    for label, words in entities.items():
        if words:
            output += f"{label}:\n"
            for w in sorted(words):
                output += f"- {w}\n"
            output += "\n"

    return output if output else "No entities found."


@app.post("/extract")
def extract(data: dict):

    text = data.get("text", "").strip()

    if not text:
        return {"result": "Please provide some text."}

    result = extract_entities(text)

    return {"result": result}
