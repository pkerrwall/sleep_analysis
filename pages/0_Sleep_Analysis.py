import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta, time

# set to wide layout mode
st.set_page_config(layout="wide")

st.write("# Sleep Analysis")

col1, col2 = st.columns(2)

def zeitgeber_time(dt):
    if dt.time() >= pd.to_datetime('06:00').time() and dt.time() <= pd.to_datetime('23:59').time():
        # subtract 6 hours from the time
        six_hours = timedelta(hours=6)
        zt_time = dt - six_hours
    else:
        # add 18 hours to the time
        eighteen_hours = timedelta(hours=18)
        zt_time = dt + eighteen_hours
    return zt_time

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
    #Load in the sleep_analysis_df session state from the previous page
    sleep_analysis_df = st.session_state.sleep_analysis_df
    #st.write(sleep_analysis_df)

    sleep_analysis_df['zt_time'] = sleep_analysis_df['Date_Time'].apply(zeitgeber_time)
    #get the numeric cols variable from Homy.py
    #st.write(sleep_analysis_df)
    numeric_cols = st.session_state.numeric_cols
    #Make column header Index, Date, Time, LDD-DD, Status, Monitor_Number, Extras, Tube_Number, Data_Type, Light_Sensor, ch1, ch2, ch3, ch4, ch5, ch6, ch7, ch8, ch9, ch10, ch11, ch12, ch13, ch14, ch15, ch16, ch17, ch18, ch19, ch20, ch21, ch22, ch23, ch24, ch25, ch26, ch27, ch28, ch29, ch30, ch31, ch32, Date_Time, LD_DD, zt_time
    sleep_analysis_df.columns = ['Index', 'Date', 'Time', 'LDD-DD', 'Status', 'Monitor_Number', 'Extras', 'Tube_Number', 'Data_Type', 'Light_Sensor', 'ch1', 'ch2', 'ch3', 'ch4', 'ch5', 'ch6', 'ch7', 'ch8', 'ch9', 'ch10', 'ch11', 'ch12', 'ch13', 'ch14', 'ch15', 'ch16', 'ch17', 'ch18', 'ch19', 'ch20', 'ch21', 'ch22', 'ch23', 'ch24', 'ch25', 'ch26', 'ch27', 'ch28', 'ch29', 'ch30', 'ch31', 'ch32', 'Date_Time', 'LD_DD', 'zt_time']
    #st.write(sleep_analysis_df)
    df_sleep_trim = sleep_analysis_df[['Date_Time', 'zt_time'] + list(numeric_cols)]
    #st.write(df_sleep_trim)
    unavailable_channels = st.session_state.unavailble_channels
    available_channels = st.session_state.available_channels
    #st.write(unavailable_channels)
    #st.write(available_channels)
    df_sleep_trim_alive = df_sleep_trim.drop(unavailable_channels, axis=1)
    
    # Vectorized calculation for sleep
    df_sleep_trim_alive = df_sleep_trim_alive.set_index('Date_Time')
    sleep_calc_df = df_sleep_trim_alive.rolling(5).sum().applymap(lambda x: 1 if x == 0 else 0)
    
    # Add zt_time back into the DataFrame
    sleep_calc_df['zt_time'] = df_sleep_trim_alive.index.to_series().apply(zeitgeber_time)
    sleep_calc_df = sleep_calc_df.reset_index()

    # Calculate mean and sem
    sleep_calc_df['mean'] = sleep_calc_df[available_channels].mean(axis=1)
    sleep_calc_df['sem'] = sleep_calc_df[available_channels].sem(axis=1)
    
    #st.write(sleep_calc_df)
    avg_sleep_df = sleep_calc_df.copy()
    avg_sleep_df['time'] = avg_sleep_df['Date_Time'].dt.time

    avg_sleep_df = avg_sleep_df[['time', 'mean']]

    avg_sleep_df.sort_values('time', inplace=True)

    # reset the index
    avg_sleep_df.reset_index(drop=True, inplace=True)
    #st.write(avg_sleep_df)

    bin = Bin_sleep_profile
    avg_sleep_list = []
    for i in range(0, len(avg_sleep_df), bin):
        #print(f"start={i}, end={i+bin-1}")
        start_time = pd.to_datetime(i, unit='m').time()
        end_time = pd.to_datetime(i+bin-1, unit='m').time()
        #print(f"start_time={start_time}, end_time={end_time}")
        
        # put the mean values into a list where the time is between start_time and end_time
        mean_values = avg_sleep_df[(avg_sleep_df['time'] >= start_time) & (avg_sleep_df['time'] <= end_time)]['mean'].tolist()
        
        # calculate the mean of the mean_values
        bin_mean = sum(mean_values) / len(mean_values)
        
        # calculate the sem of the mean_values
        bin_sem = pd.Series(mean_values).sem()
        
        avg_sleep_list.append([i, bin_mean, bin_sem])

    avg_sleep_list_df = pd.DataFrame(avg_sleep_list, columns=['time', 'mean', 'sem'])
    avg_sleep_list_df['zt_time'] = pd.to_datetime(avg_sleep_list_df['time'], unit='m').dt.time
    st.header("avg_sleep_list")
    st.write(avg_sleep_list_df)

    def day_night(dt):
        if dt.time() >= pd.to_datetime('06:00').time() and dt.time() <= pd.to_datetime('18:00').time():
            return 'Day'
        else:
            return 'Night'

    ind_day_night = sleep_calc_df.copy()  # Use sleep_calc_df here instead of df_sleep_calc
    ind_day_night['Day_Night'] = ind_day_night['Date_Time'].apply(day_night)

    ind_day_night = ind_day_night[['Day_Night'] + available_channels]

    ind_day_night_unpivoted = ind_day_night.melt(id_vars=['Day_Night'], value_vars=available_channels, var_name='Channel', value_name='Counts')


    ind_day_night_mean = ind_day_night_unpivoted.groupby(['Day_Night', 'Channel'])['Counts'].mean().reset_index()

    # sort by Channel and Day_Night
    ind_day_night_mean.sort_values(['Channel', 'Day_Night'], inplace=True)

    # reset index
    ind_day_night_mean.reset_index(drop=True, inplace=True)
    st.header("Individual Day/Night Mean")
    st.write(ind_day_night_mean)


    # Initialize list for bout data
    bout_data = []

    # Iterate over each available channel
    for col in available_channels:
        # Use diff to find transitions (0 -> 1 or 1 -> 0)
        changes = sleep_calc_df[col].diff().fillna(0).apply(lambda x: 1 if x != 0 else 0)

        # Get the indices of changes (where diff is not zero)
        change_indices = changes[changes == 1].index
        
        # Initialize variables for the previous time and value
        prev_value = sleep_calc_df.at[change_indices[0], col] if change_indices.size > 0 else None
        prev_time = sleep_calc_df.at[change_indices[0], 'Date_Time'] if change_indices.size > 0 else None

        for idx in change_indices:
            current_value = sleep_calc_df.at[idx, col]
            current_time = sleep_calc_df.at[idx, 'Date_Time']
            
            # Calculate the bout length only if the current and previous values differ
            if prev_value is not None and prev_value != current_value:
                bout_length = (current_time - prev_time).total_seconds() / 60  # Convert to minutes
                bout_data.append({
                    'Channel': col,
                    'Time': prev_time,
                    'Value': prev_value,
                    'Bout_Length': bout_length
                })
            
            # Update the previous value and time
            prev_value = current_value
            prev_time = current_time

    # Create DataFrame for the individual sleep bouts
    ind_sleep_bout_df = pd.DataFrame(bout_data)

    # Display the resulting DataFrame
    st.header("Individual Sleep Bout")
    st.write(ind_sleep_bout_df)

