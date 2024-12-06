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

            fly_count = st.number_input(f"Number of Flies in Condition {i+1}", min_value=1, value=1)
            
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
        st.write("analysis")

        #df = pd.read_csv(uploaded_files, sep='\t', header=None) // Edit this so it works with the uploaded_files variable
        df = pd.read_csv('/home/twall5/sleep_analysis-3/examples/Monitor9.txt', sep='\t', header=None)

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

        #get the time in the date_time column, if the time is from 06:00 to 18:00 then it is LD, else it is DD
        df['LD_DD'] = df['Date_Time'].dt.time
        df['LD_DD'] = df['LD_DD'].apply(lambda x: 'LD' if x >= pd.to_datetime(LD_start).time() and x <= pd.to_datetime('18:00').time() else 'DD')

        df = df[['Index','Date_Time','LD_DD','LD-DD','Status','Extras','Monitor_Number','Tube_Number','Data_Type','Light_Sensor','data_1','data_2','data_3','data_4','data_5','data_6','data_7','data_8','data_9','data_10','data_11','data_12','data_13','data_14','data_15','data_16','data_17','data_18','data_19','data_20','data_21','data_22','data_23','data_24','data_25','data_26','data_27','data_28','data_29','data_30','data_31','data_32']]

        # Adjust end_date to include the entire day of 2024-02-27
        end_date = pd.to_datetime(ld_end_date) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)

        # Filter on date between start_date & end_date
        df = df[(df['Date_Time'] >= pd.to_datetime(ld_start_date)) & (df['Date_Time'] <= end_date)]

        #Filtet on LD_DD based on LD_DD_analysis
        df = df[df['LD_DD'] == LD_DD_Analysis]

        #Create column called date_LD_DD based on concat of date + LD_DD
        df['date_LD_DD'] = df['Date_Time'].dt.date.astype(str) + '_' + df['LD_DD']
        #Move date_LD_DD to the right of LD-DD
        df = df[['Index','Date_Time','LD_DD','date_LD_DD','LD-DD','Status','Extras','Monitor_Number','Tube_Number','Data_Type','Light_Sensor','data_1','data_2','data_3','data_4','data_5','data_6','data_7','data_8','data_9','data_10','data_11','data_12','data_13','data_14','data_15','data_16','data_17','data_18','data_19','data_20','data_21','data_22','data_23','data_24','data_25','data_26','data_27','data_28','data_29','data_30','data_31','data_32']]

        # Exclude 'Date_Time' column from the sum operation
        df = df.drop(columns=['Date_Time','Index','LD_DD','LD-DD','Status','Extras','Monitor_Number','Tube_Number','Data_Type','Light_Sensor']).groupby('date_LD_DD').sum()


        st.write(df)
#         #Convert the previous R code into python code
#         #Create a dataframe with conditions and number of flies in each condition
#         Conditions_and_numbers = pd.DataFrame({
#             "Condition_names": [condition["name"] for condition in conditions],
#             "Condition_counts": [condition["fly_count"] for condition in conditions]
#         })
#         st.write(Conditions_and_numbers)


#         #Convert the code into python code from r code
#         #A vector of desired monitor order
#         Monitor_desired_order = [condition["monitor_order"] for condition in conditions]
#         st.write(Monitor_desired_order)

#         #A vector of colors
#         Plot_colors = [condition["plot_colors"] for condition in conditions]
#         st.write(Plot_colors)

#         #A vector of conditions (data frame conversion to a vector)
#         conditions = [condition["name"] for condition in conditions]
#         st.write(conditions)

#         #Create a dataframe with the monitor order and plot colors
#         Monitor_order_and_colors = pd.DataFrame({
#             "Monitor_order": Monitor_desired_order,
#             "Plot_colors": Plot_colors
#         })

#         st.write(Monitor_order_and_colors)

#         #Create a dataframe with the conditions
#         Conditions = pd.DataFrame({
#             "Conditions": conditions
#         })

#         st.write(Conditions)

