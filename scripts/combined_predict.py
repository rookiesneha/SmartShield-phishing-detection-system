import joblib
import numpy as np
import re

# -----------------------------
# REQUIRED FOR MODEL LOADINGexit
# -----------------------------
def normalize_url(url):
    url = str(url).lower()
    url = url.replace("http://","").replace("https://","")
    url = url.replace("www.","")
    return url.strip("/")

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
# LOAD MODELS
# -----------------------------
BASE = r"D:\sneha\smartshield_new"

url_model = joblib.load(BASE + "/models/url_model.pkl")
url_vectorizer = joblib.load(BASE + "/models/url_vectorizer.pkl")
phish_centroid = joblib.load(BASE + "/models/phish_centroid.pkl")
legit_centroid = joblib.load(BASE + "/models/legit_centroid.pkl")

html_model = joblib.load(BASE + "/models/html_model.pkl")

print("All models loaded!")


# -----------------------------
# FINAL DECISION
# -----------------------------
def final_decision(url_label, html_label):
    
    if url_label == "PHISHING" or html_label == "PHISHING":
        return "🚨 PHISHING WEBSITE"

    elif url_label == "SUSPICIOUS" or html_label == "SUSPICIOUS":
        return "⚠ SUSPICIOUS WEBSITE"

    else:
        return "✅ SAFE WEBSITE"


# -----------------------------
# DEMO INPUT
# -----------------------------
while True:
    try:
        print("\nEnter URL result (SAFE / PHISHING / SUSPICIOUS):")
        url_label = input().strip()

        print("\nEnter HTML result (SAFE / PHISHING / SUSPICIOUS):")
        html_label = input().strip()

        final = final_decision(url_label, html_label)

        print("\nFINAL RESULT:", final)

    except KeyboardInterrupt:
        print("\nExiting...")
        break