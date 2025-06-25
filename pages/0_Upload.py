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

def get_first_date_from_file(uploaded_file):
    try:
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file, nrows=100)
        elif uploaded_file.name.endswith(".xlsx"):
            df = pd.read_excel(uploaded_file, nrows=100)
        elif uploaded_file.name.endswith(".txt"):
            df = pd.read_csv(uploaded_file, sep="\t", nrows=100)
            if not df.empty:
                df.columns = ['Index','Date','Time','LD-DD','Status','Extras','Monitor_Number',
                                 'Tube_Number','Data_Type','Light_Sensor'] + [f'data_{i}' for i in range(1, 33)]
                df['DateTime'] = pd.to_datetime(df['Date'] + ' ' + df['Time'], 
                                                    format='%d %b %y %H:%M:%S', errors='coerce')
                first_date = df['DateTime'].min().date()
                return str(first_date)
        else:
            st.error("Unsupported file type. Please upload a CSV, Excel, or TXT file.")
            return None
        # Try to find a date column
        for col in df.columns:
            try:
                dates = pd.to_datetime(df[col], errors='coerce')
                first_valid = dates.dropna().iloc[0]
                if pd.notnull(first_valid):
                    return str(first_valid.date())
            except Exception:
                continue
    except Exception:
        pass
    return None

if uploaded_file is not None:
    # Get default name: first date found + original filename
    first_date = get_first_date_from_file(uploaded_file)
    if first_date:
        default_name = f"{first_date}_{uploaded_file.name}"
    else:
        default_name = uploaded_file.name

    st.success(f"File '{uploaded_file.name}' uploaded. Please enter a name and description/label below.")
    file_name = st.text_input("File name:", value=default_name)
    description = st.text_input("Enter a description or label for the file (optional):")
    if st.button("Save File Info"):
        # Save file to disk
        file_path = os.path.join(UPLOAD_DIR, file_name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        # Save metadata
        new_entry = {
            "Filename": file_name,
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