#         #Convert the following R code into python code, make sure you make it for if the user create a LD, DD, or Both
#         #Create a dataframe with the LD/DD status
#         if LD_DD_Analysis == "LD":
#             date_and_light_cycle_1 = pd.DataFrame({
#             "date": pd.date_range(start=ld_start_date, end=ld_end_date),
#             "light_cycle": ["LD"] * ((ld_end_date - ld_start_date).days + 1)
#             })
#         elif LD_DD_Analysis == "DD":
#             date_and_light_cycle_1 = pd.DataFrame({
#             "date": pd.date_range(start=dd_start_date, end=dd_end_date),
#             "light_cycle": ["DD"] * ((dd_end_date - dd_start_date).days + 1)
#             })
#         else:
#             ld_dates = pd.date_range(start=ld_start_date, end=ld_end_date)
#             dd_dates = pd.date_range(start=dd_start_date, end=dd_end_date)
#             dates = ld_dates.append(dd_dates)
#             light_cycles = ["LD"] * len(ld_dates) + ["DD"] * len(dd_dates)
#             date_and_light_cycle_1 = pd.DataFrame({
#             "date": dates,
#             "light_cycle": light_cycles
#             })

#         st.write(date_and_light_cycle_1)

#         # Assuming range_of_days is a function or list of dates
#         if LD_DD_Analysis == "Both":
#             range_of_days = pd.date_range(start=min(ld_start_date, dd_start_date), end=max(ld_end_date, dd_end_date))
#         elif LD_DD_Analysis == "LD":
#             range_of_days = pd.date_range(start=ld_start_date, end=ld_end_date)
#         else:
#             range_of_days = pd.date_range(start=dd_start_date, end=dd_end_date)

#         date_and_light_cycle_2 = date_and_light_cycle_1[date_and_light_cycle_1["date"].isin(range_of_days)]
#         st.write(date_and_light_cycle_2)



#         #Convert the following R code into python code
#         #Create a dataframe with the DAM system data acquisition frequency
#         dam_frequency = pd.DataFrame({
#             "DAM_frequency": [dam_frequency]
#         })
#         st.write(dam_frequency)

#         # data_freq - actually a number of minutes per day in the recorded data
#         data_freq = 1440 / dam_frequency.iloc[0, 0]

#         # List of monitor files in an order specified by the user. Order is important for proper condition assignment.
#         # List of monitor files in an order specified by the user. Order is important for proper condition assignment.
#         def import_list(uploaded_files, monitor_order):
#             # Create a dictionary to map file names to their paths
#             file_dict = {file.name: file for file in uploaded_files}
            
#             # Order the files based on the monitor_order
#             ordered_files = [file_dict[name] for sublist in monitor_order for name in sublist if name in file_dict]
            
#             # Read the files into a list of dataframes
#             dataframes = [pd.read_csv(file, delimiter='\t', header=None) for file in ordered_files]
            
#             return dataframes


#         # Removes unnecessary columns directly from objects in the list
#         def remove_unnecessary_columns(dataframes):
#             columns_to_remove = ["V7", "V8", "V9", "V10", "V11", "V12"]
#             cleaned_dataframes = [df.drop(columns=[col for col in columns_to_remove if col in df.columns and col not in ["V2", "V3", "V4", "V5"]], errors='ignore') for df in dataframes]
#             return cleaned_dataframes

#         # Example usage
#         dataframes = import_list(uploaded_files, Monitor_desired_order)
#         cleaned_dataframes = remove_unnecessary_columns(dataframes)


#         # Merges dataframes of monitor files into a single "data" dataframe
#         def merge_dataframes(dataframes):
#             with st.spinner('Reading data...'):
#                 if not dataframes:
#                     return pd.DataFrame()  # Return an empty DataFrame if the list is empty
#                 merged_data = reduce(lambda left, right: pd.merge(left, right, on=["V1", "V2", "V3", "V4", "V5"], how='outer'), dataframes)
#             return merged_data

#         # Example usage
#         merged_data = merge_dataframes(cleaned_dataframes)

