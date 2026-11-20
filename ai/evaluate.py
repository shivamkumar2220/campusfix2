# Classifier evaluation: how good is the complaint classifier on complaints it has never seen?
# Run:  venv\Scripts\python.exe -m ai.evaluate
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.model_selection import StratifiedKFold, cross_val_score, train_test_split

from ai.classifier import load_data, new_model

texts, categories = load_data()

# 1. Cross validation: train + test 5 times on different parts of the data
folds = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
scores = cross_val_score(new_model(), texts, categories, cv=folds)
print("Cross validation scores:", scores.round(3))
print(f"Average accuracy: {scores.mean():.1%}  (+/- {scores.std():.1%})")

# 2. Keep 20% of the data hidden, train on the other 80%, then test on the hidden 20%
train_x, test_x, train_y, test_y = train_test_split(texts, categories, test_size=0.2, random_state=42, stratify=categories)
model = new_model().fit(train_x, train_y)
predictions = model.predict(test_x)
print(f"\nTraining accuracy: {accuracy_score(train_y, model.predict(train_x)):.1%}")
print(f"Testing accuracy:  {accuracy_score(test_y, predictions):.1%}")
print("\nReport per category:\n", classification_report(test_y, predictions, zero_division=0))
print("Confusion matrix (rows = real, columns = predicted):", [str(c) for c in model.classes_])
print(confusion_matrix(test_y, predictions, labels=model.classes_))
