from pathlib import Path
import streamlit as st
import pandas as pd
import plotly.express as px
from natsort import index_natsorted
import matplotlib.pyplot as plt
import numpy as np
import argparse
import os

# Create the title
st.title('Sleep Bout Analysis')

# File uploader
orig_df = st.sidebar.file_uploader("Choose a file", type=['csv'])
st.sidebar.download_button(
    "Download Sleep Bout Analysis Example", Path("examples/sleep_bout.csv").read_text(), 
    "sleep_bout.csv", "text/csv", key="example-file-download"
)
    
# if the user has uploaded a file then do the rest of this script
if orig_df is not None:

    #Check to see which tab is selected and run the corresponding code
    #I want this part to be for option1 but I dont want everything to be put into the sidebar I want it all to be put into the main page

    # set the index_col to 0
    orig_df = pd.read_csv(orig_df, index_col=0)

    # change date to date
    orig_df['date'] = pd.to_datetime(orig_df['date'])

    # make a copy
    df = orig_df.copy()

    # create list of unique Channel
    channels = df['Channel'].unique()

    # add sidebar with multi-select for day, night, or both with both selected by default
    day_or_night = st.sidebar.multiselect('Day or Night', ['day', 'night'], default=['day', 'night'])
    
    # check if day_or_night is empty and then add day and night back in
    if len(day_or_night) == 0:
        day_or_night = ['day', 'night']

    # create date range slider for date
    start_date = pd.to_datetime(st.sidebar.date_input('Start Date', df['date'].min()))
    end_date = pd.to_datetime(st.sidebar.date_input('End Date', df['date'].max()))

    # add select for channels with all selected by default
    #selected_channels = st.multiselect('Select Channels', channels, default=channels)

    # filter sleep_count = 0
    df = df[df['sleep_counts'] != 0]

    # filter rows where bout_length < 5
    df = df[df['bout_length'] >= 5]

    # create column called 'day_or_night' where Dec_ZT_time = 0 to 720 is day, DecZT_time 721 to 1080 is night
    df['day_or_night'] = df['Dec_ZT_time'].apply(lambda x: 'day' if x < 720 else 'night')

    # filter by day or night
    df = df[df['day_or_night'].isin(day_or_night)]

    # filter by Channel based on the selected_channels
    #df = df[df['Channel'].isin(selected_channels)]

    # filter by date range - make sure to convert date_range to date format
    df = df[(df['date'] >= start_date) & (df['date'] <= end_date)]

    # create column bout_lengths/sleep_counts
    df['bout_length_per_sleep_counts'] = df['bout_length'] / df['sleep_counts']

    # create a column called 'channel_num' where Monitor9_ch1 is 1, Monitor9_ch2 is 2, etc.
    df['channel_num'] = df['Channel'].apply(lambda x: int(x.split('_ch')[-1]))

    # group by time_of_day, channel, date and then sum and average bout and bout_length
    grouped = df.groupby(['day_or_night', 'Channel', 'channel_num', 'Condition', 'date']).agg({'bout': ['sum'], 'bout_length': ['sum', 'mean']}).reset_index()

    # sort grouped by channel_num and date
    grouped = grouped.sort_values(['day_or_night','channel_num', 'date'])

    # format bout_length mean to 2 decimal places
    grouped['bout_length', 'mean'] = grouped['bout_length', 'mean'].apply(lambda x: round(x, 2))

    # transform the multi-index columns to single index
    grouped.columns = ['_'.join(col).strip() for col in grouped.columns.values]

    # replace columns that end with '_' with ''
    grouped.columns = grouped.columns.str.replace('_$', '', regex=True)

    # create a new grouped dataframe that is grouped by day_or_night, channel_num and averages bout sum and bout_length mean
    grouped2 = grouped.groupby(['day_or_night', 'Channel', 'channel_num', 'Condition']).agg({'bout_sum': ['mean'], 'bout_length_mean': ['mean']}).reset_index()

    # sort by channel_num
    grouped2 = grouped2.sort_values(['day_or_night', 'channel_num'])

    # transform the multi-index columns to single index
    grouped2.columns = ['_'.join(col).strip() for col in grouped2.columns.values]

    # replace columns that end with '_' with ''
    grouped2.columns = grouped2.columns.str.replace('_$', '', regex=True)

    # format bout_sum_mean and bout_length_mean_mean to 2 decimal places
    grouped2['bout_sum_mean'] = grouped2['bout_sum_mean'].apply(lambda x: round(x, 2))
    grouped2['bout_length_mean_mean'] = grouped2['bout_length_mean_mean'].apply(lambda x: round(x, 2))

    # create 2 streamlit columns
    col1, col2 = st.columns(2)

    # print the grouped dataframe
    col1.header('Grouped By Day')
    
    # add download link for grouped dataframe
    col1.download_button('Download Grouped Data', grouped.to_csv(index=False), 'grouped.csv', 'text/csv')

    # create plotly express density plot
    fig = px.density_contour(grouped, x='bout_length_mean', y='bout_sum', marginal_x='histogram', marginal_y='histogram')
    col1.plotly_chart(fig)
    col1.dataframe(grouped, hide_index=True)

    # print the grouped2 dataframe
    col2.header('Grouped By Channel')
    
    # add download link for grouped2 dataframe
    col2.download_button('Download Grouped2 Data', grouped2.to_csv(index=False), 'grouped2.csv', 'text/csv')

    # create plotly express density plot
    fig = px.density_contour(grouped2, x='bout_sum_mean', y='bout_length_mean_mean', marginal_x='histogram', marginal_y='histogram')
    col2.plotly_chart(fig)

    # print the dataframe without the index
    col2.dataframe(grouped2, hide_index=True)