import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta, time

# set to wide layout mode
st.set_page_config(layout="wide")

st.write("# Sleep Analysis")

col1, col2 = st.columns(2)

with col1:
    plot_conditions = st.radio("Conditions on a plot", ["Overlap", "Split"])

    Display_dates = st.radio("Display dates on a plot", ["Yes", "No"])
with col2:
    SEM_error = st.radio("Display SEM error bars", ["Yes", "No"], index=1)

    Sleep_profile = st.radio("X-axis average sleep profile time scale", ["Data aquisition time", "Zeitgeber time"])

#create a slider for Bin sleep profile data points into average [min] with the mininum being 1 and the max being 120
Bin_sleep_profile = st.slider("Bin sleep profile data points into average [min]", min_value=1, max_value=120, value=30)

#create a slider for Max value of sleep displayed with the minunum being 0 and the max being 1.2
Max_value_of_sleep_displayed = st.slider("Max value of sleep displayed", min_value=0.0, max_value=1.2, value=1.2)

Plot_height = st.slider("Plot height [pixel]", min_value=10, max_value=1000, value=400)

Plot_width = st.slider("Plot width [pixel]", min_value=400, max_value=3000, value=1400)

if st.button("Generate Sleep Analysis"):
    #Print out all the values
    st.write(f"**Conditions on a plot:** {plot_conditions}")
    st.write(f"**Display dates on a plot:** {Display_dates}")
    st.write(f"**Display SEM error bars:** {SEM_error}")
    st.write(f"**X-axis average sleep profile time scale:** {Sleep_profile}")
    st.write(f"**Bin sleep profile data points into average [min]:** {Bin_sleep_profile}")
    st.write(f"**Max value of sleep displayed:** {Max_value_of_sleep_displayed}")
    st.write(f"**Plot height [pixel]:** {Plot_height}")
    st.write(f"**Plot width [pixel]:** {Plot_width}")
    #Create a dataframe
    df = pd.DataFrame({
        "Conditions on a plot": [plot_conditions],
        "Display dates on a plot": [Display_dates],
        "Display SEM error bars": [SEM_error],
        "X-axis average sleep profile time scale": [Sleep_profile],
        "Bin sleep profile data points into average [min]": [Bin_sleep_profile],
        "Max value of sleep displayed": [Max_value_of_sleep_displayed],
        "Plot height [pixel]": [Plot_height],
        "Plot width [pixel]": [Plot_width]
    })
    #Save the dataframe to a .csv file
    df.to_csv("Sleep_Analysis.csv", index=False)
    st.write("Download the Sleep Analysis parameters")
    st.write("Download the file by clicking below.")
    st.markdown(f'<a href="Sleep_Analysis.csv" download="Sleep_Analysis.csv">Click here to download Sleep Analysis parameters</a>', unsafe_allow_html=True)
    