import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta, time
import plotly.express as px

if "condition_name" not in st.session_state:
    st.session_state.condition_name = "Condition 1"
    
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

def fill_sleep_counts(prev_value):
    if prev_value == 0:
        return 1
    else:
        return 0

def fill_bouts(bout_length):
    if bout_length > 0:
        return 1
    else:
        return 0

def convert_zt_to_dec(zt):
    return zt.hour * 60 + zt.minute

#load condition name
condition_name = st.session_state.condition_name

col1, col2, col3, col4 = st.columns(4)

with col1:
    plot_conditions = st.radio("Conditions on a plot", ["Overlap", "Split"])
    Display_dates = st.radio("Display dates on a plot", ["Yes", "No"])

with col2:
    SEM_error = st.radio("Display SEM error bars", ["Yes", "No"], index=0)
    Sleep_profile = st.radio("X-axis average sleep profile time scale", ["Data aquisition time", "Zeitgeber time"], index=1)

with col3:
    Bin_sleep_profile = st.slider("Bin sleep profile data points into average [min]", min_value=1, max_value=120, value=30)
    Max_value_of_sleep_displayed = st.slider("Max value of sleep displayed", min_value=0.0, max_value=1.2, value=1.2)

with col4:
    Plot_height = st.slider("Plot height [pixel]", min_value=10, max_value=1000, value=400)
    Plot_width = st.slider("Plot width [pixel]", min_value=400, max_value=3000, value=1400)


