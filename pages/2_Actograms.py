import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
import pickle
from io import BytesIO


SAVE_ANALYSIS_PATH = "saved_analysis"  # make sure this matches your folder name

def list_saved_analyses():
    os.makedirs(SAVE_ANALYSIS_PATH, exist_ok=True)
    return [f.replace("_analysis.pkl", "") for f in os.listdir(SAVE_ANALYSIS_PATH) if f.endswith("_analysis.pkl")]

def load_analysis(experiment_name):
    path = os.path.join(SAVE_ANALYSIS_PATH, f"{experiment_name}_analysis.pkl")
    if os.path.exists(path):
        with open(path, 'rb') as f:
            data = pickle.load(f)
            metadata = data.get("metadata", {})
            condition = metadata.get("condition_name", "Unknown")
            data['Experiment'] = experiment_name
            data['Condition'] = condition
            return data
    return None

def create_horizontal_actogram(df, channels, bin_minutes=5, stat='mean', color='#0D22EE'):
    df = df.copy()
    df['ZT'] = (df['Date_Time'].dt.hour * 60 + df['Date_Time'].dt.minute) / 60
    df['Date'] = df['Date_Time'].dt.date

    df = df[['Date', 'ZT'] + channels]

    if stat == 'mean':
        df['activity'] = df[channels].mean(axis=1)
    elif stat == 'median':
        df['activity'] = df[channels].median(axis=1)

    df['ZT_bin'] = (df['ZT'] // (bin_minutes / 60)) * (bin_minutes / 60)
    grouped = df.groupby(['Date', 'ZT_bin'])['activity'].mean().reset_index()

    unique_dates = grouped['Date'].unique()
    n_days = len(unique_dates)

    fig, axes = plt.subplots(nrows=n_days, figsize=(10, 1.5 * n_days), sharex=True)

    if n_days == 1:
        axes = [axes]

    for ax, date in zip(axes, unique_dates):
        day_data = grouped[grouped['Date'] == date]
        ax.bar(day_data['ZT_bin'], day_data['activity'], width=bin_minutes / 60, color=color)
        ax.set_yticks([])
        ax.set_ylabel(str(date), rotation=0, ha='right', va='center')
        ax.set_xlim(0, 24)

    fig.suptitle("Mean Actograms", fontsize=14)
    fig.supxlabel("ZT Time (h)")
    plt.tight_layout()
    return fig


st.set_page_config(page_title="Experiment Actograms", layout="wide")
st.title("📊 Actogram Viewer by Experiment")

saved_experiments = list_saved_analyses()
selected_experiment = st.selectbox("Select a saved analysis", saved_experiments)

if selected_experiment:
    loaded_data = load_analysis(selected_experiment)
    if loaded_data and 'sleep_analysis_df' in loaded_data:
        df = loaded_data['sleep_analysis_df']
        df['Date_Time'] = pd.to_datetime(df['Date_Time'])

        available_channels = [col for col in df.columns if col.startswith("ch")]

        st.markdown(f"### Experiment: {selected_experiment} — Condition: {loaded_data['Condition']}")

        stat_option = st.selectbox("Statistic", ["mean", "median"])
        bin_size = st.slider("Bin size (minutes)", 1, 60, 5)
        color = st.color_picker("Color", "#0D22EE")
        select_all = st.checkbox("Select all channels", value=True)

        # Channel selector
        if select_all:
            selected_channels = available_channels
        else:
            selected_channels = st.multiselect("Channels to include", available_channels, default=available_channels[:1])

        if selected_channels:
            fig = create_horizontal_actogram(df, selected_channels, bin_minutes=bin_size, stat=stat_option, color=color)
            st.pyplot(fig)

            buf = BytesIO()
            fig.savefig(buf, format="png")
            st.download_button("📥 Download Actogram PNG", data=buf.getvalue(), file_name=f"{selected_experiment}_actogram.png", mime="image/png")
        else:
            st.warning("Please select at least one channel.")
    else:
        st.warning("This saved analysis does not include a sleep_analysis_df.")