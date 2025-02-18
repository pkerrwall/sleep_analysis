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
    
    df_sleep_calc_list = []

    # loop through df_sleep_trim_alive
    for i in range(0, len(df_sleep_trim_alive)):
    #for i in range(0,2):
        current_row_list = [df_sleep_trim_alive.iloc[i]['Date_Time'], df_sleep_trim_alive.iloc[i]['zt_time']]
        for col in available_channels:
            # get the 5 min window
            five_min_window = df_sleep_trim_alive.iloc[i:i+5][col]
            #print(five_min_window)
            five_min_window_sum = five_min_window.sum()
            #print(five_min_window_sum)

            #print(f"index={i}, Date_Time={df_sleep_trim_alive.iloc[i]['Date_Time']}, zt_time={df_sleep_trim_alive.iloc[i]['zt_time']}, col={col}, five_min_window={five_min_window}")
            if five_min_window_sum == 0:
                sleep = 1
            else:
                sleep = 0
            # add the sleep event to the df_sleep_calc_list
            current_row_list.append(sleep)
        df_sleep_calc_list.append(current_row_list)
    df_sleep_calc = pd.DataFrame(df_sleep_calc_list, columns=['Date_Time', 'zt_time'] + available_channels)
    
    df_sleep_calc['mean'] = df_sleep_calc[available_channels].mean(axis=1)
    df_sleep_calc['sem'] = df_sleep_calc[available_channels].sem(axis=1)
    
    #st.write(df_sleep_calc)
    avg_sleep_df = df_sleep_calc.copy()
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

    ind_day_night = df_sleep_calc.copy()
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


    ind_sleep_bout_list = []

    for col in available_channels:
        #for col in ['data_10']:
        print(col)
        
        # loop through df_sleep_calc and determine when it switches from 1 to 0 or 0 to 1

        # get the first value of the column
        current_time = df_sleep_calc.iloc[0]['Date_Time']
        current_value = df_sleep_calc.iloc[0][col]
        #print(f"start_value={current_value}")
        for i in range(1, len(df_sleep_calc)):
        #for i in range(1, 1000):
            if df_sleep_calc.iloc[i-1][col] != df_sleep_calc.iloc[i][col]:
                #sleep_switch_list.append(df_sleep_calc.iloc[i]['zt_time'])
                #print(f"sleep_switch_list={sleep_switch_list}")
                new_value = df_sleep_calc.iloc[i][col]
                            
                # calcluate the time difference between the current and previous time
                bout_time = (df_sleep_calc.iloc[i]['Date_Time'] - current_time)
                
                # convert timedelta to minutes
                bout_time = bout_time.total_seconds() / 60
                
                #print(f"new_value={new_value}, current_time={current_time}, bout_time={bout_time}")
                ind_sleep_bout_list.append([col, current_time, new_value, bout_time])
                
                current_value = df_sleep_calc.iloc[i][col]
                current_time = df_sleep_calc.iloc[i]['Date_Time']
                #print(f"current_value={current_value}")
    ind_sleep_bout_df = pd.DataFrame(ind_sleep_bout_list, columns=['Channel', 'Time', 'Value', 'Bout_Length'])
    st.header("Individual Sleep Bout")
    st.write(ind_sleep_bout_df)
