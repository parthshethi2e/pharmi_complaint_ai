import pandas as pd
import nltk
import joblib
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report

nltk.download('stopwords')
from nltk.corpus import stopwords

df = pd.read_csv("data/complaints.csv")
X = df["Complaint_Text"]
y = df["Category_Label"]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

pipeline = Pipeline([
    ("tfidf", TfidfVectorizer(stop_words=stopwords.words("english"))),
    ("clf", RandomForestClassifier(n_estimators=100, random_state=42))
])

pipeline.fit(X_train, y_train)


y_pred = pipeline.predict(X_test)
print("\nClassification Report:\n", classification_report(y_test, y_pred))

joblib.dump(pipeline, "models/model.joblib")
print("✅ Model saved to models/model.joblib")