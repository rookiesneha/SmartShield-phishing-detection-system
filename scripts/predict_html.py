import joblib
import pandas as pd

BASE = r"D:\sneha\smartshield_new"

print("Loading HTML model...")

model = joblib.load(BASE + "/models/html_model.pkl")
feature_names = joblib.load(BASE + "/models/html_features.pkl")

print("Model loaded!")


def predict_html(feature_values):
    # ✅ convert to DataFrame with correct feature names
    df = pd.DataFrame([feature_values], columns=feature_names)

    probs = model.predict_proba(df)[0]

    legit_prob = probs[0]
    phish_prob = probs[1]

    raw_conf = max(legit_prob, phish_prob)

    # ✅ smooth confidence
    confidence = raw_conf ** 0.5
    confidence = max(0.6, min(confidence, 0.95))
    phish_prob = phish_prob * 1.1
    phish_prob = min(phish_prob, 1.0)
    # ✅ decision logic
    if phish_prob > 0.6:
        return "PHISHING", round(confidence, 3)
    elif legit_prob > 0.75:
        return "SAFE", round(confidence, 3)
    else:
        return "SUSPICIOUS", round(confidence, 3)
    # 🔥 bias toward phishing (safer in security systems)
    

# -----------------------------
# MANUAL TEST LOOP
# -----------------------------
while True:
    try:
        print("\nEnter 20 feature values:")
        user_input = input()

        if user_input.strip() == "":
            print("Exiting...")
            break

        values = list(map(float, user_input.split()))

        if len(values) != 20:
            print("Enter exactly 20 values!")
            continue

        label, score = predict_html(values)

        print("Result:", label, "Confidence:", score)

    except KeyboardInterrupt:
        print("\nExiting...")
        break