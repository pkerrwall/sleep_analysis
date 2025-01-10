import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta, time
from functools import reduce


download_path = "/home/twall5/sleep_analysis-3/Monitor9.txt"

#Create a header
st.write("# Settings and Daily Locomotor Activity Analysis")

# --- File Upload ---
uploaded_files = st.sidebar.file_uploader("Choose DAM Monitor Files", accept_multiple_files=True)
#Make a uploaded_files variable that automatically uploads the Monitor9.txt file
#uploaded_files = [download_path]
LD_start = '06:00'
DD_start = '18:00'


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
            #condition_name = st.text_input(f"Condition {i+1} Name", value=f"Condition {i+1}")
            condition_name = st.text_input(f"Condition {i+1} Name", value="wt")

            fly_count = st.number_input(f"Number of Flies in Condition {i+1}", min_value=1, value=32)
            
            # Monitor Order and Plot Colors
            monitor_order = []
            plot_colors = []
            
            if uploaded_files:
                for j, file in enumerate(uploaded_files):
                    st.write(f"File: {file.name}")
                    monitor_order.append(st.text_input(f"Monitor Order for {file.name} (Condition {i+1})", value=f"Monitor {j+1}"))
                    plot_colors.append(st.color_picker(f"Pick Plot Color for {file.name} (Condition {i+1})", value="#BEBEBE"))

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

        LD_DD_Analysis = st.radio("LD DD Analysis", ["LD", "DD", "Both"], index=0)


        if LD_DD_Analysis == "LD":
        # Date range for LD phase
            st.markdown("### Date Range for LD")
            ld_start_date = st.date_input("LD Start Date", value=datetime(2024, 2, 24))
            ld_end_date = st.date_input("LD End Date", value=datetime(2024, 2, 27))

            #Convert the date to "24 Feb 24'" format
            ld_start_date = ld_start_date.strftime('%d %b %y')
            ld_end_date = ld_end_date.strftime('%d %b %y')

            start_date = ld_start_date + ' 00:00:00'
            end_date = ld_end_date + ' 23:59:59'
        elif LD_DD_Analysis == "DD":

            # Date range for DD phase
            st.markdown("### Date Range for DD")
            dd_start_date = st.date_input("DD Start Date", value=datetime(2024, 1, 16))
            start_date = dd_start_date + ' 00:00:00'
            dd_end_date = st.date_input("DD End Date", value=datetime(2024, 1, 31))
            end_date = dd_end_date + ' 23:59:59'
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
        dam_frequency = st.number_input("Enter the frequency in minutes", min_value=1, max_value=60, value=1)

        # Threshold for identifying dead flies
        st.markdown("### Threshold of Counts per Day Identifying Dead Flies")
        dead_fly_threshold = st.number_input("Threshold of Counts per Day", min_value=0, value=100)

        # Light onset time
        st.markdown("### Light Onset Time")
        light_onset_time = st.time_input("Enter the light onset time", value=time(6, 0))

        # Display summary of entered values
        # st.write("### Summary of LD-DD Analysis Parameters")
        # st.write(f"**LD Phase:** {ld_start_date} to {ld_end_date}")
        # st.write(f"**DD Phase:** {dd_start_date} to {dd_end_date}")
        # st.write(f"**Data Acquisition Frequency:** {dam_frequency} minutes")
        # st.write(f"**Threshold for Dead Flies:** {dead_fly_threshold} counts/day")
        # st.write(f"**Light Onset Time:** {light_onset_time}")
    #Make a start analysis button that when the user clicks it, the analysis will start and for right now it prints out all of the variables
    #Make this download into a .csv file, use pandas to create a dataframe and then use the .to_csv() function to save it as a .csv file
    if st.button("Start Analysis"):
        df = pd.read_csv(uploaded_files[0], sep='\t', header=None)
        st.header("Locomotor activity in LD")
        #Give the columns names
        #Index,Date,Time,LD-DD,Status,Extras,Monitor_Number,Tube_Number,Data_Type,Unused,Light_Sensor,data_1,data_2,data_3,data_4,data_5,data_6,data_7,data_8,data_9,data_10,data_11,data_12,data_13,data_14,data_15,data_16,data_17,data_18,data_19,data_20,data_21,data_22,data_23,data_24,data_25,data_26,data_27,data_28,data_29,data_30,data_31,data_32
        df.columns = ['Index','Date','Time','LD-DD','Status','Extras','Monitor_Number','Tube_Number','Data_Type','Light_Sensor','data_1','data_2','data_3','data_4','data_5','data_6','data_7','data_8','data_9','data_10','data_11','data_12','data_13','data_14','data_15','data_16','data_17','data_18','data_19','data_20','data_21','data_22','data_23','data_24','data_25','data_26','data_27','data_28','data_29','data_30','data_31','data_32']

        #Combine the date and time collumns, it should look something like '23 Feb 24 11:03:00'
        df['Date'] = df['Date'] + ' ' + df['Time']
        #Get rid of the time column
        df = df.drop(columns=['Time'])
        #Rename the collumn to Date_Time
        df = df.rename(columns={'Date':'Date_Time'})

        #Convert df_copy Date_Time to a datetime object, the format is day Feb 24 time
        df['Date_Time'] = pd.to_datetime(df['Date_Time'], format='%d %b %y %H:%M:%S')
        

        #Filter on date between start_date & end_date, make sure you include the entire day of end_date
        df = df[(df['Date_Time'] >= pd.to_datetime(start_date)) & (df['Date_Time'] <= pd.to_datetime(end_date))]
        
        #Create a new column called "date" and just put the date in it
        df['Date'] = df['Date_Time'].dt.date

        #create a new column called "time" and just put the time in it
        df['Time'] = df['Date_Time'].dt.time
        #create a new column called "Condition" and put the condition in it
        df['Condition'] = condition_name

        #create a new column called 'Light_Cycle' and just put LD_DD_Analysis in it
        df['Light_Cycle'] = LD_DD_Analysis

        #rename the Data columns to ch columns, for example make Data_1 = ch1
        df = df.rename(columns={'data_1':'ch1','data_2':'ch2','data_3':'ch3','data_4':'ch4','data_5':'ch5','data_6':'ch6','data_7':'ch7','data_8':'ch8','data_9':'ch9','data_10':'ch10','data_11':'ch11','data_12':'ch12','data_13':'ch13','data_14':'ch14','data_15':'ch15','data_16':'ch16','data_17':'ch17','data_18':'ch18','data_19':'ch19','data_20':'ch20','data_21':'ch21','data_22':'ch22','data_23':'ch23','data_24':'ch24','data_25':'ch25','data_26':'ch26','data_27':'ch27','data_28':'ch28','data_29':'ch29','data_30':'ch30','data_31':'ch31','data_32':'ch32'})
        
        df = df[['Date','Time','Condition','Light_Cycle','ch1','ch2','ch3','ch4','ch5','ch6','ch7','ch8','ch9','ch10','ch11','ch12','ch13','ch14','ch15','ch16','ch17','ch18','ch19','ch20','ch21','ch22','ch23','ch24','ch25','ch26','ch27','ch28','ch29','ch30','ch31','ch32']]

        data_df_total = pd.DataFrame()

        #get all the days selected in the date range
        days = df['Date'].unique()

        for day in days:
            # Filter the dataframe for the current day
            data_df_day = df[df['Date'] == day]

            # Drop the Date and Time columns
            data_df_day = data_df_day.drop(columns=['Date', 'Time'])

            # Add a row at the bottom of the dataframe that is the sum of all the columns
            data_df_day.loc[day] = data_df_day.sum()

            # Make Condition and Light_Cycle go back to normal
            data_df_day['Condition'] = condition_name
            data_df_day['Light_Cycle'] = LD_DD_Analysis

            # Add the date back to the total row
            data_df_day.loc[day, 'Date'] = day

            #Move date to the front of the dataframe
            data_df_day = data_df_day[['Date', 'Condition', 'Light_Cycle', 'ch1', 'ch2', 'ch3', 'ch4', 'ch5', 'ch6', 'ch7', 'ch8', 'ch9', 'ch10', 'ch11', 'ch12', 'ch13', 'ch14', 'ch15', 'ch16', 'ch17', 'ch18', 'ch19', 'ch20', 'ch21', 'ch22', 'ch23', 'ch24', 'ch25', 'ch26', 'ch27', 'ch28', 'ch29', 'ch30', 'ch31', 'ch32']]

            # Add the total row to the data_df_total dataframe
            data_df_total = pd.concat([data_df_total, data_df_day.tail(1)], ignore_index=True)

        # Create a new row that is the mean of all the ch columns
        numeric_cols = data_df_total.columns[3:]  # Exclude 'Condition', 'Light_Cycle', 'Name'
        data_df_total.loc['Mean', numeric_cols] = data_df_total[numeric_cols].mean()



        n_of_all_flies = 32
        n_of_alive_flies = 32
        n_of_dead_flies = 0
        # Create a list of available channels
        channel_columns = [f'ch{i}' for i in range(1, 33)]
        available_channels = channel_columns.copy()
        unavailble_channels = []

        # Loop through all the rows except mean, if any of the ch columns is less than counts_per_day_alive, add 1 to n_of_dead_flies
        for index, row in data_df_total.iterrows():
            if index != 'Mean':
                for ch in available_channels:
                    if row[ch] < dead_fly_threshold:
                        n_of_dead_flies += 1
                        available_channels.remove(ch)
                        unavailble_channels.append(ch)
                        break
        n_of_alive_flies = n_of_all_flies - n_of_dead_flies

        # On the mean row, add up all the columns from ch1 to ch32, put this into a new variable called mean
        mean = data_df_total.loc['Mean', available_channels].sum() / n_of_alive_flies
        #find the standard deviation from the available_channels mean
        std = data_df_total.loc['Mean', available_channels].std()
        #Find the Standard Error of the Mean (SEM) from the available_channels mean
        sem = std / (n_of_alive_flies ** 0.5)
        #Create a new dataframe called Daily_locomotor_activity with the columns Condition, Light_Cycle, Mean, SD, SEM, N_of_alive_flies, N_of_dead_flies, N_of_all_flies
        Daily_locomotor_activity = pd.DataFrame(data={'Condition': [condition_name], 'Light_Cycle': [LD_DD_Analysis], 'Mean': [mean], 'SD': [std], 'SEM': [sem], 'N_of_alive_flies': [n_of_alive_flies], 'N_of_dead_flies': [n_of_dead_flies], 'N_of_all_flies': [n_of_all_flies]})

        st.write(Daily_locomotor_activity)
        #st.write(data_df_total)
        #st.write(df)