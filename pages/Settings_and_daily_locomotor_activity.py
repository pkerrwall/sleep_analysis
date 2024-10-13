import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta, time


#Create a header
st.write("# Settings and Daily Locomotor Activity Analysis")

# --- File Upload ---
uploaded_files = st.sidebar.file_uploader("Choose DAM Monitor Files", type=["txt"], accept_multiple_files=True)

if uploaded_files:
    # --- Create Two Columns ---
    col1, col2 = st.columns(2)
    
    # --- First Column: Conditions ---
    with col1:
        st.subheader("Condition Details")

        # Number of Conditions
        num_conditions = st.number_input("Enter Number of Conditions", min_value=1, value=1)

        # Input Condition Names, Fly Counts, Colors, and Monitor File Order
        conditions = []
        for i in range(num_conditions):
            st.write(f"**Condition {i+1}**")
            condition_name = st.text_input(f"Condition {i+1} Name", value=f"Condition {i+1}")
            fly_count = st.number_input(f"Number of Flies in Condition {i+1}", min_value=1, value=1)
            
            # Monitor Order and Plot Colors
            monitor_order = []
            plot_colors = []
            
            if uploaded_files:
                for j, file in enumerate(uploaded_files):
                    st.write(f"File: {file.name}")
                    monitor_order.append(st.text_input(f"Monitor Order for {file.name} (Condition {i+1})", value=f"Monitor {j+1}"))
                    plot_colors.append(st.color_picker(f"Pick Plot Color for {file.name} (Condition {i+1})", value="#000000"))

            # Add to conditions list
            conditions.append({
                "name": condition_name,
                "fly_count": fly_count,
                "monitor_order": monitor_order,
                "plot_colors": plot_colors
            })
    
    # --- Second Column: Rest of the Fields ---
    with col2:
        st.subheader("LD-DD Analysis")

        LD_DD_Analysis = st.radio("LD DD Analysis", ["LD", "DD", "Both"], index=2)


        if LD_DD_Analysis == "LD":
        # Date range for LD phase
            st.markdown("### Date Range for LD")
            ld_start_date = st.date_input("LD Start Date", value=datetime(2024, 1, 1))
            ld_end_date = st.date_input("LD End Date", value=datetime(2024, 1, 15))
        elif LD_DD_Analysis == "DD":

            # Date range for DD phase
            st.markdown("### Date Range for DD")
            dd_start_date = st.date_input("DD Start Date", value=datetime(2024, 1, 16))
            dd_end_date = st.date_input("DD End Date", value=datetime(2024, 1, 31))
        elif LD_DD_Analysis =="Both":
            # Date range for LD phase
            st.markdown("### Date Range for LD")
            ld_start_date = st.date_input("LD Start Date", value=datetime(2024, 1, 1))
            ld_end_date = st.date_input("LD End Date", value=datetime(2024, 1, 15))

            # Date range for DD phase
            st.markdown("### Date Range for DD")
            dd_start_date = st.date_input("DD Start Date", value=datetime(2024, 1, 16))
            dd_end_date = st.date_input("DD End Date", value=datetime(2024, 1, 31))

        # DAM system data acquisition frequency
        st.markdown("### DAM System Data Acquisition Frequency [min]")
        dam_frequency = st.number_input("Enter the frequency in minutes", min_value=1, max_value=60, value=30)

        # Threshold for identifying dead flies
        st.markdown("### Threshold of Counts per Day Identifying Dead Flies")
        dead_fly_threshold = st.number_input("Threshold of Counts per Day", min_value=0, value=50)

        # Light onset time
        st.markdown("### Light Onset Time")
        light_onset_time = st.time_input("Enter the light onset time", value=time(8, 0))

        # Display summary of entered values
        st.write("### Summary of LD-DD Analysis Parameters")
        st.write(f"**LD Phase:** {ld_start_date} to {ld_end_date}")
        st.write(f"**DD Phase:** {dd_start_date} to {dd_end_date}")
        st.write(f"**Data Acquisition Frequency:** {dam_frequency} minutes")
        st.write(f"**Threshold for Dead Flies:** {dead_fly_threshold} counts/day")
        st.write(f"**Light Onset Time:** {light_onset_time}")
    #Make a start analysis button that when the user clicks it, the analysis will start and for right now it prints out all of the variables
    #Make this download into a .csv file, use pandas to create a dataframe and then use the .to_csv() function to save it as a .csv file
    if st.button("Start Analysis"):
        st.write("Starting Analysis...")
        st.write(f"**Conditions:** {conditions}")
        st.write(f"**LD-DD Analysis:** {LD_DD_Analysis}")
        st.write(f"**LD Phase:** {ld_start_date} to {ld_end_date}")
        st.write(f"**DD Phase:** {dd_start_date} to {dd_end_date}")
        st.write(f"**Data Acquisition Frequency:** {dam_frequency} minutes")
        st.write(f"**Threshold for Dead Flies:** {dead_fly_threshold} counts/day")
        st.write(f"**Light Onset Time:** {light_onset_time}")
        st.write("Analysis Completed!")
        #Create a dataframe
        df = pd.DataFrame({
            "Condition": [condition["name"] for condition in conditions],
            "Fly Count": [condition["fly_count"] for condition in conditions],
            "Monitor Order": [condition["monitor_order"] for condition in conditions],
            "Plot Colors": [condition["plot_colors"] for condition in conditions],
            "LD-DD Analysis": [LD_DD_Analysis],
            "LD Start Date": [ld_start_date],
            "LD End Date": [ld_end_date],
            "DD Start Date": [dd_start_date],
            "DD End Date": [dd_end_date],
            "Data Acquisition Frequency": [dam_frequency],
            "Threshold for Dead Flies": [dead_fly_threshold],
            "Light Onset Time": [light_onset_time]
        })
        #Save the dataframe as a .csv file
        df.to_csv("analysis_parameters.csv", index=False)
        st.write("Analysis Parameters Saved as analysis_parameters.csv")
        st.write("Download the file by clicking below.")


