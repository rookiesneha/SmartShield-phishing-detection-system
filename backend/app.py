from flask import Flask, request, jsonify
from flask_cors import CORS

import joblib
import numpy as np
import re
import sys
import os

from scipy.sparse import hstack
from sklearn.metrics.pairwise import cosine_similarity
from urllib.parse import urlparse

# -----------------------------
# PATH FIX
# -----------------------------

sys.path.append(
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..")
    )
)

from scripts.url_utils import tokenize_url, normalize_url

# -----------------------------
# APP INIT
# -----------------------------

app = Flask(__name__)
CORS(app)

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

print("Loading models...")

url_model = joblib.load(BASE + "/models/url_model.pkl")
vectorizer = joblib.load(BASE + "/models/url_vectorizer.pkl")
phish_centroid = joblib.load(BASE + "/models/phish_centroid.pkl")
legit_centroid = joblib.load(BASE + "/models/legit_centroid.pkl")

html_model = joblib.load(BASE + "/models/html_model.pkl")
html_vectorizer = joblib.load(BASE + "/models/html_vectorizer.pkl")

print("Models loaded successfully!")

# -----------------------------
# URL FEATURES
# -----------------------------

def extract_url_features(url):

    try:

        url = normalize_url(str(url))

        parsed = urlparse("http://" + url)

        host = parsed.netloc
        path = parsed.path

        return [

            len(url),
            url.count('-'),
            url.count('.'),
            url.count('/'),
            sum(c.isdigit() for c in url),
            len(host),
            len(path),
            len(host)

        ]

    except:

        return [0]*8


# -----------------------------
# URL PREDICTION
# -----------------------------

def predict_url(url):

    url = normalize_url(url)

    vec = vectorizer.transform([url])

    sim_phish = cosine_similarity(vec, phish_centroid)
    sim_legit = cosine_similarity(vec, legit_centroid)

    cosine_feat = np.hstack([sim_phish, sim_legit])
    url_feat = np.array([extract_url_features(url)])

    final_vec = hstack([vec, url_feat, cosine_feat])

    probs = url_model.predict_proba(final_vec)[0]

    legit_prob = probs[0]
    phish_prob = probs[1]

    if phish_prob > 0.65:

        label = "PHISHING"

    elif legit_prob > 0.75:

        label = "SAFE"

    else:

        label = "SUSPICIOUS"

    confidence = max(legit_prob, phish_prob)
    confidence = max(0.6, min(confidence, 0.95))

    return label, float(confidence)


# -----------------------------
# URL API
# -----------------------------

@app.route("/predict", methods=["POST"])
def predict():

    data = request.get_json()

    url = data.get("url", "")

    print("URL RECEIVED:", url)

    label, confidence = predict_url(url)
    print("\n------ URL CHECK ------")
    print("URL:", url)
    print("Result:", label)
    print("Confidence:", round(confidence,3))
    print("-----------------------")
    

    return jsonify({

        "result": label,
        "confidence": round(confidence, 3),
        "source": "URL"

    })


# -----------------------------
# HTML API
# -----------------------------

# -----------------------------
# HTML API
# -----------------------------

@app.route("/predict_html", methods=["POST"])
def predict_html():

    data = request.get_json()

    html = data.get("html", "")
    url = data.get("url", "")

    print("HTML RECEIVED FOR:", url)

    trusted = [

        "google.com",
        "youtube.com",
        "bing.com",
        "github.com",
        "chatgpt.com"

    ]

    try:

        # -----------------------------
        # TRUSTED SITE SHORTCUT
        # -----------------------------

        if any(t in url for t in trusted):

            label = "SAFE"
            confidence = 0.95

            print("HTML CALLED")
            print("\n------ HTML CHECK ------")
            print("URL:", url)
            print("Result:", label)
            print("Confidence:", confidence)
            print("------------------------")

            return jsonify({

                "result": label,
                "confidence": confidence,
                "source": "HTML"

            })

        # -----------------------------
        # CLEAN HTML
        # -----------------------------

        html = str(html)

        html = re.sub(
            r"<script.*?>.*?</script>",
            "",
            html,
            flags=re.DOTALL
        )

        html = re.sub(
            r"<style.*?>.*?</style>",
            "",
            html,
            flags=re.DOTALL
        )

        html = re.sub(
            r"<.*?>",
            " ",
            html
        )

        html = re.sub(
            r"[^a-zA-Z]",
            " ",
            html
        )

        html = html.lower()

        # -----------------------------
        # VECTORIZE
        # -----------------------------

        vector = html_vectorizer.transform([html])

        probs = html_model.predict_proba(vector)[0]

        legit_prob = probs[0]
        phish_prob = probs[1]

        if phish_prob > 0.85:

            label = "PHISHING"

        elif legit_prob > 0.75:

            label = "SAFE"

        else:

            label = "SUSPICIOUS"

        confidence = max(
            legit_prob,
            phish_prob
        )

        confidence = max(
            0.6,
            min(confidence, 0.95)
        )

        print("HTML CALLED ✅")
        print("\n------ HTML CHECK ------")
        print("URL:", url)
        print("Result:", label)
        print("Confidence:", round(confidence,3))
        print("------------------------")

        return jsonify({

            "result": label,
            "confidence": round(confidence, 3),
            "source": "HTML"

        })

    except Exception as e:

        print("HTML ERROR:", e)

        return jsonify({

            "result": "SAFE",
            "confidence": 0.6,
            "source": "HTML"

        })
# -----------------------------
# RUN
# -----------------------------
# -----------------------------
# FEEDBACK DATABASE
# -----------------------------

import sqlite3
from datetime import datetime

DB_PATH = BASE + "/feedback.db"

def init_feedback_db():

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""

        CREATE TABLE IF NOT EXISTS feedback (

            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT,
            prediction TEXT,
            feedback TEXT,
            timestamp TEXT

        )

    """)

    conn.commit()
    conn.close()

init_feedback_db()


# -----------------------------
# SAVE FEEDBACK API
# -----------------------------

@app.route("/save_feedback", methods=["POST"])
def save_feedback():

    data = request.get_json()

    url = data.get("url")
    prediction = data.get("prediction")
    feedback = data.get("feedback")

    timestamp = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    try:

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute("""

            INSERT INTO feedback
            (url, prediction, feedback, timestamp)

            VALUES (?, ?, ?, ?)

        """, (

            url,
            prediction,
            feedback,
            timestamp

        ))

        conn.commit()
        conn.close()

        print("FEEDBACK SAVED ✅")

        return jsonify({

            "status": "success"

        })

    except Exception as e:

        print("FEEDBACK ERROR:", e)

        return jsonify({

            "status": "error"

        })
if __name__ == "__main__":

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )