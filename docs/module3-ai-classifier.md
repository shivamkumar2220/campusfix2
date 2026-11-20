# Module 3 – AI Classifier

**Owner:** Member 3  **Files:** `ai/classifier.py`, `ai/evaluate.py`, `ai/data/complaints.csv`, `ai/model.pkl` (made automatically)

## What it does
Reads the complaint text (title + description) and predicts its **category**:
**IT**, **Classroom**, **Maintenance** or **Lab Equipment**.

Example: *"Projector broken – projector not turning on in class"* → **Classroom**

## Training data – `ai/data/complaints.csv`
About 200 example complaints, each with the correct category:
```
complaint,category
Wi-Fi is not working,IT
Printer is not printing,IT
...
```
More (and more varied) rows = better model.

## How the model works
```
"Wi-Fi is very slow"
        │
        ▼  TF-IDF  (words → numbers)
   [0.0, 0.61, 0.0, 0.45, 0.66, ...]     one number per word; rare, useful words get bigger numbers
        │
        ▼  Logistic Regression  (numbers → category)
   IT 0.91 · Classroom 0.03 · Maintenance 0.04 · Lab 0.02
        │
        ▼
       "IT"
```
- **TF-IDF** = Term Frequency × Inverse Document Frequency. A word that appears often in *this* complaint but rarely in others (like "printer") is important. Common words (like "is") count less.
- **Logistic Regression** learns which words point to which category.
- Both are joined in one scikit-learn **Pipeline**.

## Code in short
```python
def new_model():
    return Pipeline([("tfidf", TfidfVectorizer()), ("classifier", LogisticRegression(max_iter=1000))])

model = joblib.load(MODEL_FILE) if MODEL_FILE.exists() else train()   # train once, then reuse

def classify(text):
    return model.predict([text])[0]
```
`model.pkl` is the saved trained model. It is not on GitHub – it is created automatically the first time the server starts.

**Retrain after changing the CSV:**
`venv\Scripts\python.exe -m ai.classifier`

## Testing – `ai/evaluate.py`
Run: `venv\Scripts\python.exe -m ai.evaluate`

| Test | Result |
|------|--------|
| 5-fold cross validation | about **94.5 %** average |
| Train on 80 %, test on hidden 20 % | about **97.6 %** |

It also prints a **classification report** (precision / recall per category) and a **confusion matrix**.

## Known weakness (next module)
Spelling not in the data, like "wifi" (data says "Wi-Fi") or typos ("nnot"), can go to the wrong category. Fix: add more varied rows, or use character n-grams: `TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 4))`.

## Viva questions
| Question | Answer |
|----------|--------|
| Why TF-IDF? | Computers need numbers. TF-IDF turns text into numbers and gives useful words more weight. |
| Why Logistic Regression? | Simple, fast, works well on small text datasets, easy to explain. |
| What is cross validation? | Split the data into 5 parts; train on 4, test on 1; repeat 5 times; average. Gives a fair accuracy. |
| What is a confusion matrix? | A table of real vs predicted categories – shows which categories get mixed up. |
| Training 99 % but test 97 % – why? | The model has already seen the training data; test data is new. A small gap is normal. |
| What is model.pkl? | The trained model saved to a file so we don't retrain every time the server starts. |
