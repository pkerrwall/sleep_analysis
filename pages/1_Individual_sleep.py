from pathlib import Path
import streamlit as st
import pandas as pd
import plotly.express as px
from natsort import index_natsorted
import matplotlib.pyplot as plt
import numpy as np
import argparse
import os



st.header('Sleep Analysis')

#option = st.sidebar.success('Please select an option from the dropdown menu')
#Make the options Option A, Option B, and Option C
#input = st.sidebar.selectbox('Select an option', ['Option A', 'Option B', 'Option C'])

orig_df = st.sidebar.file_uploader("Choose a file", type=['csv'])






if orig_df is None:
    st.sidebar.download_button(
    "Download individual sleep", Path("examples/Individual_sleep.csv").read_text(), 
    "Individual_sleep.csv", "text/csv", key="example-2-file-download"
    )
else:
        
    #Read in dataframe
    df = pd.read_csv(orig_df)

    #Get the number
    df['Channel#'] = df['Channel'].str.replace("Monitor7_ch", "").astype(int)

    #Sort it by Day/Night column and then by Channel# column
    df = df.sort_values(by=['Light_status', 'Channel#'])

    #Make a new dataframe takes each Channel# and its corresponding Light_stats sleep status
    #This means that the new dataframe should only have 3 columns, the channel#, the day_mean_sleep_per_ind, and the night_mean_sleep_per_ind
    #The day or night mean_slep_per_ind is the one that corresponds to the Light_status column
    df_new = pd.DataFrame()
    df_new['Channel#'] = df['Channel#'].unique()
    df_new['day_mean_sleep_per_ind'] = df[df['Light_status'] == 'Day']['mean_sleep_per_ind'].values
    df_new['night_mean_sleep_per_ind'] = df[df['Light_status'] == 'Night']['mean_sleep_per_ind'].values

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
    data_df['day_sleep_per_30'] = df_new['day_sleep_per_30'].values
    data_df['night_sleep_per_30'] = df_new['night_sleep_per_30'].values
    data_df['total_sleep_per_day'] = df_new['total_sleep_per_day'].values

    #again, make it so that the Channel# column is the index
    data_df = data_df.set_index('Channel#')


    #Show data_df dataframe on the streamlit with an option to download it
    st.write(data_df)
    st.download_button('Download Data', data_df.to_csv(), 'data.csv', 'text/csv')

# with tab3:

#     st.download_button(
#     "Download option 3 file", Path("/home/twall5/sleep_analysis/Notebooks/Average_sleep_profiles_in_LD_analyzed.csv").read_text(), 
#     "example.csv", "text/csv", key="example-3-file-download"
#     )

#     if orig_df is not None:
#         #Read in dataframe
#         table = pd.read_csv(orig_df)

#         #Dec_ZT_time column in chronological order
#         table = table.sort_values(by="Dec_ZT_time",key=lambda x: np.argsort(index_natsorted(table["Dec_ZT_time"])))

#         hours = table['Dec_ZT_time']/60
#         table['ZT_time_in_hours'] = hours

#         table['Sleep_30min'] = table['mean_binned_sleep']*30

#         table['SEM_30min'] = table['sem_binned_sleep']*30

#         st.write(table)

#         def scatter_plot (save, Label, table):
#             figure = table
#             plt.plot(figure['ZT_time_in_hours'],figure['Sleep_30min'],color=args.color, label=Label)
#             plt.errorbar(figure['ZT_time_in_hours'],figure['Sleep_30min'],yerr=figure['SEM_30min'],fmt='.',color='black',ecolor='black',elinewidth=0.5,capsize=2)
#             plt.xlabel('ZT time in hours')
#             plt.xticks(np.arange(0,26,5))
#             plt.ylabel('Sleep per 30min')
#             plt.yticks(np.arange(0,31,5))
#             plt.title('Average Sleep')
#             plt.legend()
#             plt.savefig(save + '.png')

#         st.write(scatter_plot(orig_df, 'Average_Sleep', 'WT'))
        
# with tab1:
        

#     # add upload in sidebar

#     # add link to download the example file in examples/Individual_sleep_activity_bout_data.csv
#     # st.sidebar.download_button(
#     #     "Download example file", Path("examples/Individual_sleep_activity_bout_data.csv").read_text(), 
#     #     "example.csv", "text/csv", key="example-file-download"
#     # )

#     st.download_button(
#     "Download example file", Path("examples/Individual_sleep_activity_bout_data.csv").read_text(), 
#     "example.csv", "text/csv", key="example-file-download"
#     )

#     # if the user has uploaded a file then do the rest of this script
#     if orig_df is not None:
#             #Check to see which tab is selected and run the corresponding code
#         #I want this part to be for option1 but I dont want everything to be put into the sidebar I want it all to be put into the main page

#         # set the index_col to 0
#         orig_df = pd.read_csv(orig_df, index_col=0)

#         # open input file
#         #orig_df = pd.read_csv('/home/shared/projects/sleep_analysis/Individual_sleep_activity_bout_data.csv', index_col=0)

#         # change date to date
#         orig_df['date'] = pd.to_datetime(orig_df['date'])

#         # make a copy
#         df = orig_df.copy()