if st.button("Generate Sleep Analysis"):
     # ---------------------------------------------------------------
    # This section is executed when the "Generate Sleep Analysis" button is pressed.
    # It prepares the data for all analysis tabs:
    # - Loads and processes the main sleep analysis DataFrame from session state.
    # - Applies Zeitgeber time calculations and sets up the data for plotting and analysis.
    # - Prepares data for each tab: Average Sleep, Individual Sleep, Sleep Bout, and Raw Data.
    # ---------------------------------------------------------------

    # Create tabs for each section
    tab1, tab2, tab3, tab4 = st.tabs(["Average Sleep", "Individual Sleep", "Sleep Bout", "Raw Data"])
    
    sleep_analysis_df = st.session_state.sleep_analysis_df
    sleep_analysis_df['zt_time'] = sleep_analysis_df['Date_Time'].apply(zeitgeber_time)
    numeric_cols = st.session_state.numeric_cols
    sleep_analysis_df.columns = ['Index', 'Date', 'Time', 'LDD-DD', 'Status', 'Monitor_Number', 'Extras', 'Tube_Number', 'Data_Type', 'Light_Sensor', 'ch1', 'ch2', 'ch3', 'ch4', 'ch5', 'ch6', 'ch7', 'ch8', 'ch9', 'ch10', 'ch11', 'ch12', 'ch13', 'ch14', 'ch15', 'ch16', 'ch17', 'ch18', 'ch19', 'ch20', 'ch21', 'ch22', 'ch23', 'ch24', 'ch25', 'ch26', 'ch27', 'ch28', 'ch29', 'ch30', 'ch31', 'ch32', 'Date_Time', 'LD_DD', 'zt_time']
    df_sleep_trim = sleep_analysis_df[['Date_Time', 'zt_time'] + list(numeric_cols)]
    unavailable_channels = st.session_state.unavailble_channels
    available_channels = st.session_state.available_channels
    df_sleep_trim_alive = df_sleep_trim.drop(unavailable_channels, axis=1)
    df_sleep_trim_alive = df_sleep_trim_alive.set_index('Date_Time')
    numeric_df_sleep_trim_alive = df_sleep_trim_alive.select_dtypes(include=['number'])
    sleep_calc_df = numeric_df_sleep_trim_alive.rolling(5).sum().applymap(lambda x: 1 if x == 0 else 0)
    sleep_calc_df['zt_time'] = df_sleep_trim_alive.index.to_series().apply(zeitgeber_time)
    sleep_calc_df = sleep_calc_df.reset_index()
    sleep_calc_df['mean'] = sleep_calc_df[available_channels].mean(axis=1)
    sleep_calc_df['sem'] = sleep_calc_df[available_channels].sem(axis=1)

    with tab1:
        st.header('Average Sleep Analysis')
        col1, col2 = st.columns(2)

        with col1:
            # Average Sleep List
            
            avg_sleep_df = sleep_calc_df.copy()
            avg_sleep_df['time'] = avg_sleep_df['Date_Time'].dt.time
            avg_sleep_df = avg_sleep_df[['time', 'mean']]
            avg_sleep_df.sort_values('time', inplace=True)
            avg_sleep_df.reset_index(drop=True, inplace=True)
            bin = Bin_sleep_profile
            avg_sleep_list = []
            for i in range(0, len(avg_sleep_df), bin):
                start_time = pd.to_datetime(i, unit='m').time()
                end_time = pd.to_datetime(i+bin-1, unit='m').time()
                mean_values = avg_sleep_df[(avg_sleep_df['time'] >= start_time) & (avg_sleep_df['time'] <= end_time)]['mean'].tolist()
                bin_mean = sum(mean_values) / len(mean_values)
                bin_sem = pd.Series(mean_values).sem()
                avg_sleep_list.append([i, bin_mean, bin_sem])
            avg_sleep_list_df = pd.DataFrame(avg_sleep_list, columns=['time', 'mean', 'sem'])
            avg_sleep_list_df['zt_time'] = pd.to_datetime(avg_sleep_list_df['time'], unit='m').dt.time

            #only keep the first instances of each zt_time
            avg_sleep_list_df = avg_sleep_list_df.drop_duplicates(subset='zt_time', keep='first')

            #add a Condition column with the condition name
            avg_sleep_list_df['Condition'] = condition_name

            #Make the columns go in the order of time, zt_time, condition, mean, sem
            avg_sleep_list_df = avg_sleep_list_df[['time', 'zt_time', 'Condition', 'mean', 'sem']]
            avg_sleep_list_df.columns = ['Time', 'ZT_Time', 'Condition', 'Mean','SEM']

            #change the names of the columns to Dec_time, Dec_ZT_time, Condition, mean_binned_sleep, sem_binned_sleep
            avg_sleep_list_df.columns = ['Dec_time', 'Dec_ZT_time', 'Condition', 'mean_binned_sleep','sem_binned_sleep']

            #convert zt_time to actual zeigterberg time. it should start at 0 when dec_time is at 360 and then add 30 to each interval after that
            avg_sleep_list_df['Dec_ZT_time'] = avg_sleep_list_df['Dec_time'].apply(lambda x: x/60)
            avg_sleep_list_df['Dec_ZT_time'] = avg_sleep_list_df['Dec_ZT_time'] - 6
            avg_sleep_list_df['Dec_ZT_time'] = avg_sleep_list_df['Dec_ZT_time'].apply(lambda x: x if x >= 0 else x + 24)
            #multiply Dec_zt_time by 60
            avg_sleep_list_df['Dec_ZT_time'] = avg_sleep_list_df['Dec_ZT_time'] * 60

            st.write("Average Sleep List")
            st.write(avg_sleep_list_df)

            csv = avg_sleep_list_df.to_csv(index=False)

            #add a download button
            st.download_button(
                label="Download average sleep list as CSV",
                data=csv,
                file_name='avg_sleep_list.csv',
                mime='text/csv'
                )
            
            
            # Sort Dec_ZT_time column in chronological order
            avg_sleep_list_df = avg_sleep_list_df.sort_values(by="Dec_ZT_time")

            # Convert Dec_ZT_time to hours
            hours = avg_sleep_list_df['Dec_ZT_time'] / 60
            avg_sleep_list_df['ZT_time_in_hours'] = hours

            # Calculate Sleep_30min and SEM_30min
            avg_sleep_list_df['Sleep_30min'] = avg_sleep_list_df['mean_binned_sleep'] * 30
            avg_sleep_list_df['SEM_30min'] = avg_sleep_list_df['sem_binned_sleep'] * 30
    
            # remove the 'Unamed: 0' column
            #avg_sleep_list_df = avg_sleep_list_df.drop(columns=['Unnamed: 0'])

            #Clone table
            table1 = avg_sleep_list_df.copy()
            st.write(avg_sleep_list_df)
            #Make a download data button
            st.download_button('Download Entire Table', avg_sleep_list_df.to_csv(), file_name='average_sleep.csv', mime='text/csv')

            #Get all unique conditions in table1
            conditions = table1['Condition'].unique()
            #Make a dropdown menu for the user to select a condition
            condition = st.selectbox('Select a condition', conditions)
            #Filter table1 to only include the selected condition
            table1 = table1[table1['Condition'] == condition]
            #Move the condition column to the front of the table
            first_column = table1.pop('Condition')
            table1.insert(0, 'Condition', first_column)
            st.write(table1)
            #Make a download button for table1
            st.download_button('Download Specific Column', table1.to_csv(), file_name='average_sleep.csv', mime='text/csv')

            #def scatter_plot (save, Label, table):
            #figure = table
    
            # create plotly express scatter plot
            fig = px.scatter(avg_sleep_list_df, x='ZT_time_in_hours', y='Sleep_30min', error_y='SEM_30min', title='Average Sleep', labels={'ZT_time_in_hours':'ZT time in hours', 'Sleep_30min':'Sleep per 30min'})
            st.plotly_chart(fig)
            
        """
        with col2:
            st.write("Average Sleep profiles in LD")

            table = avg_sleep_list_df

            # Sort Dec_ZT_time column in chronological order
            table = table.sort_values(by="Dec_ZT_time")

            # Convert Dec_ZT_time to hours
            hours = table['Dec_ZT_time'] / 60
            table['ZT_time_in_hours'] = hours

            # Calculate Sleep_30min and SEM_30min
            table['Sleep_30min'] = table['mean_binned_sleep'] * 30
            table['SEM_30min'] = table['sem_binned_sleep'] * 30
            
            # remove the 'Unamed: 0' column
            #table = table.drop(columns=['Unnamed: 0'])

            #Clone table
            table1 = table.copy()
            st.write(table)
            #Make a download data button
            st.download_button('Download Table', table.to_csv(), file_name='average_sleep.csv', mime='text/csv')

            #Get all unique conditions in table1
            conditions = table1['Condition'].unique()
            #Make a dropdown menu for the user to select a condition
            condition = st.selectbox('Select condition', conditions)
            #Filter table1 to only include the selected condition
            table1 = table1[table1['Condition'] == condition]
            #Move the condition column to the front of the table
            first_column = table1.pop('Condition')
            table1.insert(0, 'Condition', first_column)
            st.write(table1)
            #Make a download button for table1
            st.download_button('Download Specific Collumn', table1.to_csv(), file_name='average_sleep.csv', mime='text/csv')

            #def scatter_plot (save, Label, table):
            #figure = table
            
            # create plotly express scatter plot
            fig2 = px.scatter(table, x='ZT_time_in_hours', y='Sleep_30min', error_y='SEM_30min', title='Average Sleep', labels={'ZT_time_in_hours':'ZT time in hours', 'Sleep_30min':'Sleep per 30min'})
            st.plotly_chart(fig2)
        """
    with tab2:

        st.header('Individual Sleep Analysis')
        col1, col2 = st.columns(2)
        with col1:
            # Individual Day/Night Mean
            def day_night(dt):
                if dt.time() >= pd.to_datetime('06:00').time() and dt.time() <= pd.to_datetime('18:00').time():
                    return 'Day'
                else:
                    return 'Night'
            ind_day_night = sleep_calc_df.copy()
            ind_day_night['Day_Night'] = ind_day_night['Date_Time'].apply(day_night)
            ind_day_night = ind_day_night[['Day_Night'] + available_channels]
            ind_day_night_unpivoted = ind_day_night.melt(id_vars=['Day_Night'], value_vars=available_channels, var_name='Channel', value_name='Counts')
            ind_day_night_mean = ind_day_night_unpivoted.groupby(['Day_Night', 'Channel'])['Counts'].mean().reset_index()
            ind_day_night_mean.sort_values(['Channel', 'Day_Night'], inplace=True)
            ind_day_night_mean.reset_index(drop=True, inplace=True)

            #add the condition column
            ind_day_night_mean['Condition'] = condition_name

            #Make the columns go bo the order of Channel, Condition, Light_status, mean_sleep_per_ind
            ind_day_night_mean = ind_day_night_mean[['Channel', 'Condition', 'Day_Night', 'Counts']]
            ind_day_night_mean.columns = ['Channel', 'Condition', 'Light_status', 'mean_sleep_per_ind']


            st.write("Individual Day/Night Mean")
            st.write(ind_day_night_mean)
        with col2:
            st.write("Individual Sleep Profiles in LD")
            
            df = ind_day_night_mean

            #Get the number
            df['Channel#'] = df['Channel'].str.extract(r'(\d+)$').astype(int)

            #Sort it by Day/Night column and then by Channel# column
            df = df.sort_values(by=['Light_status', 'Channel#'])

            #Sort it by the column "Condition"

            #Make a new dataframe takes each Channel# and its corresponding Light_stats sleep status
            #This means that the new dataframe should only have 3 columns, the channel#, the day_mean_sleep_per_ind, and the night_mean_sleep_per_ind
            #The day or night mean_slep_per_ind is the one that corresponds to the Light_status column
            df_new = pd.DataFrame()
            df_new['Channel#'] = df['Channel#'].unique()
            day_df = df[df['Light_status'] == 'Day'][['Channel#', 'mean_sleep_per_ind']].rename(columns={'mean_sleep_per_ind': 'day_mean_sleep_per_ind'})
            night_df = df[df['Light_status'] == 'Night'][['Channel#', 'mean_sleep_per_ind']].rename(columns={'mean_sleep_per_ind': 'night_mean_sleep_per_ind'})
            df_new = pd.merge(day_df, night_df, on='Channel#', how='outer').fillna(0)

            #Add on the "Condition" column to the new dataframe, sort it by that column
            df_new = pd.merge(df_new, df[['Channel#', 'Condition']].drop_duplicates(), on='Channel#', how='outer').fillna(0)


            #Make it so that the Channel# column is the index
            df_new = df_new.set_index('Channel#')

            #Multiply day/night mean_sleep_per_ind by 30 to get sleep/30 for both day/day
            #label these columns day_sleep_per_30, night_sleep_per_30
            df_new['day_sleep_per_30'] = df_new['day_mean_sleep_per_ind'] * 30
            df_new['night_sleep_per_30'] = df_new['night_mean_sleep_per_ind'] * 30

            #Multiply mean_sleep_per_ind by 720 to get total sleep(min) for botbh day and night data
            #label these columns day_total_sleep(min), night_total_sleep(min)
            df_new['day_total_sleep(min)'] = df_new['day_mean_sleep_per_ind'] * 720
            df_new['night_total_sleep(min)'] = df_new['night_mean_sleep_per_ind'] * 720

            #add both day_total_sleep(min) and night_total_sleep(min) to get total_sleep(min)
            #Divide total_sleep(min) by 60 to get total_sleep_per_day
            df_new['total_sleep(min)'] = df_new['day_total_sleep(min)'] + df_new['night_total_sleep(min)']
            df_new['total_sleep_per_day'] = df_new['total_sleep(min)'] / 60

            #Create a new dataframe called data_df that has the following columns: Channel#, day_sleep_per_30, night_sleep_per_30, total_sleep_per_day
            data_df = pd.DataFrame()
            data_df['Channel#'] = df_new.index

            #Add back the condition column
            data_df['Condition'] = df_new['Condition'].values

            data_df['day_sleep_per_30'] = df_new['day_sleep_per_30'].values
            data_df['night_sleep_per_30'] = df_new['night_sleep_per_30'].values
            data_df['total_sleep_per_day'] = df_new['total_sleep_per_day'].values

            #again, make it so that the Channel# column is the index
            data_df = data_df.set_index('Channel#')

            #Sort the data_df by the conditions column
            data_df = data_df.sort_values(by='Condition')

            data_df1 = data_df.copy()

            #Get each unique condition
            conditions = data_df['Condition'].unique()

            #Make a drop down menu for the user to select the condition
            condition = st.selectbox('Select Condition', conditions)

            #Filter the data_df by the selected condition
            data_df = data_df[data_df['Condition'] == condition]



            #Show data_df dataframe on the streamlit with an option to download it
            st.write(data_df)
            st.download_button('Download Data', data_df.to_csv(), 'data.csv', 'text/csv')

            #Add the conditions to the dataframe and print that one, make a button to download everything
            st.write(data_df1)
            st.download_button('Download Data with Conditions', data_df1.to_csv(), 'data_with_conditions.csv', 'text/csv')



    with tab3:
        # Individual Sleep Bout
        bout_data = []
        for col in available_channels:
            changes = sleep_calc_df[col].diff().fillna(0).apply(lambda x: 1 if x != 0 else 0)
            change_indices = changes[changes == 1].index
            prev_value = sleep_calc_df.at[change_indices[0], col] if change_indices.size > 0 else None
            prev_time = sleep_calc_df.at[change_indices[0], 'Date_Time'] if change_indices.size > 0 else None
            for idx in change_indices:
                current_value = sleep_calc_df.at[idx, col]
                current_time = sleep_calc_df.at[idx, 'Date_Time']
                zt_time = zeitgeber_time(prev_time)
                if prev_value is not None and prev_value != current_value:
                    bout_length = (current_time - prev_time).total_seconds() / 60
                    bout_data.append({
                        'Channel': col,
                        'Condition': 'wt',
                        'Light_Cycle': 'LD',
                        'Date': 'NA',
                        'Time': prev_time,
                        'ZT_Time': zt_time,
                        'Dec_ZT_Time': convert_zt_to_dec(zt_time),
                        'Value': prev_value,
                        'Sleep_Count': fill_sleep_counts(prev_value),
                        'Bout': fill_bouts(bout_length),
                        'Bout_Length': bout_length
                    })
                prev_value = current_value
                prev_time = current_time
        ind_sleep_bout_df = pd.DataFrame(bout_data)
        st.header("Sleep Bout Analysis")
        
        

        # split the Time column into a Date and Time column
        ind_sleep_bout_df['Time'] = pd.to_datetime(ind_sleep_bout_df['Time'])
        ind_sleep_bout_df['Date'] = ind_sleep_bout_df['Time'].dt.date
        ind_sleep_bout_df['Time'] = ind_sleep_bout_df['Time'].dt.time
        ind_sleep_bout_df['ZT_Time'] = ind_sleep_bout_df['ZT_Time'].dt.time
        print(ind_sleep_bout_df)

        st.write(ind_sleep_bout_df)

        #give an option to download the data in this format
        st.download_button('Download Sleep Bout Table', ind_sleep_bout_df.to_csv(), 'sleep_bout.csv', 'text/csv')

        start_date = ind_sleep_bout_df['Date'].iloc[0]
        end_date = ind_sleep_bout_df['Date'].iloc[-1]

        # create list of unique Channel
        channels = ind_sleep_bout_df['Channel'].unique()
        
        # add multi-select for day, night, or both with both selected by default
        day_or_night = st.multiselect('Day or Night', ['day', 'night'], default=['day', 'night'])
    
        # check if day_or_night is empty and then add day and night back in
        if len(day_or_night) == 0:
            day_or_night = ['day', 'night']

        # filter sleep_count = 0
        ind_sleep_bout_df = ind_sleep_bout_df[ind_sleep_bout_df['Sleep_Count'] != 0]

        # filter rows where bout_length < 5
        ind_sleep_bout_df = ind_sleep_bout_df[ind_sleep_bout_df['Bout_Length'] >= 5]

        # create column called 'day_or_night' where Dec_ZT_time = 0 to 720 is day, DecZT_time 721 to 1080 is night
        ind_sleep_bout_df['day_or_night'] = ind_sleep_bout_df['Dec_ZT_Time'].apply(lambda x: 'day' if x < 720 else 'night')

        # filter by day or night
        ind_sleep_bout_df = ind_sleep_bout_df[ind_sleep_bout_df['day_or_night'].isin(day_or_night)]

        
        # filter by date range - make sure to convert date_range to date format
        ind_sleep_bout_df = ind_sleep_bout_df[(ind_sleep_bout_df['Date'] >= start_date) & (ind_sleep_bout_df['Date'] <= end_date)]

        # create column bout_lengths/sleep_counts
        ind_sleep_bout_df['bout_length_per_sleep_counts'] = ind_sleep_bout_df['Bout_Length'] / ind_sleep_bout_df['Sleep_Count']

        # create a column called 'channel_num' where Monitor9_ch1 is 1, Monitor9_ch2 is 2, etc.
        ind_sleep_bout_df['channel_num'] = ind_sleep_bout_df['Channel'].apply(lambda x: int(x.split('ch')[-1]))

        # group by time_of_day, channel, date and then sum and average bout and bout_length
        grouped = ind_sleep_bout_df.groupby(['day_or_night', 'Channel', 'channel_num', 'Condition', 'Date']).agg({'Bout': ['sum'], 'Bout_Length': ['sum', 'mean']}).reset_index()

        # sort grouped by channel_num and date
        grouped = grouped.sort_values(['day_or_night','channel_num', 'Date'])

        # format bout_length mean to 2 decimal places
        grouped['Bout_Length', 'mean'] = grouped['Bout_Length', 'mean'].apply(lambda x: round(x, 2))

        # transform the multi-index columns to single index
        grouped.columns = ['_'.join(col).strip() for col in grouped.columns.values]

        # replace columns that end with '_' with ''
        grouped.columns = grouped.columns.str.replace('_$', '', regex=True)

        # create a new grouped dataframe that is grouped by day_or_night, channel_num and averages bout sum and bout_length mean
        grouped2 = grouped.groupby(['day_or_night', 'Channel', 'channel_num', 'Condition']).agg({'Bout_sum': ['mean'], 'Bout_Length_mean': ['mean']}).reset_index()

        # sort by channel_num
        grouped2 = grouped2.sort_values(['day_or_night', 'channel_num'])

        # transform the multi-index columns to single index
        grouped2.columns = ['_'.join(col).strip() for col in grouped2.columns.values]

        # replace columns that end with '_' with ''
        grouped2.columns = grouped2.columns.str.replace('_$', '', regex=True)

        # format bout_sum_mean and bout_length_mean_mean to 2 decimal places
        grouped2['Bout_sum_mean'] = grouped2['Bout_sum_mean'].apply(lambda x: round(x, 2))
        grouped2['Bout_Length_mean_mean'] = grouped2['Bout_Length_mean_mean'].apply(lambda x: round(x, 2))

        #Group the header by the collumn "Condition"
        grouped2 = grouped2.sort_values(by=['Condition'])


        # create 2 streamlit columns
        col1, col2 = st.columns(2)

        
        #Move the condition collumn to the second collumn in both grouped and grouped2
        grouped = grouped[['day_or_night', 'Condition', 'Channel', 'channel_num', 'Date', 'Bout_sum', 'Bout_Length_sum', 'Bout_Length_mean']]
        grouped2 = grouped2[['day_or_night', 'Condition', 'Channel', 'channel_num', 'Bout_sum_mean', 'Bout_Length_mean_mean']]

        #make copies of grouped and grouped 2
        grouped1 = grouped.copy()
        grouped2_1 = grouped2.copy()

        #Sort each by the condition column
        grouped1 = grouped.sort_values(by='Condition')
        grouped2_1 = grouped2.sort_values(by='Condition')


        # print the grouped dataframe
        col1.header('Grouped By Day')

        # add download link for grouped dataframe
        col1.download_button('Download Grouped Data', grouped.to_csv(index=False), 'grouped.csv', 'text/csv')

        # create plotly express density plot
        fig = px.density_contour(grouped, x='Bout_Length_mean', y='Bout_sum', marginal_x='histogram', marginal_y='histogram')
        col1.plotly_chart(fig)
        col1.dataframe(grouped, hide_index=True)

        # print the grouped2 dataframe
        col2.header('Grouped By Channel')

        
        # add download link for grouped2 dataframe
        col2.download_button('Download Grouped2 Data', grouped2.to_csv(index=False), 'grouped2.csv', 'text/csv')

        # create plotly express density plot
        fig = px.density_contour(grouped2, x='Bout_sum_mean', y='Bout_Length_mean_mean', marginal_x='histogram', marginal_y='histogram')
        col2.plotly_chart(fig)

        # print the dataframe without the index
        col2.dataframe(grouped2, hide_index=True)

        #Get each unique conditions in grouped1
        conditions = grouped1['Condition'].unique()
        #Get each unique conditions in grouped2_1
        conditions2 = grouped2_1['Condition'].unique()
        #Make a drop down of both conditions and conditions2
        condition = col1.selectbox('Select Condition for day', conditions)
        condition2 = col2.selectbox('Select Condition for night', conditions2)
        #Filter the grouped1 dataframe by the selected condition
        grouped1 = grouped1[grouped1['Condition'] == condition]
        #Filter the grouped2_1 dataframe by the selected condition
        grouped2_1 = grouped2_1[grouped2_1['Condition'] == condition2]
        #Show the grouped1 dataframe
        col1.dataframe(grouped1, hide_index=True)
        #Show the grouped2_1 dataframe
        col2.dataframe(grouped2_1, hide_index=True)
        #Add a download button for both grouped1 and grouped2_1
        col1.download_button('Download Grouped Day Data', grouped1.to_csv(index=False), 'grouped1.csv', 'text/csv')
        col2.download_button('Download Grouped Night Data', grouped2_1.to_csv(index=False), 'grouped2_1.csv', 'text/csv')
