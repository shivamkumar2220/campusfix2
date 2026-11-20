# Complaint classifier: machine learning model that reads a complaint and predicts its category
# (IT, Classroom, Maintenance, Lab Equipment).
# TF-IDF turns words into numbers, Logistic Regression learns which words mean which category.
# Train again after changing data/complaints.csv:  venv\Scripts\python.exe -m ai.classifier
import csv
from pathlib import Path

import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

FOLDER = Path(__file__).parent
DATA_FILE = FOLDER / "data" / "complaints.csv"
MODEL_FILE = FOLDER / "model.pkl"


# Read the training data: list of complaint texts and list of correct categories
def load_data():
    with open(DATA_FILE, encoding="utf-8") as file:
        rows = list(csv.DictReader(file))
    return [r["complaint"] for r in rows], [r["category"] for r in rows]


def new_model():
    return Pipeline([("tfidf", TfidfVectorizer()), ("classifier", LogisticRegression(max_iter=1000))])


# Train on all the data and save the model to model.pkl
def train():
    texts, categories = load_data()
    model = new_model().fit(texts, categories)
    joblib.dump(model, MODEL_FILE)
    return model


# Load the saved model (train it the first time)
model = joblib.load(MODEL_FILE) if MODEL_FILE.exists() else train()


def classify(text):
    return model.predict([text])[0]


if __name__ == "__main__":
    train()
    print("Model trained and saved to", MODEL_FILE)
