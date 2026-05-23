import joblib
import numpy as np
import re
from url_utils import tokenize_url, normalize_url
from urllib.parse import urlparse
from scipy.sparse import hstack
from sklearn.metrics.pairwise import cosine_similarity


BASE = r"D:\sneha\smartshield_new"


# -----------------------------
# NORMALIZE URL
# -----------------------------
def normalize_url(url):
    url = str(url).lower()
    url = url.replace("http://", "").replace("https://", "")
    url = url.replace("www.", "")
    return url.strip("/")


# -----------------------------
# TOKENIZER
# -----------------------------
def tokenize_url(url):
    url = normalize_url(url)
    tokens = re.split(r"[./?=&]+", url)

    final_tokens = []
    for t in tokens:
        final_tokens.append(t)
        if "-" in t:
            final_tokens.extend(t.split("-"))

    return [x for x in final_tokens if len(x) > 2]


# -----------------------------
# STRUCTURAL FEATURES
# -----------------------------
def get_domain_feature(url):
    url = normalize_url(url)
    domain = url.split("/")[0]
    return len(domain)


def extract_url_features(url):
    try:
        url = normalize_url(url)

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
            get_domain_feature(url)   # ✅ ADD THIS
        ]

    except:
        return [0,0,0,0,0,0,0,0]

# -----------------------------
# LOAD MODEL
# -----------------------------
print("Loading model...")

model = joblib.load(BASE + "/models/url_model.pkl")
vectorizer = joblib.load(BASE + "/models/url_vectorizer.pkl")
phish_centroid = joblib.load(BASE + "/models/phish_centroid.pkl")
legit_centroid = joblib.load(BASE + "/models/legit_centroid.pkl")

print("Model loaded successfully!")


# -----------------------------
# PREDICT (IMPROVED)
# -----------------------------
def predict(url):

    url = normalize_url(url)

    # TF-IDF
    vec = vectorizer.transform([url])

    # STRUCT FEATURES
    url_feat = np.array([extract_url_features(url)])

    # COSINE
    sim_phish = cosine_similarity(vec, phish_centroid)
    sim_legit = cosine_similarity(vec, legit_centroid)

    cosine_feat = np.hstack([sim_phish, sim_legit])

    # FINAL VECTOR
    final_vec = hstack([vec, url_feat, cosine_feat])

    probs = model.predict_proba(final_vec)[0]

    legit_prob = probs[0]
    phish_prob = probs[1]

    # -----------------------------
    # 🔥 IMPROVED CONFIDENCE
    # -----------------------------
    raw_conf = max(legit_prob, phish_prob)

    # 🔥 confidence scaling (power boost)
    confidence = (raw_conf ** 0.5)   # sqrt scaling (boosts values)

    

    # clamp
    confidence =max(0.5, min(confidence, 0.95))

    # -----------------------------
    # 🔥 SMART RULE BOOST
    # -----------------------------
    suspicious_words = ["login", "verify", "secure", "update", "bank", "free", "win"]

    if any(word in url for word in suspicious_words):
        phish_prob += 0.05
    # -----------------------------
# 🔥 ADVANCED RULE ENGINE
# -----------------------------
    suspicious_keywords = [
        "login", "verify", "secure", "account",
        "update", "bank", "paypal", "free",
        "win", "bonus", "gift", "claim"
    ]

    score_boost = 0

    # keyword detection
    for word in suspicious_keywords:
        if word in url:
            score_boost += 0.08

    # too many hyphens
    if url.count("-") >= 2:
        score_boost += 0.1

    # too many digits
    if sum(c.isdigit() for c in url) > 3:
        score_boost += 0.1

    # long URL
    if len(url) > 40:
        score_boost += 0.05

    # suspicious TLDs
    if any(url.endswith(tld) for tld in [".xyz", ".tk", ".ml", ".ga", ".cf"]):
        score_boost += 0.15

    # apply boost
    phish_prob += score_boost

    # clamp values
    phish_prob = min(phish_prob, 1.0)
    legit_prob = 1 - phish_prob
    # -----------------------------
    # FINAL DECISION
    # -----------------------------
    if phish_prob > 0.65:
        return "PHISHING", round(confidence, 3)

    elif legit_prob > 0.75:
        return "SAFE", round(confidence, 3)

    else:
        return "SUSPICIOUS", round(confidence, 3)


# -----------------------------
# CLI LOOP
# -----------------------------
while True:
    try:
        url = input("\nEnter URL: ")
        label, score = predict(url)
        print("Result:", label, "Confidence:", score)

    except KeyboardInterrupt:
        print("\nExiting...")
        break