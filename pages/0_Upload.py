import streamlit as st
import pandas as pd
from datetime import datetime
import os

st.write("# Upload Monitor Files")

UPLOAD_DIR = "uploaded_monitors"
HISTORY_CSV = "uploaded_files_history.csv"

os.makedirs(UPLOAD_DIR, exist_ok=True)

# Initialize session state for upload history
if "upload_history" not in st.session_state:
    if os.path.exists(HISTORY_CSV):
        history_df = pd.read_csv(HISTORY_CSV)
        st.session_state.upload_history = history_df.to_dict("records")
    else:
        st.session_state.upload_history = []

# File uploader
uploaded_file = st.file_uploader("Choose a file", type=["csv", "xlsx", "txt"])

if uploaded_file is not None:
    st.success(f"File '{uploaded_file.name}' uploaded. Please enter a description/label below.")
    description = st.text_input("Enter a description or label for the file (optional):")
    if st.button("Save File Info"):
        # Save file to disk
        file_path = os.path.join(UPLOAD_DIR, uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        # Save metadata
        new_entry = {
            "Filename": uploaded_file.name,
            "Upload Time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Description": description
        }
        st.session_state.upload_history.append(new_entry)
        pd.DataFrame(st.session_state.upload_history).to_csv(HISTORY_CSV, index=False)
        st.success("File info and content saved!")

# Show upload history
if st.session_state.upload_history:
    history_df = pd.DataFrame(st.session_state.upload_history, columns=["Filename", "Upload Time", "Description"])
    st.write("### Uploaded Data")
    st.dataframe(history_df)
else:
    st.info("No files have been uploaded yet.")
