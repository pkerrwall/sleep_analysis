#!/usr/bin/env python3
#found shebang line on https://stackoverflow.com/questions/6908143/should-i-put-shebang-in-python-scripts-and-what-form-should-it-take
import pandas as pd
import numpy as np
from natsort import index_natsorted
import matplotlib.pyplot as plt
import argparse
import os
import streamlit as st

# Load the data
def csv_loaded (file):
    table = pd.read_csv(file)
    return table

#Dec_ZT_time column in chronological order
def sort_chrono (file):
    table = csv_loaded(file)
    table = table.sort_values(by="Dec_ZT_time",key=lambda x: np.argsort(index_natsorted(table["Dec_ZT_time"])))
    return table

#add new column called ZT_time_in_hours by dividing Dec_ZT_time by 60
def add_hours (file):
    table = sort_chrono(file)
    hours = table['Dec_ZT_time']/60
    table['ZT_time_in_hours'] = hours
    return table

#add new column called mean_binned_sleep by multiplying mean_sleep by 30
def add_sleep_30min (file):
    table = add_hours(file)
    table['Sleep_30min'] = table['mean_binned_sleep']*30
    return table

#add new column called SEM_30min by multiplying sem_binned_sleep by 30 (Average Sleep Table Complete)
def complete_table (file):
    table = add_sleep_30min(file)
    table['SEM_30min'] = table['sem_binned_sleep']*30
    return table

#generate scatterplot; Used Github & Microsoft CoPilot for reference
def scatter_plot (file, save, Label):
    figure = complete_table(file)
    plt.plot(figure['ZT_time_in_hours'],figure['Sleep_30min'],color=args.color, label=Label)
    plt.errorbar(figure['ZT_time_in_hours'],figure['Sleep_30min'],yerr=figure['SEM_30min'],fmt='.',color='black',ecolor='black',elinewidth=0.5,capsize=2)
    plt.xlabel('ZT time in hours')
    plt.xticks(np.arange(0,26,5))
    plt.ylabel('Sleep per 30min')
    plt.yticks(np.arange(0,31,5))
    plt.title('Average Sleep')
    plt.legend()
    plt.savefig(save + '.png')

#argument parser for input; Used Github & Microsoft CoPilot for reference
fdir = os.path.dirname(os.path.abspath(__file__))
parser = argparse.ArgumentParser()
parser.add_argument('-f', '--file', type=str, required=True)
parser.add_argument('-s', '--save', type=str, required=True)
parser.add_argument('-c', '--color', type=str, default='black', required=False)
parser.add_argument('-l', '--label', type=str, default='WT', required=False)
args = parser.parse_args()
function = complete_table(fdir + '/' + args.file)
function.to_csv(fdir + '/' + args.save, index=False)
function2 = scatter_plot(fdir + '/' + args.file, fdir + '/' + args.save, args.label)
print('Analyzed file saved as ' + args.save)
print('Scatterplot saved as ' + args.save + '.png')

st.header('Average Sleep')
st.write(function)
st.write(function2)

