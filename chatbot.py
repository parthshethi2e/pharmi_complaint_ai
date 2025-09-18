import streamlit as st
from gemini_classifier import classify_complaint
import pandas as pd
import re
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials

# CONFIG
SHEET_NAME = "PharmaComplaints"
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]
CREDS = Credentials.from_service_account_file("portfolioonetest-5d749f3c33db.json", scopes=SCOPES)
gc = gspread.authorize(CREDS)
worksheet = gc.open(SHEET_NAME).sheet1

# ✅ Ensure correct headers exist
def ensure_sheet_headers(sheet):
    headers = ["Ticket_ID", "Date", "User_Name", "Medicine_Name", "Complaint_Text", "Predicted_Category"]
    existing = sheet.row_values(1)
    if existing != headers:
        sheet.clear()
        sheet.insert_row(headers, index=1)

ensure_sheet_headers(worksheet)

# Utilities
def get_sheet_df():
    data = worksheet.get_all_records()
    return pd.DataFrame(data)

def append_to_sheet(row_dict):
    worksheet.append_row(list(row_dict.values()))

def generate_ticket_id():
    df = get_sheet_df()
    today = datetime.now().strftime("%Y-%m-%d")
    if "Date" not in df.columns:
        return f"CMP-{datetime.now().strftime('%Y%m%d')}-001"
    count_today = df[df["Date"] == today].shape[0] + 1
    return f"CMP-{datetime.now().strftime('%Y%m%d')}-{count_today:03d}"

def check_complaint_status(ticket_id):
    df = get_sheet_df()
    row = df[df["Ticket_ID"].str.strip() == ticket_id.strip()]
    if row.empty:
        return f"❌ No complaint found with Ticket ID: `{ticket_id}`."
    data = row.iloc[0]
    return (
        f"📄 Complaint Details:\n"
        f"- **Ticket ID:** {data['Ticket_ID']}\n"
        f"- **Date:** {data['Date']}\n"
        f"- **Name:** {data['User_Name']}\n"
        f"- **Medicine:** {data['Medicine_Name']}\n"
        f"- **Category:** {data['Predicted_Category']}\n"
        f"- **Text:** _{data['Complaint_Text']}_"
    )

# Streamlit UI
st.set_page_config(page_title="Pharma Complaint Chatbot")
st.title("🤖 Pharma Complaint Chatbot")

if "messages" not in st.session_state:
    st.session_state.messages = []
if "pending_ticket" not in st.session_state:
    st.session_state.pending_ticket = None
if "pending_medicine" not in st.session_state:
    st.session_state.pending_medicine = None

# Display chat history
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# User input
if prompt := st.chat_input("Enter your complaint or ticket ID..."):
    st.chat_message("user").write(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Check ticket status
    ticket_check_match = re.search(r"(status|check).*?(CMP-\d{8}-\d{3})", prompt, re.IGNORECASE)
    if ticket_check_match:
        ticket_id = ticket_check_match.group(2)
        status_reply = check_complaint_status(ticket_id)
        st.chat_message("assistant").write(status_reply)
        st.session_state.messages.append({"role": "assistant", "content": status_reply})
        st.stop()

    # Step 3: Name
    if st.session_state.pending_ticket and st.session_state.pending_medicine:
        ticket_data = st.session_state.pending_ticket
        user_name = prompt.strip()
        ticket_id = ticket_data["ticket_id"]

        append_to_sheet({
            "Ticket_ID": ticket_id,
            "Date": ticket_data["date"],
            "User_Name": user_name,
            "Medicine_Name": ticket_data["medicine_name"],
            "Complaint_Text": ticket_data["complaint"],
            "Predicted_Category": ticket_data["category"]
        })

        reply = f"✅ Thank you **{user_name}**. Your complaint has been logged with **Ticket #{ticket_id}**."
        st.chat_message("assistant").write(reply)
        st.session_state.messages.append({"role": "assistant", "content": reply})
        st.session_state.pending_ticket = None
        st.session_state.pending_medicine = None

    # Step 2: Medicine name
    elif st.session_state.pending_ticket and not st.session_state.pending_medicine:
        st.session_state.pending_ticket["medicine_name"] = prompt.strip()
        st.session_state.pending_medicine = True
        reply = "Please enter your **name** to complete your complaint submission."
        st.chat_message("assistant").write(reply)
        st.session_state.messages.append({"role": "assistant", "content": reply})

    # Step 1: New complaint
    else:
        complaint = prompt.strip()
        category = classify_complaint(complaint)
        ticket_id = generate_ticket_id()
        date_str = datetime.now().strftime("%Y-%m-%d")

        reply = (
            f"This seems like a **{category}** complaint.\n\n"
            f"Please enter the **medicine name** involved in this issue."
        )
        st.session_state.pending_ticket = {
            "ticket_id": ticket_id,
            "complaint": complaint,
            "category": category,
            "date": date_str
        }
        st.session_state.pending_medicine = False
        st.chat_message("assistant").write(reply)
        st.session_state.messages.append({"role": "assistant", "content": reply})
