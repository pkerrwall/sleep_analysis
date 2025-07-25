# 🔁 FULL ACTOGRAM IMPLEMENTATION (MEAN, MEDIAN, INDIVIDUAL)
# This version replaces ShinyR-DAM actogram code with a Python/Streamlit equivalent

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO
import os
from datetime import datetime
from matplotlib.ticker import MultipleLocator
import pickle

# You may already have this
SAVE_ANALYSIS_PATH = "saved_analysis"


# ------------------------- UTILITY HELPERS ----------------------------

def get_dam_settings():
    settings = st.session_state.get("monitor_settings", {})
    return settings.get("dam_settings", {}), settings.get("ld_dd_settings", {})

def identify_alive_dead_channels(df, threshold, frequency):
    """Return list of alive and dead channels based on daily total counts."""
    channels = [c for c in df.columns if c.startswith("ch")]
    counts = df[channels].groupby(df['Date_Time'].dt.date).sum()
    total_counts = counts.sum()
    alive = total_counts[total_counts > threshold].index.tolist()
    dead = total_counts[total_counts <= threshold].index.tolist()
    return alive, dead


# ------------------------- BINNING AND AGGREGATION ----------------------------

def compute_mean_median_binned(df, channels, frequency, bin_size):
    df = df.copy()
    df['Dec_time'] = ((df['Date_Time'].dt.hour * 60 + df['Date_Time'].dt.minute) // frequency).astype(int)
    df['date'] = df['Date_Time'].dt.date
    df['ZT'] = (df['Date_Time'].dt.hour * 60 + df['Date_Time'].dt.minute) / 60

    # Normalize counts by recording interval (match R logic)
    norm = lambda x: x / frequency
    df['mean'] = df[channels].apply(norm).mean(axis=1)
    df['median'] = df[channels].apply(norm).median(axis=1)

    bin_frames = []
    for stat in ['mean', 'median']:
        binned = (
            df.groupby(['date', 'Dec_time'])[stat]
              .mean()
              .reset_index()
              .sort_values(['date', 'Dec_time'])
        )
        binned['binned_' + stat] = (
            binned[stat]
            .rolling(window=bin_size, min_periods=1)
            .mean()
            .shift(-bin_size//2)
        )
        bin_frames.append(binned[['date', 'Dec_time', 'binned_' + stat]])

    result = pd.concat(bin_frames, axis=1)
    result.columns = ['date', 'Dec_time', 'binned_mean', '_d', '_t', 'binned_median']
    return result[['date', 'Dec_time', 'binned_mean', 'binned_median']]


def compute_individual_binned(df, channel, frequency, bin_size):
    df = df.copy()
    df['Dec_time'] = ((df['Date_Time'].dt.hour * 60 + df['Date_Time'].dt.minute) // frequency).astype(int)
    df['date'] = df['Date_Time'].dt.date
    df['ZT'] = (df['Date_Time'].dt.hour * 60 + df['Date_Time'].dt.minute) / 60
    df['value'] = df[channel] / frequency
    binned = (
        df.groupby(['date', 'Dec_time'])['value']
          .mean()
          .reset_index()
          .sort_values(['date', 'Dec_time'])
    )
    binned['binned_value'] = (
        binned['value']
        .rolling(window=bin_size, min_periods=1)
        .mean()
        .shift(-bin_size//2)
    )
    return binned[['date', 'Dec_time', 'binned_value']]


# ------------------------- PLOTTING ----------------------------

def plot_actograms(df, value_col, plot_type='mean', double=False, max_y=20, height_per_day=2.5, width=10, color="#0D22EE"):
    unique_dates = df['date'].unique()
    n_days = len(unique_dates)

    # Prepare plotting data
    df = df.copy()
    if double:
        df = pd.concat([df, df.copy()], ignore_index=True)
        df['Dec_time'] = df['Dec_time'] + df.groupby('date').cumcount() // len(df['Dec_time'].unique()) * 1440
        df['date2'] = np.repeat(np.arange(1, len(unique_dates)+1), len(df) // (2 * len(unique_dates)))[:len(df)]
        facet_dates = df['date2'].unique()
    else:
        facet_dates = unique_dates

    fig, axes = plt.subplots(nrows=len(facet_dates), figsize=(width, height_per_day * len(facet_dates)), sharex=True)
    if len(facet_dates) == 1:
        axes = [axes]

    for i, ax in enumerate(axes):
        if double:
            day_data = df[df['date2'] == facet_dates[i]]
            x = day_data['Dec_time']
        else:
            day_data = df[df['date'] == facet_dates[i]]
            x = day_data['Dec_time']

        y = day_data[value_col].fillna(0)
        ax.fill_between(x, y, step='mid', color=color, alpha=1.0)
        ax.set_ylim(0, max_y)
        ax.set_xlim(0, 2880 if double else 1440)
        ax.yaxis.set_major_locator(MultipleLocator(max_y // 4))
        ax.set_ylabel("Counts", fontsize=10)
        ax.annotate(str(facet_dates[i]), xy=(1.01, 0.5), xycoords='axes fraction', va='center', fontsize=9)
        ax.grid(True, axis='y', linestyle='--', alpha=0.3)
        ax.tick_params(axis='x', labelsize=9)

    fig.supxlabel("ZT Time (h)", fontsize=12)
    fig.suptitle(f"{plot_type.capitalize()} Actograms", fontsize=14)
    fig.subplots_adjust(hspace=0.4)
    return fig


st.set_page_config(page_title="Actogram Viewer", layout="wide")

saved_files = [f.replace("_analysis.pkl", "") for f in os.listdir(SAVE_ANALYSIS_PATH) if f.endswith("_analysis.pkl")]
selected_file = st.selectbox("Select saved experiment", saved_files)


if selected_file:
    with open(os.path.join(SAVE_ANALYSIS_PATH, f"{selected_file}_analysis.pkl"), 'rb') as f:
        data = pickle.load(f)
        df = data.get('sleep_analysis_df')
        df['Date_Time'] = pd.to_datetime(df['Date_Time'])
        df.rename(columns={f"data_{i}": f"ch{i}" for i in range(1, 33)}, inplace=True)
        available_channels = data.get("available_channels", [])
    df = data.get('sleep_analysis_df')
    df['Date_Time'] = pd.to_datetime(df['Date_Time'])

    dam_settings, ld_dd_settings = get_dam_settings()
    frequency = int(dam_settings.get("dam_frequency", 1))
    dead_threshold = int(dam_settings.get("dead_fly_threshold", 100))

    channel_cols = [col for col in df.columns if col.startswith("data_")]
    alive, dead = identify_alive_dead_channels(df, dead_threshold, frequency)

    alive = [f"ch{str(c).zfill(2)}" for c in alive if not str(c).startswith("ch")]
    dead = [f"ch{str(c).zfill(2)}" for c in dead if not str(c).startswith("ch")]


    st.markdown(f"### Condition: **{data['metadata'].get('condition_name', 'Unknown')}**")

    # UI controls
    col1, col2, col3 = st.columns(3)
    with col1:
        bin_size = st.slider("Bin size (minutes)", 1, 60, 5)
        actogram_type = st.selectbox("Statistic", ["mean", "median", "individual"])
    with col2:
        max_y = st.slider("Max Y-axis (Counts)", 1, 100, 20)
        fly_filter = st.selectbox("Fly subset", ["all", "alive", "dead"])
    with col3:
        double_plot = st.checkbox("Double Plotted (48h)", value=False)
        color = st.color_picker("Actogram color", "#0D22EE")

    plot_height = st.slider("Plot height per day", 1.0, 4.0, 2.5)
    plot_width = st.slider("Plot width", 6.0, 14.0, 10.0)

    # Determine which channels to include
    if fly_filter == "alive":
        channels = available_channels
    elif fly_filter == "dead":
        # Dead = all chXX channels in df, not in available_channels
        all_channels = [col for col in df.columns if col.startswith("ch")]
        channels = [c for c in all_channels if c not in available_channels]
    else:
        # All = all chXX channels present in df
        channels = [col for col in df.columns if col.startswith("ch")]


    if not channels:
        st.warning("No matching channels found for this selection.")
    else:
        if actogram_type in ["mean", "median"]:
            binned = compute_mean_median_binned(df, channels, frequency, bin_size)
            value_col = "binned_mean" if actogram_type == "mean" else "binned_median"
            fig = plot_actograms(binned, value_col, actogram_type, double_plot, max_y, plot_height, plot_width, color)
        else:
            channel = st.selectbox("Select individual channel", channels)
            binned = compute_individual_binned(df, channel, frequency, bin_size)
            fig = plot_actograms(binned, "binned_value", "individual", double_plot, max_y, plot_height, plot_width, color)

        st.pyplot(fig)

        # Download
        buf = BytesIO()
        fig.savefig(buf, format="png")
        st.download_button(
            label="📥 Download Actogram PNG",
            data=buf.getvalue(),
            file_name=f"{selected_file}_actogram.png",
            mime="image/png"
        )