#         # create list of unique Channel
#         channels = df['Channel'].unique()

#         # create 2 columns for the multiselects
#         #col1, col2, col3, col4 = st.columns(4)

#         # add sidebar with multi-select for day, night, or both with both selected by default
#         #day_or_night = col1.multiselect('Day or Night', ['day', 'night'], default=['day', 'night'])
#         day_or_night = st.sidebar.multiselect('Day or Night', ['day', 'night'], default=['day', 'night'])
        
#         # check if day_or_night is empty and then add day and night back in
#         if len(day_or_night) == 0:
#             day_or_night = ['day', 'night']

#         # create date range slider for date
#         start_date = pd.to_datetime(st.sidebar.date_input('Start Date', df['date'].min()))
#         end_date = pd.to_datetime(st.sidebar.date_input('End Date', df['date'].max()))

#         # add select for channels with all selected by default
#         #selected_channels = st.multiselect('Select Channels', channels, default=channels)

#         # filter sleep_count = 0
#         df = df[df['sleep_counts'] != 0]

#         # filter rows where bout_length < 5
#         df = df[df['bout_length'] >= 5]

#         # create column called 'day_or_night' where Dec_ZT_time = 0 to 720 is day, DecZT_time 721 to 1080 is night
#         df['day_or_night'] = df['Dec_ZT_time'].apply(lambda x: 'day' if x < 720 else 'night')

#         # filter by day or night
#         df = df[df['day_or_night'].isin(day_or_night)]

#         # filter by Channel based on the selected_channels
#         #df = df[df['Channel'].isin(selected_channels)]

#         # filter by date range - make sure to convert date_range to date format
#         df = df[(df['date'] >= start_date) & (df['date'] <= end_date)]

#         # create column bout_lengths/sleep_counts
#         df['bout_length_per_sleep_counts'] = df['bout_length'] / df['sleep_counts']

#         # create a column called 'channel_num' where Monitor9_ch1 is 1, Monitor9_ch2 is 2, etc.
#         df['channel_num'] = df['Channel'].apply(lambda x: int(x.split('_ch')[-1]))

#         # group by time_of_day, channel, date and then sum and average bout and bout_length
#         grouped = df.groupby(['day_or_night', 'Channel', 'channel_num', 'Condition', 'date']).agg({'bout': ['sum'], 'bout_length': ['sum', 'mean']}).reset_index()

#         # sort grouped by channel_num and date
#         grouped = grouped.sort_values(['day_or_night','channel_num', 'date'])

#         # format bout_length mean to 2 decimal places
#         grouped['bout_length', 'mean'] = grouped['bout_length', 'mean'].apply(lambda x: round(x, 2))

#         # transform the multi-index columns to single index
#         grouped.columns = ['_'.join(col).strip() for col in grouped.columns.values]

#         # replace columns that end with '_' with ''
#         grouped.columns = grouped.columns.str.replace('_$', '', regex=True)

#         # create a new grouped dataframe that is grouped by day_or_night, channel_num and averages bout sum and bout_length mean
#         grouped2 = grouped.groupby(['day_or_night', 'Channel', 'channel_num', 'Condition']).agg({'bout_sum': ['mean'], 'bout_length_mean': ['mean']}).reset_index()

#         # sort by channel_num
#         grouped2 = grouped2.sort_values(['day_or_night', 'channel_num'])

#         # transform the multi-index columns to single index
#         grouped2.columns = ['_'.join(col).strip() for col in grouped2.columns.values]

#         # replace columns that end with '_' with ''
#         grouped2.columns = grouped2.columns.str.replace('_$', '', regex=True)

#         # format bout_sum_mean and bout_length_mean_mean to 2 decimal places
#         grouped2['bout_sum_mean'] = grouped2['bout_sum_mean'].apply(lambda x: round(x, 2))
#         grouped2['bout_length_mean_mean'] = grouped2['bout_length_mean_mean'].apply(lambda x: round(x, 2))

#         # create 2 streamlit columns
#         col1, col2 = st.columns(2)

#         # print the grouped dataframe
#         col1.header('Grouped By Day')
        
#         # add download link for grouped dataframe
#         col1.download_button('Download Grouped Data', grouped.to_csv(index=False), 'grouped.csv', 'text/csv')

#         # create plotly express density plot
#         fig = px.density_contour(grouped, x='bout_length_mean', y='bout_sum', marginal_x='histogram', marginal_y='histogram')
#         col1.plotly_chart(fig)
#         col1.dataframe(grouped, hide_index=True)

#         # print the grouped2 dataframe
#         col2.header('Grouped By Channel')
        
#         # add download link for grouped2 dataframe
#         col2.download_button('Download Grouped2 Data', grouped2.to_csv(index=False), 'grouped2.csv', 'text/csv')

#         # create plotly express density plot
#         fig = px.density_contour(grouped2, x='bout_sum_mean', y='bout_length_mean_mean', marginal_x='histogram', marginal_y='histogram')
#         col2.plotly_chart(fig)

#         # print the dataframe without the index
#         col2.dataframe(grouped2, hide_index=True)
#         #I want this part to be for option2 but I dont want everything to be put into the sidebar I want it all to be put into the main page
    