import google.generativeai as genai
import os

GEMINI_API_KEY = "AIzaSyBMM2BohiQF8MxJ80euOy8pwcb7Q25Lk2g"

genai.configure(api_key=GEMINI_API_KEY)

model = genai.GenerativeModel("models/gemini-2.0-flash")

def classify_complaint(text: str) -> str:
    prompt = f"""
Classify the following pharmaceutical complaint into one of these:
- Packaging Defect
- Adverse Event
- Lack of Efficacy
- Logistics Error
- Expired Product
- Wrong Dosage
- Tampered Seal
- Contamination Suspected

Complaint: "{text}"

Category:"""
    response = model.generate_content(prompt)
    return response.text.strip()
