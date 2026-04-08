🧠 Information Extraction using NLP (SVM + Regex)

A hybrid Information Extraction (IE) system that combines Regular Expressions (Regex) and a Support Vector Machine (SVM) model to extract structured data from unstructured text.

🚀 Features
🔍 Extracts entities from raw text
⚡ Fast pattern matching using Regex
🧠 Machine learning-based extraction using SVM
🔗 Hybrid pipeline (Rule-based + ML)
📄 Easy to extend and customize
🛠️ Tech Stack
Language: Python
Techniques: NLP, Regex, SVM

```bash
.
├── app.py                  # Main application (Hugging Face / Flask app)
├── requirements.txt        # Dependencies

├── svm_ner_model.pkl       # Trained SVM model
├── vectorizer.pkl          # Feature vectorizer (TF-IDF / CountVectorizer)

├── templates/              # HTML templates
│   └── index.html

├── static/                 # Static assets
│   ├── style.css
│   └── script.js

├── Dockerfile              # Deployment configuration (Hugging Face Spaces)
├── .gitattributes          # Git configuration

└── README.md               # Project documentation

⚙️ How It Works
Preprocessing
Clean and tokenize text
Regex Extraction
Extract structured patterns (dates, emails, phone numbers)
SVM Model
Classify and extract contextual entities
Final Output
Combine results into structured format

## 📸 Output Screenshot

<p align="center">
  <img src="output.png" width="700"/>
</p>

<p align="center">
  <img src="output1.png" width="700"/>
</p>

