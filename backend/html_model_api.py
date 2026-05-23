from flask import Flask, request, jsonify
import joblib
import re

app = Flask(__name__)

print("Loading model...")

model = joblib.load(
    r"D:\sneha\smartshield_new\models\html_model.pkl"
)

vectorizer = joblib.load(
    r"D:\sneha\smartshield_new\models\html_vectorizer.pkl"
)

print("Model loaded successfully!")

def clean_html(text):

    text = str(text)

    text = re.sub(
        r"<script.*?>.*?</script>",
        "",
        text,
        flags=re.DOTALL
    )

    text = re.sub(
        r"<style.*?>.*?</style>",
        "",
        text,
        flags=re.DOTALL
    )

    text = re.sub(r"<.*?>", " ", text)

    text = re.sub(r"[^a-zA-Z]", " ", text)

    return text.lower()


@app.route("/predict_html", methods=["POST"])
def predict_html():

    data = request.json

    html = data.get("html", "")

    cleaned = clean_html(html)

    vector = vectorizer.transform([cleaned])

    prediction = model.predict(vector)[0]

    probability = model.predict_proba(vector)[0]

    confidence = float(max(probability))

    return jsonify({

        "prediction": int(prediction),
        "confidence": confidence

    })


if __name__ == "__main__":

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )