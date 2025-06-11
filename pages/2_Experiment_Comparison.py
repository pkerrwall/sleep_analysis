import streamlit as st
import pickle
import os
import matplotlib.pyplot as plt

SAVE_ANALYSIS_PATH = "saved_analysis"

def list_saved_analyses():
    os.makedirs(SAVE_ANALYSIS_PATH, exist_ok=True)
    return [f.replace("_analysis.pkl", "") for f in os.listdir(SAVE_ANALYSIS_PATH) if f.endswith("_analysis.pkl")]

def load_analysis(experiment_name):
    path = os.path.join(SAVE_ANALYSIS_PATH, f"{experiment_name}_analysis.pkl")
    if os.path.exists(path):
        with open(path, 'rb') as f:
            return pickle.load(f)
    return None

st.set_page_config(layout="wide")
st.title("Compare Monitor Analyses")

all_experiments = list_saved_analyses()
selected_experiments = st.multiselect("Select two or more monitor analyses to compare", all_experiments)

if len(selected_experiments) >= 1:
    cols = st.columns(len(selected_experiments))
    
    for i, experiment in enumerate(selected_experiments):
        analysis = load_analysis(experiment)
        with cols[i]:
            st.subheader(f"Experiment: {experiment}")
            if not analysis:
                st.warning("Failed to load analysis.")
                continue

            # --- Metadata ---
            st.markdown(f"**Condition:** {analysis.get('condition_name')}")
            st.markdown(f"**Saved:** {analysis.get('saved_time')}")

            # --- Summary Locomotor Activity ---
            # --- Summary Locomotor Activity ---
            st.markdown("**Summary Locomotor Activity**")
            st.pyplot(analysis.get('fig_summary_locomotor'))

            # --- Locomotor by Day ---
            st.markdown("**Locomotor Activity by Day**")
            st.pyplot(analysis.get('fig_by_day_activity'))
            st.dataframe(analysis.get('locomotor_activity_by_day'))

            # --- Sleep Grouped Night ---
            st.markdown("**Sleep Grouped Night**")
            st.pyplot(analysis.get('fig_sleep_grouped_night'))
            st.dataframe(analysis.get('df_by_LD_DD'))

            # --- Average Sleep ---
            st.markdown("**Average Sleep**")
            st.dataframe(analysis.get('avg_sleep_list_df'))

            # --- Individual Day/Night Mean ---
            st.markdown("**Individual Sleep (Day/Night Mean)**")
            st.dataframe(analysis.get('ind_day_night_mean'))

            # --- Sleep Bout Table ---
            st.markdown("**Sleep Bouts**")
            st.dataframe(analysis.get('ind_sleep_bout_df'))

            # --- Sleep Bout Plots ---
            st.markdown("**Sleep Bout Plots (Grouped by Day)**")
            st.plotly_chart(analysis.get('fig_sleep_bout_by_day'), key=f"fig_sleep_bout_by_day_{experiment}")

            st.markdown("**Sleep Bout Plots (Grouped by Channel)**")
            st.plotly_chart(analysis.get('fig_sleep_bout_by_channel'), key=f"fig_sleep_bout_by_channel_{experiment}")

            st.markdown("**Sleep Bouts Grouped by Day**")
            st.dataframe(analysis.get('sleep_grouped'), key=f"sleep_grouped_{experiment}")

            st.markdown("**Sleep Bouts Grouped by Channel**")
            st.dataframe(analysis.get('sleep_grouped2'), key=f"sleep_grouped2_{experiment}")