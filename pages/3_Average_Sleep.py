from pathlib import Path
import streamlit as st
import pandas as pd
import plotly.express as px
from natsort import index_natsorted
#import matplotlib.pyplot as plt
import numpy as np
import argparse
import os

# import plotly express
import plotly.express as px


st.title('Average Sleep Analysis')


orig_df = st.sidebar.file_uploader("Choose a file")
st.sidebar.download_button(
    "Download Average Sleep Example", Path("examples/shiny_tool/sleep_analysis_results/Average_sleep_profiles_in_LD.csv").read_text(), 
    "average_sleep.csv", "text/csv", key="example-3-file-download"
)

if orig_df is not None:
    
    #Read in dataframe
    table = pd.read_csv(orig_df)

    #Dec_ZT_time column in chronological order
    table = table.sort_values(by="Dec_ZT_time",key=lambda x: np.argsort(index_natsorted(table["Dec_ZT_time"])))
    hours = table['Dec_ZT_time']/60
    table['ZT_time_in_hours'] = hours
    table['Sleep_30min'] = table['mean_binned_sleep']*30
    table['SEM_30min'] = table['sem_binned_sleep']*30
    
    # remove the 'Unamed: 0' column
    table = table.drop(columns=['Unnamed: 0'])

    #Clone table
    table1 = table.copy()
    st.write(table)
    #Make a download data button
    st.download_button('Download Entire Table', table.to_csv(), file_name='average_sleep.csv', mime='text/csv')

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
    st.download_button('Download Specific Collumn', table1.to_csv(), file_name='average_sleep.csv', mime='text/csv')

    #def scatter_plot (save, Label, table):
    #figure = table
    
    # create plotly express scatter plot
    fig = px.scatter(table, x='ZT_time_in_hours', y='Sleep_30min', error_y='SEM_30min', title='Average Sleep', labels={'ZT_time_in_hours':'ZT time in hours', 'Sleep_30min':'Sleep per 30min'})
    st.plotly_chart(fig)