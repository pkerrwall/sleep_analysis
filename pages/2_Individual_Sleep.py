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

orig_df = st.sidebar.file_uploader("Choose a file")

st.sidebar.download_button(
    "Download Individual Sleep Analysis Example", Path("examples/shiny_tool/sleep_analysis_results/Individual_day_night_sleep.csv").read_text(), 
    "individual_sleep.csv", "text/csv", key="example-2-file-download"
)

if orig_df is not None:
        
    #Read in dataframe
    df = pd.read_csv(orig_df)

    #Get the number
    df['Channel#'] = df['Channel'].str.replace(".*_ch", "", regex=True).astype(int)

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

