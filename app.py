import streamlit as st
from gemini_classifier import classify_complaint

st.set_page_config(page_title="Pharma Complaint Classifier", layout="centered")

st.title("💊 Pharma Complaint Classifier")
st.markdown("Classify pharmaceutical complaints using **Gemini AI**")

# Text input
complaint_text = st.text_area("Enter complaint text here:")

if st.button("Classify"):
    if complaint_text.strip():
        with st.spinner("Classifying using Gemini..."):
            category = classify_complaint(complaint_text)
        st.success(f"**Predicted Category:** {category}")
    else:
        st.warning("Please enter a complaint to classify.")
