import google.generativeai as genai
import os


GEMINI_API_KEY =  os.environ.get("GEMINI_API_KEY")

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

def is_pharmacy_related(text: str) -> bool:
    """
    Uses Gemini to check if text is a pharmacy-related complaint.
    Returns True if relevant, False otherwise.
    """
    prompt = f"""
    Determine if the following text is a **pharmacy-related complaint** 
    (examples: medicine defect, packaging issue, side effects, expired medicine, contamination, wrong dosage).
    
    Text: "{text}"
    
    Answer only YES or NO.
    """
    response = model.generate_content(prompt)
    answer = response.text.strip().upper()
    return "YES" in answer

