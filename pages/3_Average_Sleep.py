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


orig_df = st.sidebar.file_uploader("Choose a file", type=['csv'])
st.sidebar.download_button(
    "Download Average Sleep Example", Path("examples/average_sleep.csv").read_text(), 
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
    st.write(table)

    #def scatter_plot (save, Label, table):
    #figure = table
    
    # create plotly express scatter plot
    fig = px.scatter(table, x='ZT_time_in_hours', y='Sleep_30min', error_y='SEM_30min', title='Average Sleep', labels={'ZT_time_in_hours':'ZT time in hours', 'Sleep_30min':'Sleep per 30min'})
    st.plotly_chart(fig)