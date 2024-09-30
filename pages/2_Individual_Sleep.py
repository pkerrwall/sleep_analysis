from pathlib import Path
import streamlit as st
import pandas as pd
import plotly.express as px
from natsort import index_natsorted
import matplotlib.pyplot as plt
import numpy as np
import argparse
import os



st.title('Individuial Sleep Analysis')

orig_df = st.sidebar.file_uploader("Choose a file", type=['csv'])

st.sidebar.download_button(
    "Download Individual Sleep Analysis Example", Path("examples/individual_sleep.csv").read_text(), 
    "individual_sleep.csv", "text/csv", key="example-2-file-download"
)

if orig_df is not None:
        
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