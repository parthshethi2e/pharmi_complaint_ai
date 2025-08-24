import pandas as pd
import joblib
from gemini_classifier import classify_complaint

# Load data
df = pd.read_csv("data/complaints.csv").sample(10, random_state=1)  # Test on 10 samples
model = joblib.load("models/model.joblib")

# Predict using Traditional ML
df["ML_Prediction"] = model.predict(df["Complaint_Text"])

# Predict using Gemini
df["Gemini_Prediction"] = df["Complaint_Text"].apply(classify_complaint)

# Show comparison
print(df[["Complaint_Text", "Category_Label", "ML_Prediction", "Gemini_Prediction"]])
