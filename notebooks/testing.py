from functools import reduce
import pandas as pd
import streamlit as st

file1 = "/home/twall5/sleep_analysis-3/examples/Monitor9.txt"

# Read in the file
df = pd.read_csv(file1, sep="\t", header=None)

#Remove the 7th, 8th, 9th, 10th, 11th, and 12th collumns
df = df.drop(columns=[6, 7, 8, 9, 10, 11])

#Only keep the first 5 columns
df = df.iloc[:, :5]

st.write(df)