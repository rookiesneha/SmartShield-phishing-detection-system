import pandas as pd
import os

# ----------------------------
# Paths
# ----------------------------

BASE = r"D:\sneha\smartshield_new\datasets"

raw_path = os.path.join(BASE, "raw", "url_dataset", "malicious_phish.csv")

output_path = os.path.join(BASE, "processed", "url_dataset.csv")


# ----------------------------
# Load dataset
# ----------------------------

print("Loading malicious URL dataset...")

df = pd.read_csv(raw_path)


# ----------------------------
# Keep only needed columns
# ----------------------------

df = df[["url", "type"]]


# ----------------------------
# Convert labels
# ----------------------------

df["label"] = df["type"].replace({
    "phishing": "phishing",
    "malware": "phishing",
    "defacement": "phishing",
    "benign": "legitimate"
})


df = df[["url", "label"]]


# ----------------------------
# Clean dataset
# ----------------------------

df = df.dropna()

df = df.drop_duplicates()

print("Dataset size:", len(df))


# ----------------------------
# Balance dataset
# ----------------------------

phish = df[df["label"] == "phishing"]
legit = df[df["label"] == "legitimate"]

min_size = min(len(phish), len(legit))

phish = phish.sample(min_size, random_state=42)
legit = legit.sample(min_size, random_state=42)

balanced = pd.concat([phish, legit])


# ----------------------------
# Save dataset
# ----------------------------

balanced.to_csv(output_path, index=False)

print("Saved dataset to:", output_path)

print("Final dataset size:", len(balanced))