#         # Singles out the data status columns. This column stores error codes.
#         def monitor_data_status(data):
#             # Select columns that match the pattern "V6*"
#             status_columns = data.filter(regex="^V6.*")
#             return status_columns

#         # Example usage
#         data_status = monitor_data_status(merged_data)


#         # Removes data_status column
#         def remove_data_status_column(data):
#             return data.drop(columns=data.filter(regex="^V6.*").columns)

#         # Removes columns containing time and data status information, necessary for renaming other columns with monitor and channel number
#         def remove_time_and_status_columns(data):
#             return data.drop(columns=data.columns[:5])

#         # Renames channels adding a Monitor number
#         def rename_channels(data, monitor_order):
#             file_name_short = [name.replace(".txt", "") for sublist in monitor_order for name in sublist]
#             new_column_names = [f"{file_name_short[i]}_{col}" for i, col in enumerate(data.columns)]
#             data.columns = new_column_names
#             return data

#         # Example usage
#         data_without_status = remove_data_status_column(merged_data)
#         data_without_time_and_status = remove_time_and_status_columns(data_without_status)
#         renamed_data = rename_channels(data_without_time_and_status, Monitor_desired_order)


#         # Pastes channel numbers
#         def paste_channel_numbers(data, monitor_order):
#             file_name_short = [name.replace(".txt", "") for sublist in monitor_order for name in sublist]
#             new_column_names = [f"{file_name_short[i // 32]}_ch{(i % 32) + 1}" for i in range(len(data.columns))]
#             data.columns = new_column_names
#             return data

#         # Example usage
#         renamed_data_44 = paste_channel_numbers(renamed_data, Monitor_desired_order)

#         # Pastes monitor numbers into a dataframe containing monitor status codes
#         def paste_monitor_numbers(data_status, monitor_order):
#             file_name_short = [name.replace(".txt", "") for sublist in monitor_order for name in sublist]
#             new_column_names = [f"{file_name_short[i]}_data_status" for i in range(len(data_status.columns))]
#             data_status.columns = new_column_names
#             return data_status

#         # Example usage
#         monitor_data_status_1 = paste_monitor_numbers(data_status, Monitor_desired_order)


#         # Creates a dataframe with date information and status codes
#         def create_dataframe_with_date_info(data_x, monitor_data_status, renamed_data_44):
#             if all(col in data_x.columns for col in ["V2", "V3", "V4", "V5"]):
#                 data_43 = pd.DataFrame({
#                 "day": data_x["V2"],
#                 "month": data_x["V3"],
#                 "year": data_x["V4"],
#                 "time": data_x["V5"]
#                 })
#                 data_43 = pd.concat([data_43, monitor_data_status, renamed_data_44], axis=1)
#                 return data_43
#             else:
#                 return None

#         # Reformats date information from 3 into 1 column
#         def reformat_date_information(data_43):
#             data_43["date"] = pd.to_datetime(data_43[["day", "month", "year"]].astype(str).agg('-'.join, axis=1), format="%d-%b-%y")
#             return data_43

#         # Subsets the data to a range of dates
#         def subset_data_to_date_range(data_42, range_of_days):
#             s_1 = data_42[data_42["date"].isin(range_of_days)]
#             return s_1

#         #Convert the following R code into python code
#         #Counts the number of days in a dataset
#         number_of_days = len(date_and_light_cycle_2["date"].unique())


#         #Convert the following R code into python code
#         #Function converting time into decimal values
#         def decimateTime(time):
#             time = time.split(":")
#             time = int(time[0])*60 + int(time[1]) + int(time[2])/60
#             return time

#         #Convert the following R code into python code, use the subset_data_to_date_range function
#         #Subsets the data to a range of dates
#         s_1 = create_dataframe_with_date_info(dataframes[0], monitor_data_status_1, renamed_data_44)
#         s_1 = reformat_date_information(s_1)
#         s_1 = subset_data_to_date_range(s_1, range_of_days)


