import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import os, json, base64
import matplotlib.pyplot as plt
import matplotlib.dates as mdates


SHEET_NAME = "PharmaComplaints"
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

creds_b64 = os.environ.get("GOOGLE_CREDS")
if not creds_b64:
    raise RuntimeError("❌ GOOGLE_CREDS environment variable is missing!")

creds_json = base64.b64decode(creds_b64).decode("utf-8")
creds_dict = json.loads(creds_json)


#CREDS = Credentials.from_service_account_file("portfolioonetest-5d749f3c33db.json", scopes=SCOPES)
CREDS = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
gc = gspread.authorize(CREDS)
worksheet = gc.open(SHEET_NAME).sheet1

data = worksheet.get_all_records()
df = pd.DataFrame(data)

st.set_page_config(page_title="📊 Pharma Complaint Analytics")
st.title("📊 Pharma Complaint Analytics Dashboard")

if df.empty:
    st.warning("No complaint data available yet.")
    st.stop()

# Convert Date column to datetime
df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

# Show raw data
with st.expander("📂 View Raw Data"):
    st.dataframe(df)

# --- Stats ---
st.subheader("📈 Overall Statistics")
st.metric("Total Complaints", len(df))
st.metric("Unique Medicines", df["Medicine_Name"].nunique())
st.metric("Complaint Categories", df["Predicted_Category"].nunique())

# --- Graph 1: Complaints over time ---
st.subheader("🗓 Complaints Over Time")
complaints_over_time = df.groupby(df["Date"].dt.date).size()
fig, ax = plt.subplots()
complaints_over_time.plot(kind="line", marker="o", ax=ax)
ax.set_xlabel("Date")
ax.set_ylabel("Number of Complaints")
ax.set_title("Complaints Logged Over Time")
ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
plt.xticks(rotation=45, ha="right")

fig.tight_layout()
st.pyplot(fig)

# --- Graph 2: Complaint Categories ---
st.subheader("📌 Complaints by Category")
category_counts = df["Predicted_Category"].value_counts()
fig2, ax2 = plt.subplots()
category_counts.plot(kind="bar", ax=ax2)
ax2.set_xlabel("Category")
ax2.set_ylabel("Count")
ax2.set_title("Complaint Types")
st.pyplot(fig2)

# --- Graph 3: Medicine-wise complaints ---
st.subheader("💊 Complaints by Medicine")
medicine_counts = df["Medicine_Name"].value_counts().head(10)  # top 10
fig3, ax3 = plt.subplots()
medicine_counts.plot(kind="barh", ax=ax3)
ax3.set_xlabel("Number of Complaints")
ax3.set_ylabel("Medicine")
ax3.set_title("Top Medicines with Complaints")
st.pyplot(fig3)