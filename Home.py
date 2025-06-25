import streamlit as st

st.set_page_config(page_title="Welcome", layout="wide")

st.title("🐝 Drosophila Locomotor & Sleep Analysis App")
st.markdown("Welcome! This app helps you upload, configure, analyze, and compare **Drosophila locomotor and sleep activity** using DAM system monitor files.")

st.markdown("---")

st.header("📂 App Navigation Guide")

st.subheader("1. **Defaults**")
st.markdown("""
Customize your **default analysis settings** here:
- Set default LD/DD start and end dates
- Apply offsets to automatically shift dates after uploading
- Configure DAM system parameters like sampling frequency, threshold, and light onset time

These settings will auto-fill during experiments but can be overridden as needed.
""")

st.subheader("2. **Upload**")
st.markdown("""
Upload one or more **monitor files** from the DAM system.
- The app reads and previews your data
- Start and end dates are automatically adjusted using your default offset (if set)
""")

st.subheader("3. **Experiments**")
st.markdown("""
Run a **locomotor activity and sleep analysis** on uploaded monitor files.
- Set condition names and fly counts
- Apply the configured LD/DD and DAM settings
- Save and review the results
""")

st.subheader("4. **Experiment Comparison**")
st.markdown("""
Compare the results of two or more **saved experiments** side by side.
- Visualize and evaluate differences between experimental conditions
- Useful for genotype comparisons, treatment effects, or time series
""")

st.markdown("---")

st.info("Tip: Start by setting your default preferences in the **Defaults** tab, then upload your data in **Upload** to begin analysis.")
