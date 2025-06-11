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

st.set_page_config(layout="wide")
st.title("🧪 Final Universal Monitor Analysis Comparison")

all_experiments = list_saved_analyses()
selected_experiments = st.multiselect("Select two or more monitor analyses to compare", all_experiments)

if len(selected_experiments) >= 1:

    # -------- SUMMARY LOCOMOTOR ACTIVITY --------
    summary_combined = pd.DataFrame()
    for experiment in selected_experiments:
        analysis = load_analysis(experiment)
        df = analysis.get('daily_locomotor_activity')
        if df is not None:
            df = df.copy()
            df['Experiment'] = experiment
            df['Condition'] = analysis['Condition']
            summary_combined = pd.concat([summary_combined, df], ignore_index=True)

    if not summary_combined.empty:
        st.header("Summary Locomotor Activity by Condition")
        st.dataframe(summary_combined)

        y_col = 'Mean' if 'Mean' in summary_combined.columns else 'mean'
        fig_summary = px.bar(summary_combined, x='Condition', y=y_col, color='Condition', barmode='group')
        st.plotly_chart(fig_summary)

    # -------- LOCOMOTOR ACTIVITY BY DAY --------
    locomotor_combined = pd.DataFrame()
    for experiment in selected_experiments:
        analysis = load_analysis(experiment)
        df = analysis.get('locomotor_activity_by_day')
        if df is not None:
            df = df.copy()
            df['Experiment'] = experiment
            df['Condition'] = analysis['Condition']
            locomotor_combined = pd.concat([locomotor_combined, df], ignore_index=True)

    if not locomotor_combined.empty:
        st.header("Locomotor Activity by Day")
        st.dataframe(locomotor_combined)

        agg = locomotor_combined.groupby(['Condition', 'Date']).agg({'mean':'mean'}).reset_index()
        fig = px.bar(agg, x='Date', y='mean', color='Condition', barmode='group')
        st.plotly_chart(fig)

    # -------- SLEEP GROUPED NIGHT --------
    sleep_night_combined = pd.DataFrame()
    for experiment in selected_experiments:
        analysis = load_analysis(experiment)
        df = analysis.get('df_by_LD_DD')
        if df is not None:
            df = df.copy()
            df['Experiment'] = experiment
            df['Condition'] = analysis['Condition']
            sleep_night_combined = pd.concat([sleep_night_combined, df], ignore_index=True)

    if not sleep_night_combined.empty:
        st.header("Sleep Grouped Night")
        st.dataframe(sleep_night_combined)
        fig2 = px.bar(sleep_night_combined, x='Light_status', y='mean', color='Condition', barmode='group')
        st.plotly_chart(fig2)

    # -------- AVERAGE SLEEP --------
    avg_sleep_combined = pd.DataFrame()
    for experiment in selected_experiments:
        analysis = load_analysis(experiment)
        df = analysis.get('avg_sleep_list_df')
        if df is not None:
            df = df.copy()
            df['Experiment'] = experiment
            df['Condition'] = analysis['Condition']
            avg_sleep_combined = pd.concat([avg_sleep_combined, df], ignore_index=True)

    if not avg_sleep_combined.empty:
        st.header("Average Sleep (Combined)")
        st.dataframe(avg_sleep_combined)

    # -------- INDIVIDUAL SLEEP DAY/NIGHT --------
    daynight_combined = pd.DataFrame()
    for experiment in selected_experiments:
        analysis = load_analysis(experiment)
        df = analysis.get('ind_day_night_mean')
        if df is not None:
            df = df.copy()
            df['Experiment'] = experiment
            df['Condition'] = analysis['Condition']
            daynight_combined = pd.concat([daynight_combined, df], ignore_index=True)

    if not daynight_combined.empty:
        st.header("Individual Sleep Day/Night Mean (Combined)")
        st.dataframe(daynight_combined)

    # -------- SLEEP BOUT TABLE + METRICS --------
    bout_combined = pd.DataFrame()
    for experiment in selected_experiments:
        analysis = load_analysis(experiment)
        df = analysis.get('ind_sleep_bout_df')
        if df is not None:
            df = df.copy()
            df['Experiment'] = experiment
            df['Condition'] = analysis['Condition']
            bout_combined = pd.concat([bout_combined, df], ignore_index=True)

    if not bout_combined.empty:
        st.header("Bout Length / Bout Number Summary")
        st.dataframe(bout_combined)

        # Only sleep bouts (Value == 1) if applicable
        sleep_bouts = bout_combined[bout_combined['Value'] == 1] if 'Value' in bout_combined.columns else bout_combined
        sleep_group = sleep_bouts.groupby(['Condition']).agg({
            'Bout_Length': ['mean', compute_sem],
            'Bout': ['mean', compute_sem]
        }).reset_index()

        sleep_group.columns = ['Condition', 'Mean_bout_length', 'SEM_length', 'Mean_bout_number', 'SEM_number']

        fig_len = px.bar(sleep_group, x='Condition', y='Mean_bout_length', color='Condition',
                         error_y='SEM_length', barmode='group',
                         title='Sleep Bout Length (min)')
        st.plotly_chart(fig_len)

        fig_num = px.bar(sleep_group, x='Condition', y='Mean_bout_number', color='Condition',
                         error_y='SEM_number', barmode='group',
                         title='Sleep Bout Number')
        st.plotly_chart(fig_num)

    # -------- SLEEP GROUPED BY DAY --------
    grouped_day_combined = pd.DataFrame()
    for experiment in selected_experiments:
        analysis = load_analysis(experiment)
        df = analysis.get('sleep_grouped')
        if df is not None:
            df = df.copy()
            df['Experiment'] = experiment
            df['Condition'] = analysis['Condition']
            grouped_day_combined = pd.concat([grouped_day_combined, df], ignore_index=True)

    if not grouped_day_combined.empty:
        st.header("Sleep Bouts Grouped by Day")
        st.dataframe(grouped_day_combined)

        agg_day = grouped_day_combined.groupby(['Condition', 'Date']).agg({'Bout_Length_mean': 'mean'}).reset_index()
        fig3 = px.bar(agg_day, x='Date', y='Bout_Length_mean', color='Condition', barmode='group')
        st.plotly_chart(fig3)

    # -------- SLEEP GROUPED BY CHANNEL --------
    grouped_channel_combined = pd.DataFrame()
    for experiment in selected_experiments:
        analysis = load_analysis(experiment)
        df = analysis.get('sleep_grouped2')
        if df is not None:
            df = df.copy()
            df['Experiment'] = experiment
            df['Condition'] = analysis['Condition']
            grouped_channel_combined = pd.concat([grouped_channel_combined, df], ignore_index=True)

    if not grouped_channel_combined.empty:
        st.header("Sleep Bouts Grouped by Channel")
        st.dataframe(grouped_channel_combined)

        agg_channel = grouped_channel_combined.groupby(['Condition', 'Channel']).agg({'Bout_Length_mean_mean':'mean'}).reset_index()
        fig4 = px.bar(agg_channel, x='Channel', y='Bout_Length_mean_mean', color='Condition', barmode='group')
        st.plotly_chart(fig4)
