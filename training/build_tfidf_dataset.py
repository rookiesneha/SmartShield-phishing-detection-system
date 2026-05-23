import pandas as pd
import os

# -----------------------------
# Paths
# -----------------------------

BASE = r"D:\sneha\smartshield_new\datasets"

text_path = os.path.join(BASE, "raw", "text_dataset")

fake_path = os.path.join(text_path, "Fake.csv")
true_path = os.path.join(text_path, "True.csv")
email_path = os.path.join(text_path, "Phishing_Email.csv")
sms_path = os.path.join(text_path, "SMSSpamCollection")

output_path = os.path.join(BASE, "processed", "tfidf_dataset.csv")


# -----------------------------
# Load Fake news dataset
# -----------------------------

print("Loading Fake.csv")

fake_df = pd.read_csv(fake_path)

fake_df["text"] = fake_df["title"] + " " + fake_df["text"]
fake_df = fake_df[["text"]]

fake_df["label"] = "phishing"


# -----------------------------
# Load True news dataset
# -----------------------------

print("Loading True.csv")

true_df = pd.read_csv(true_path)

true_df["text"] = true_df["title"] + " " + true_df["text"]
true_df = true_df[["text"]]

true_df["label"] = "legitimate"


# -----------------------------
# Load Phishing Email dataset
# -----------------------------

print("Loading Phishing_Email.csv")

email_df = pd.read_csv(email_path)

email_df = email_df.rename(columns={
    "Email Text": "text",
    "Email Type": "label"
})

email_df["label"] = email_df["label"].str.lower()

email_df["label"] = email_df["label"].replace({
    "phishing email": "phishing",
    "safe email": "legitimate"
})

email_df = email_df[["text", "label"]]


# -----------------------------
# Load SMS dataset
# -----------------------------

print("Loading SMS dataset")

sms_df = pd.read_csv(
    sms_path,
    sep="\t",
    header=None,
    names=["label", "text"]
)

sms_df["label"] = sms_df["label"].replace({
    "spam": "phishing",
    "ham": "legitimate"
})


# -----------------------------
# Combine datasets
# -----------------------------

print("Combining datasets")

combined = pd.concat([
    fake_df,
    true_df,
    email_df,
    sms_df
])


# -----------------------------
# Clean dataset
# -----------------------------

combined = combined.dropna()

combined["text"] = combined["text"].astype(str)

combined = combined.drop_duplicates()

print("Dataset size:", len(combined))


# -----------------------------
# Balance dataset
# -----------------------------

phish = combined[combined["label"] == "phishing"]
legit = combined[combined["label"] == "legitimate"]

min_size = min(len(phish), len(legit))

phish = phish.sample(min_size, random_state=42)
legit = legit.sample(min_size, random_state=42)

balanced = pd.concat([phish, legit])


# -----------------------------
# Save dataset
# -----------------------------

balanced.to_csv(output_path, index=False)

print("Saved dataset to:", output_path)

print("Final size:", len(balanced))