import streamlit as st
import pickle
import os
import pandas as pd
import numpy as np
import plotly.express as px

SAVE_ANALYSIS_PATH = "saved_analysis"

# ---------- Utility functions ----------
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

def compute_sem(series):
    return series.std(ddof=1) / np.sqrt(len(series))

# ---------- UI ----------
st.set_page_config(page_title="View Experiment", layout="wide")
st.title("View Single Monitor Experiment")

all_experiments = list_saved_analyses()
selected_experiment = st.selectbox("Select a monitor experiment to view", all_experiments)

if selected_experiment:
    analysis = load_analysis(selected_experiment)
    condition = analysis['Condition']

    
    # -------- Metadata --------
    st.header("📋 Metadata")
    metadata = analysis.get('metadata', {})
    if metadata:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"**Condition:** `{metadata.get('condition_name', 'N/A')}`")
            st.markdown(f"**Monitor:** `{metadata.get('monitor_name', 'N/A')}`")
        with col2:
            st.markdown(f"**Start Date:** `{metadata.get('start_date', 'N/A')}`")
            st.markdown(f"**End Date:** `{metadata.get('end_date', 'N/A')}`")
        with col3:
            st.markdown(f"**LD/DD Cycle:** `{metadata.get('ld_dd_analysis', 'N/A')}`")
            st.markdown(f"**Light Onset:** `{metadata.get('light_onset', 'N/A')}`")
    else:
        st.info("No metadata found in this experiment.")

    # -------- Summary Locomotor Activity --------
    df = analysis.get('daily_locomotor_activity')
    if df is not None:
        st.header("Summary Locomotor Activity")
        st.dataframe(df)
        y_col = 'Mean' if 'Mean' in df.columns else 'mean'
        fig_summary = px.bar(df, x='Channel' if 'Channel' in df.columns else df.index, 
                             y=y_col, color_discrete_sequence=['#1f77b4'], title=f"{condition} - Summary Activity")
        st.plotly_chart(fig_summary)

    # -------- Locomotor Activity by Day --------
    df = analysis.get('locomotor_activity_by_day')
    if df is not None:
        st.header("Locomotor Activity by Day")
        st.dataframe(df)
        fig = px.bar(df, x='Date', y='mean', color_discrete_sequence=['#1f77b4'], title="Mean Activity by Day")
        st.plotly_chart(fig)

    # -------- Sleep Grouped Night --------
    df = analysis.get('df_by_LD_DD')
    if df is not None:
        st.header("Sleep Grouped Night")
        st.dataframe(df)
        fig2 = px.bar(df, x='Light_status', y='mean', color_discrete_sequence=['#1f77b4'], title="Grouped Sleep: Light vs Dark")
        st.plotly_chart(fig2)

    # -------- Average Sleep --------
    df = analysis.get('avg_sleep_list_df')
    if df is not None:
        st.header("Average Sleep")
        st.dataframe(df)

    # -------- Individual Sleep Day/Night --------
    df = analysis.get('ind_day_night_mean')
    if df is not None:
        st.header("Individual Sleep: Day/Night Mean")
        st.dataframe(df)

    # -------- Sleep Bout Table & Metrics --------
    df = analysis.get('ind_sleep_bout_df')
    if df is not None:
        st.header("Sleep Bout Table")
        st.dataframe(df)

        # Only sleep bouts (Value == 1) if applicable
        sleep_bouts = df[df['Value'] == 1] if 'Value' in df.columns else df
        sleep_group = sleep_bouts.groupby(['Condition']).agg({
            'Bout_Length': ['mean', compute_sem],
            'Bout': ['mean', compute_sem]
        }).reset_index()
        sleep_group.columns = ['Condition', 'Mean_bout_length', 'SEM_length', 'Mean_bout_number', 'SEM_number']

        fig_len = px.bar(sleep_group, x='Condition', y='Mean_bout_length', error_y='SEM_length',
                         title='Bout Length', color_discrete_sequence=['#1f77b4'])
        st.plotly_chart(fig_len)

        fig_num = px.bar(sleep_group, x='Condition', y='Mean_bout_number', error_y='SEM_number',
                         title='Bout Number', color_discrete_sequence=['#1f77b4'])
        st.plotly_chart(fig_num)

    # -------- Sleep Grouped by Day --------
    df = analysis.get('sleep_grouped')
    if df is not None:
        st.header("Sleep Bouts Grouped by Day")
        st.dataframe(df)
        agg_day = df.groupby(['Date']).agg({'Bout_Length_mean': 'mean'}).reset_index()
        fig3 = px.bar(agg_day, x='Date', y='Bout_Length_mean', title="Bout Length by Day", color_discrete_sequence=['#e377c2'])
        st.plotly_chart(fig3)

    # -------- Sleep Grouped by Channel --------
    df = analysis.get('sleep_grouped2')
    if df is not None:
        st.header("Sleep Bouts Grouped by Channel")
        st.dataframe(df)
        agg_channel = df.groupby(['Channel']).agg({'Bout_Length_mean_mean':'mean'}).reset_index()
        fig4 = px.bar(agg_channel, x='Channel', y='Bout_Length_mean_mean', title="Bout Length by Channel", color_discrete_sequence=['#17becf'])
        st.plotly_chart(fig4)
