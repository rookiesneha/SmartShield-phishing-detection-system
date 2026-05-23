import pandas as pd
import os
import re
import joblib
import numpy as np
from scripts.url_utils import tokenize_url, normalize_url
from urllib.parse import urlparse
from scipy.sparse import hstack
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report


BASE = r"D:\sneha\smartshield_new"

# ✅ YOUR CLEAN DATASET
data_path = r"D:\sneha\smartshield_new\datasets\raw\url_dataset\cleaned_dataset.csv"

model_dir = os.path.join(BASE, "models")
os.makedirs(model_dir, exist_ok=True)



# -----------------------------
# DOMAIN FEATURE (NEW)
# -----------------------------
def get_domain_feature(url):
    url = normalize_url(url)
    domain = url.split("/")[0]
    return len(domain)


# -----------------------------
# STRUCTURAL FEATURES
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
            get_domain_feature(url)   # NEW
        ]
    except:
        return [0]*8


# -----------------------------
# LOAD DATASET
# -----------------------------
print("Loading dataset...")
df = pd.read_csv(data_path)

print("Dataset size:", len(df))

df["label"] = df["status"]

df = df[df["label"].isin([0,1])]
df = df.dropna()
print("After cleaning:", len(df))

# -----------------------------
# BALANCE DATASET
# -----------------------------
print("Balancing dataset...")

phish = df[df["label"] == 1]
legit = df[df["label"] == 0]

min_size = min(len(phish), len(legit))

phish = phish.sample(min_size, random_state=42)
legit = legit.sample(min_size, random_state=42)

df = pd.concat([phish, legit])
df = df.sample(frac=1, random_state=42).reset_index(drop=True)

print("Final dataset:", len(df))


# -----------------------------
# SPLIT
# -----------------------------
train_df, test_df = train_test_split(
    df, test_size=0.2, random_state=42, stratify=df["label"]
)


# -----------------------------
# TF-IDF (FIXED)
# -----------------------------
print("Training TF-IDF...")

vectorizer = TfidfVectorizer(
    tokenizer=tokenize_url,
    max_features=5000,
    ngram_range=(1,1)
)

X_train = vectorizer.fit_transform(train_df["url"])
X_test = vectorizer.transform(test_df["url"])

y_train = train_df["label"].values
y_test = test_df["label"].values


# -----------------------------
# STRUCT FEATURES
# -----------------------------
train_url_features = np.array([extract_url_features(u) for u in train_df["url"]])
test_url_features = np.array([extract_url_features(u) for u in test_df["url"]])


# -----------------------------
# CENTROIDS
# -----------------------------
phish_centroid = np.asarray(X_train[y_train == 1].mean(axis=0))
legit_centroid = np.asarray(X_train[y_train == 0].mean(axis=0))


# -----------------------------
# COSINE FEATURES
# -----------------------------
train_sim_phish = cosine_similarity(X_train, phish_centroid)
train_sim_legit = cosine_similarity(X_train, legit_centroid)

test_sim_phish = cosine_similarity(X_test, phish_centroid)
test_sim_legit = cosine_similarity(X_test, legit_centroid)

train_cosine = np.hstack([train_sim_phish, train_sim_legit])
test_cosine = np.hstack([test_sim_phish, test_sim_legit])


# -----------------------------
# FINAL FEATURES
# -----------------------------
X_train = hstack([X_train, train_url_features, train_cosine])
X_test = hstack([X_test, test_url_features, test_cosine])


# -----------------------------
# TRAIN MODEL
# -----------------------------
print("Training model...")

model = RandomForestClassifier(
    n_estimators=200,
    n_jobs=-1,
    random_state=42
)

model.fit(X_train, y_train)


# -----------------------------
# EVALUATE
# -----------------------------
pred = model.predict(X_test)

print("Accuracy:", accuracy_score(y_test, pred))
print(confusion_matrix(y_test, pred))
print(classification_report(y_test, pred))


# -----------------------------
# SAVE
# -----------------------------
joblib.dump(model, os.path.join(model_dir,"url_model.pkl"))
joblib.dump(vectorizer, os.path.join(model_dir,"url_vectorizer.pkl"))
joblib.dump(phish_centroid, os.path.join(model_dir,"phish_centroid.pkl"))
joblib.dump(legit_centroid, os.path.join(model_dir,"legit_centroid.pkl"))

print("Model saved successfully!")