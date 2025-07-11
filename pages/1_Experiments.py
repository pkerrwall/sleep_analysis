import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta, time
import os
import json
import pickle
import plotly.express as px
from datetime import datetime
from io import StringIO
import numpy as np
import zipfile
import io

# set wide layout mode
st.set_page_config(layout="wide")

defaults = {
    "condition_name": "",
    "uploaded_files": [],
    "analysis_ran": False,
    # Add others as needed
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

if 'condition_name' not in st.session_state:
    st.session_state.condition_name = ''  # or some default value

SAVE_ANALYSIS_PATH = "saved_analysis"
os.makedirs(SAVE_ANALYSIS_PATH, exist_ok=True)

EXPERIMENT_SAVE_DIR = "saved_experiments"
if not os.path.exists(EXPERIMENT_SAVE_DIR):
    os.makedirs(EXPERIMENT_SAVE_DIR)

def save_experiment(experiment_name, monitor_name, settings, uploaded_file=None):
    # Save uploaded monitor file if it's new
    if uploaded_file:
        save_monitor_file(monitor_name, uploaded_file)

    # Create experiment dict
    experiment_data = {
        "experiment_name": experiment_name,
        "monitor_name": monitor_name,
        "settings": settings
    }

    # Save experiment
    experiment_path = os.path.join(EXPERIMENT_SAVE_DIR, f"{experiment_name}.json")
    with open(experiment_path, 'w') as f:
        json.dump(experiment_data, f, indent=2)

def save_analysis():
    experiment_name = st.session_state.get("experiment_name")
    condition_name = st.session_state.get("condition_name", "unknown")
    monitor_name = st.session_state.get("current_monitor", "unknown")
    save_file_path = os.path.join(SAVE_ANALYSIS_PATH, f"{experiment_name}_analysis.pkl")

    data_to_save = {
        'metadata': {
            "start_date": st.session_state.monitor_settings.get('ld_dd_settings', {}).get('start_date', 'Unknown'),
            'end_date': st.session_state.monitor_settings.get('ld_dd_settings', {}).get('end_date', 'Unknown'),
            'condition_name': condition_name,
            'monitor_name': monitor_name,
            'saved_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'settings': st.session_state.monitor_settings,
            "ld_dd_analysis": st.session_state.monitor_settings.get('ld_dd_analysis', 'Unknown'),
            "light_onset": st.session_state.monitor_settings.get('dam_settings', {}).get('light_onset_time', 'Unknown')
        },
        'daily_locomotor_activity': st.session_state.get('daily_locomotor_activity'),
        'locomotor_activity_by_day': st.session_state.get('locomotor_activity_by_day'),
        'df_by_LD_DD': st.session_state.get('df_by_LD_DD'),
        'sleep_analysis_df': st.session_state.get('sleep_analysis_df'),
        'avg_sleep_list_df': st.session_state.get('avg_sleep_list_df'),
        'ind_day_night_mean': st.session_state.get('ind_day_night_mean'),
        'ind_sleep_bout_df': st.session_state.get('ind_sleep_bout_df'),
        'sleep_grouped': st.session_state.get('grouped'),
        'sleep_grouped2': st.session_state.get('grouped2'),

        # Plots as figure objects
        'fig_summary_locomotor': st.session_state.get('fig_summary'),
        'fig_by_day_activity': st.session_state.get('fig_by_day'),
        'fig_by_LD_DD_activity': st.session_state.get('fig_by_LD_DD'),
        'fig_sleep_grouped_night': st.session_state.get('fig_sleep_grouped_night'),
        'daily_sleep_profile': st.session_state.get('fig_daily_sleep_profile'),
        'average_sleep_profile': st.session_state.get('fig_avg_sleep'),
        'total_sleep_in_LD': st.session_state.get('fig_total_sleep_in_LD'),
        'daytime_sleep_in_LD': st.session_state.get('fig_daytime_sleep_in_LD'),
        'nighttime_sleep_in_LD': st.session_state.get('fig_nighttime_sleep_in_LD'),
        'fig_sleep_bout_by_day': st.session_state.get('fig_sleep_bout_by_day'),
        'fig_sleep_bout_by_channel': st.session_state.get('fig_sleep_bout_by_channel'),
        'fig_avg_bout_length_1': st.session_state.get('fig_avg_bout_length_1'),
        'fig_avg_bout_length_0': st.session_state.get('fig_avg_bout_length_0'),
    }

    with open(save_file_path, 'wb') as f:
        pickle.dump(data_to_save, f)
    st.success(f"Analysis saved as {condition_name}_analysis.pkl")


def load_analysis(condition_name):
    file_path = os.path.join("saved_analysis", f"{condition_name}_analysis.pkl")
    if os.path.exists(file_path):
        with open(file_path, 'rb') as f:
            return pickle.load(f)
    return None

# Create a directory to save monitor files and settings
SAVE_DIR = "saved_monitors"
if not os.path.exists(SAVE_DIR):
    os.makedirs(SAVE_DIR)

DEFAULTS_FILE = "user_defaults.json"

def get_default_monitor_settings():
    DEFAULTS_FILE = "user_defaults.json"
    defaults = {
        "ld_dd_analysis": "LD",
        "ld_dd_settings": {
            "start_date": "2024-01-01",
            "end_date": "2024-01-31",
            "LD_DD_Analysis": "LD"
        },
        "dam_settings": {
            "dam_frequency": 1,
            "dead_fly_threshold": 100,
            "light_onset_time": "06:00"
        },
        "start_offset_days": 0,
        "end_offset_days": 0
    }

    if os.path.exists(DEFAULTS_FILE):
        with open(DEFAULTS_FILE, "r") as f:
            try:
                user_defaults = json.load(f)
                # Map flat structure into nested
                defaults["ld_dd_settings"]["start_date"] = user_defaults.get("start_date", defaults["ld_dd_settings"]["start_date"])
                defaults["ld_dd_settings"]["end_date"] = user_defaults.get("end_date", defaults["ld_dd_settings"]["end_date"])
                defaults["dam_settings"]["dam_frequency"] = user_defaults.get("frequency", defaults["dam_settings"]["dam_frequency"])
                defaults["dam_settings"]["dead_fly_threshold"] = user_defaults.get("threshold", defaults["dam_settings"]["dead_fly_threshold"])
                defaults["dam_settings"]["light_onset_time"] = user_defaults.get("light_onset", defaults["dam_settings"]["light_onset_time"])
                defaults["start_offset_days"] = user_defaults.get("start_offset_days", 0)
                defaults["end_offset_days"] = user_defaults.get("end_offset_days", 0)
            except json.JSONDecodeError:
                pass

    return defaults

# Initialize default settings if none exist
if 'monitor_settings' not in st.session_state:
    st.session_state.monitor_settings = get_default_monitor_settings()

def save_experiment(experiment_name, monitor_name, settings, uploaded_file=None):
    if uploaded_file:
        save_monitor_file(monitor_name, uploaded_file)
    experiment_data = {
        "experiment_name": experiment_name,
        "monitor_name": monitor_name,
        "settings": settings,
        "saved_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    experiment_path = os.path.join(EXPERIMENT_SAVE_DIR, f"{experiment_name}.json")
    with open(experiment_path, 'w') as f:
        json.dump(experiment_data, f, indent=2)

def save_monitor_file(monitor_name, file_data):
    """Save monitor file data"""
    filepath = os.path.join(SAVE_DIR, f"{monitor_name}.pkl")
    with open(filepath, 'wb') as f:
        pickle.dump(file_data, f)

def load_monitor_settings(monitor_name):
    """Load monitor settings from a file"""
    filepath = os.path.join(SAVE_DIR, f"{monitor_name}_settings.json")
    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            return json.load(f)
    return None


def load_monitor_file(monitor_name):
    """Load monitor file data"""
    filepath = os.path.join(SAVE_DIR, f"{monitor_name}.pkl")
    if os.path.exists(filepath):
        with open(filepath, 'rb') as f:
            return pickle.load(f)
    return None

def get_saved_monitors():
    upload_dir = "uploaded_monitors"
    if not os.path.exists(upload_dir):
        return []
    files = os.listdir(upload_dir)
    monitor_files = [os.path.splitext(f)[0] for f in files if f.endswith(('.txt', '.csv', '.xlsx'))]
    return monitor_files

tabA, tabB, tabC = st.tabs(["Create Experiments", "Experiments List", "Experiment Comparison"])

with tabA:

    #Create a header
    st.write("# Settings and Daily Locomotor Activity Analysis")

    # Monitor dropdown
    st.sidebar.subheader("Saved Monitors")
    saved_monitors = get_saved_monitors()
    selected_monitor = st.sidebar.selectbox("Select Saved Monitor", ["None"] + saved_monitors)
    st.sidebar.subheader("Experiment Info")
    experiment_name_input = st.sidebar.text_input("Enter Experiment Name", placeholder="e.g., wt_ld_analysis")

    # Default fallback name if user leaves it blank
    if not experiment_name_input.strip():
        experiment_name = f"experiment_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    else:
        experiment_name = experiment_name_input.strip()

    st.session_state["experiment_name"] = experiment_name

    # Initialize session state for current monitor
    if 'current_monitor' not in st.session_state:
        st.session_state.current_monitor = None
        st.session_state.uploaded_files = []
        st.session_state.analysis_ran = False

    # Load selected monitor if it's different from the current one
    if selected_monitor != "None" and selected_monitor != st.session_state.current_monitor:
        # Clear old widget keys that will be overridden
        keys_to_clear = [k for k in st.session_state.keys() if (
            k.startswith("condition_") or 
            k in ["ld_dd_analysis", "dam_frequency", "dead_fly_threshold", 
                "light_onset_time", "ld_start_date", "ld_end_date", 
                "dd_start_date", "dd_end_date"]
        )]
        for key in keys_to_clear:
            del st.session_state[key]

        # Load monitor file
        file_data = load_monitor_file(selected_monitor)
        if file_data:
            st.session_state.uploaded_files = [file_data]

        # Load monitor settings
        settings = load_monitor_settings(selected_monitor)
        if settings:
            st.session_state.monitor_settings = settings
            st.session_state.current_monitor = selected_monitor

            # Clear num_conditions so Streamlit will use the new value
            if 'num_conditions' in st.session_state:
                del st.session_state['num_conditions']

            # Load number of conditions
            if 'num_conditions' not in st.session_state:
                st.session_state['num_conditions'] = settings.get("num_conditions", 1)

            # Load each condition's values into session state
            conditions = settings.get("conditions", [])
            for i, cond in enumerate(conditions):
                st.session_state[f'condition_{i}_name'] = cond["name"]
                st.session_state[f'condition_{i}_fly_count'] = cond["fly_count"]
                for j, monitor_order in enumerate(cond.get("monitor_order", [])):
                    st.session_state[f'condition_{i}_monitor_{j}_order'] = monitor_order
                for j, color in enumerate(cond.get("plot_colors", [])):
                    st.session_state[f'condition_{i}_monitor_{j}_color'] = color

            # Force UI to reflect updated session state
            st.rerun()


    LD_start = '06:00'
    DD_start = '18:00'

    # --- Create Three Columns ---
    col1, col2, col3 = st.columns(3)

    # --- First Column: Conditions ---
    with col1:
        st.subheader("Condition Details")

        # Number of Conditions
        num_conditions = st.number_input(
            "Enter Number of Conditions", 
            min_value=1, 
            value=st.session_state.get('num_conditions', 1),
            key='num_conditions'
        )
        conditions = []
        for i in range(num_conditions):
            st.write(f"**Condition {i+1}**")
            condition_name = st.text_input(
                f"Condition {i+1} Name", 
                value=st.session_state.get(f'condition_{i}_name', "wt"),
                key=f'condition_{i}_name'
            )

            fly_count = st.number_input(
                f"Number of Flies in Condition {i+1}", 
                min_value=1, 
                value=st.session_state.get(f'condition_{i}_fly_count', 32),
                key=f'condition_{i}_fly_count'
            )

            monitor_order = []
            plot_colors = []

            for j, file in enumerate(st.session_state.get('uploaded_files', [])):
                monitor_order.append(st.text_input(
                    f"Monitor Order for {file.name} (Condition {i+1})", 
                    value=st.session_state.get(f'condition_{i}_monitor_{j}_order', f"Monitor {j+1}"),
                    key=f'condition_{i}_monitor_{j}_order'
                ))

                plot_colors.append(st.color_picker(
                    f"Pick Plot Color for {file.name} (Condition {i+1})", 
                    value=st.session_state.get(f'condition_{i}_monitor_{j}_color', "#BEBEBE"),
                    key=f'condition_{i}_monitor_{j}_color'
                ))
            conditions.append({
                "name": condition_name,
                "fly_count": fly_count,
                "monitor_order": monitor_order,
                "plot_colors": plot_colors
            })

        # Save conditions and number to session
        st.session_state.monitor_settings['num_conditions'] = num_conditions
        st.session_state.monitor_settings['conditions'] = conditions
        
    # --- Second Column: LD-DD Analysis ---
    with col2:
        st.subheader("LD-DD Analysis")
        LD_DD_Analysis = st.radio("LD DD Analysis", ["LD", "DD", "Both"], 
                                index=["LD", "DD", "Both"].index(
                                    st.session_state.monitor_settings.get('ld_dd_analysis', "LD")),
                                key='ld_dd_analysis')

        # Default date range
        min_date = datetime(2024, 1, 1).date()
        max_date = datetime(2024, 1, 31).date()

        # Try to get date range from uploaded files if available
        if st.session_state.uploaded_files or selected_monitor != "None":
            try:
                monitor_name = selected_monitor if selected_monitor != "None" else st.session_state.uploaded_files[0].name.split(".")[0]
                monitor_path = os.path.join("uploaded_monitors", f"{monitor_name}.txt")

                df_temp = pd.read_csv(monitor_path, sep='\t', header=None)
                
                if not df_temp.empty:
                    monitor_settings = get_default_monitor_settings()
                    offset_start = monitor_settings.get("start_offset_days", 0)
                    offset_end = monitor_settings.get("end_offset_days", 0)

                    df_temp.columns = ['Index','Date','Time','LD-DD','Status','Extras','Monitor_Number',
                                    'Tube_Number','Data_Type','Light_Sensor'] + [f'data_{i}' for i in range(1, 33)]
                    df_temp['DateTime'] = pd.to_datetime(df_temp['Date'] + ' ' + df_temp['Time'], 
                                                        format='%d %b %y %H:%M:%S', errors='coerce')
                    min_date = df_temp['DateTime'].min().date() + timedelta(days=offset_start)
                    max_date = df_temp['DateTime'].max().date() + timedelta(days=offset_end)
            except Exception as e:
                st.error(f"Error reading file: {str(e)}")

        if LD_DD_Analysis == "LD":
            ld_start_date = st.date_input("LD Start Date", 
                                        value=st.session_state.monitor_settings.get('ld_start_date', min_date), 
                                        min_value=min_date, 
                                        max_value=max_date,
                                        key='ld_start_date')
            ld_end_date = st.date_input("LD End Date", 
                                    value=st.session_state.monitor_settings.get('ld_end_date', max_date), 
                                    min_value=min_date, 
                                    max_value=max_date,
                                    key='ld_end_date')

            # Convert the date to "24 Feb 24'" format
            ld_start_date = ld_start_date.strftime('%d %b %y')
            ld_end_date = ld_end_date.strftime('%d %b %y')

            start_date = ld_start_date + ' 00:00:00' 
            end_date = ld_end_date + ' 23:59:59'
            
        elif LD_DD_Analysis == "DD":
            dd_start_date = st.date_input("DD Start Date", 
                                        value=st.session_state.monitor_settings.get('dd_start_date', min_date), 
                                        min_value=min_date, 
                                        max_value=max_date,
                                        key='dd_start_date')
            start_date = dd_start_date.strftime('%d %b %y') + ' 00:00:00'
            dd_end_date = st.date_input("DD End Date", 
                                    value=st.session_state.monitor_settings.get('dd_end_date', max_date), 
                                    min_value=min_date, 
                                    max_value=max_date,
                                    key='dd_end_date')
            end_date = dd_end_date.strftime('%d %b %y') + ' 23:59:59'
            
        elif LD_DD_Analysis == "Both":
            ld_start_date = st.date_input("LD Start Date", 
                                        value=st.session_state.monitor_settings.get('ld_start_date', min_date), 
                                        min_value=min_date, 
                                        max_value=max_date,
                                        key='ld_start_date')
            ld_end_date = st.date_input("LD End Date", 
                                    value=st.session_state.monitor_settings.get('ld_end_date', min_date + timedelta(days=14)),
                                    min_value=min_date, 
                                    max_value=max_date,
                                    key='ld_end_date')
            dd_start_date = st.date_input("DD Start Date", 
                                        value=st.session_state.monitor_settings.get('dd_start_date', ld_end_date + timedelta(days=1)),
                                        min_value=ld_end_date + timedelta(days=1), 
                                        max_value=max_date,
                                        key='dd_start_date')
            dd_end_date = st.date_input("DD End Date", 
                                    value=st.session_state.monitor_settings.get('dd_end_date', max_date), 
                                    min_value=dd_start_date, 
                                    max_value=max_date,
                                    key='dd_end_date')

        # Save LD/DD settings to session state
        st.session_state.monitor_settings['ld_dd_settings'] = {
            'start_date': start_date,
            'end_date': end_date,
            'LD_DD_Analysis': LD_DD_Analysis
        }

    # --- Third Column: DAM System Settings ---
    from datetime import time  # make sure this is imported

    with col3:
        st.subheader("DAM System Settings")

        # Load nested DAM defaults correctly
        monitor_settings = get_default_monitor_settings()
        dam_defaults = monitor_settings.get('dam_settings', {})

        dam_frequency = dam_defaults.get('dam_frequency', 1)
        dead_fly_threshold = dam_defaults.get('dead_fly_threshold', 200)
        light_onset_time = dam_defaults.get('light_onset_time', '06:00')

        # Convert light_onset_time to time object if it's a string
        if isinstance(light_onset_time, str):
            light_onset_time = time.fromisoformat(light_onset_time)

        # DAM system data acquisition frequency
        dam_frequency = st.number_input("Enter the frequency in minutes", 
                                        min_value=1, max_value=60, 
                                        value=dam_frequency,
                                        key='dam_frequency')

        # Threshold for identifying dead flies
        dead_fly_threshold = st.number_input("Threshold of Counts per Day", 
                                            min_value=0, 
                                            value=dead_fly_threshold,
                                            key='dead_fly_threshold')

        # Light onset time
        light_onset_time = st.time_input("Enter the light onset time", 
                                        value=light_onset_time,
                                        key='light_onset_time')

        # Save updated DAM settings to session state
        st.session_state.monitor_settings['dam_settings'] = {
            'dam_frequency': dam_frequency,
            'dead_fly_threshold': dead_fly_threshold,
            'light_onset_time': light_onset_time.strftime('%H:%M')
        }

    st.write("# Sleep Analysis")

    col1, col2 = st.columns(2)

    def zeitgeber_time(dt):
        if dt.time() >= pd.to_datetime('06:00').time() and dt.time() <= pd.to_datetime('23:59').time():
            # subtract 6 hours from the time
            six_hours = timedelta(hours=6)
            zt_time = dt - six_hours
        else:
            # add 18 hours to the time
            eighteen_hours = timedelta(hours=18)
            zt_time = dt + eighteen_hours
        return zt_time

    def fill_sleep_counts(prev_value):
        if prev_value == 0:
            return 1
        else:
            return 0

    def fill_bouts(bout_length):
        if bout_length > 0:
            return 1
        else:
            return 0

    def convert_zt_to_dec(zt):
        return zt.hour * 60 + zt.minute

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        plot_conditions = st.radio("Conditions on a plot", ["Overlap", "Split"])
        Display_dates = st.radio("Display dates on a plot", ["Yes", "No"])

    with col2:
        SEM_error = st.radio("Display SEM error bars", ["Yes", "No"], index=0)
        Sleep_profile = st.radio("X-axis average sleep profile time scale", ["Data aquisition time", "Zeitgeber time"], index=1)

    with col3:
        Bin_sleep_profile = st.slider("Bin sleep profile data points into average [min]", min_value=1, max_value=120, value=30)
        Max_value_of_sleep_displayed = st.slider("Max value of sleep displayed", min_value=0.0, max_value=1.2, value=1.2)

    with col4:
        Plot_height = st.slider("Plot height [pixel]", min_value=10, max_value=1000, value=400)
        Plot_width = st.slider("Plot width [pixel]", min_value=400, max_value=3000, value=1400)

    # Only show analysis section if files are uploaded
    if selected_monitor != "None":
        monitor_name = selected_monitor
    elif st.session_state.uploaded_files:
        monitor_name = st.session_state.uploaded_files[0].name.split(".")[0]
    else:
        monitor_name = "UnknownMonitor"

    st.session_state.current_monitor = monitor_name

    # Only show analysis section if files are present
    if st.session_state.uploaded_files or selected_monitor != "None":
        if st.button("Start Analysis"):
            # Only save file data if using uploaded files
            if st.session_state.uploaded_files:
                save_monitor_file(monitor_name, st.session_state.uploaded_files[0])

            # Save settings
            save_experiment(
                experiment_name=experiment_name,
                monitor_name=monitor_name,
                settings=st.session_state.monitor_settings,
                uploaded_file=st.session_state.uploaded_files[0] if st.session_state.uploaded_files else None
            )

            # Update session settings
            st.session_state.monitor_settings.update({
                'num_conditions': num_conditions,
                'conditions': conditions,
                'ld_dd_analysis': LD_DD_Analysis,
                'dam_frequency': dam_frequency,
                'dead_fly_threshold': dead_fly_threshold,
                'light_onset_time': light_onset_time.strftime('%H:%M') if isinstance(light_onset_time, time) else light_onset_time
            })

            st.session_state.analysis_ran = True
            
            all_daily_locomotor_activity = []
            all_locomotor_activity_by_day = []
            all_df_by_LD_DD = []
            all_sleep_analysis_df = []

            channel_columns = [f'ch{i}' for i in range(1, 33)]
            fly_counts = [cond['fly_count'] for cond in st.session_state.monitor_settings['conditions']]
            channel_assignments = []
            start = 0
            for count in fly_counts:
                end = start + count
                channel_assignments.append(channel_columns[start:end])
                start = end

            for idx, cond in enumerate(st.session_state.monitor_settings['conditions']):
                condition_name = cond['name']
                fly_count = cond.get('fly_count', 32)
                assigned_channels = channel_assignments[idx]
                print(f"Processing condition: {condition_name}")
                print(f"Number of flies: {fly_count}")
                # Get filename from session state (you already store monitor_name)
                monitor_filename = f"{monitor_name}.txt"  # Or use uploaded_file.name from metadata
                monitor_filepath = os.path.join("uploaded_monitors", monitor_filename)

                # Load file from disk
                df = pd.read_csv(monitor_filepath, sep='\t', header=None)
                new_df = df.copy()

                # Give the columns names
                df.columns = ['Index','Date','Time','LD-DD','Status','Extras','Monitor_Number','Tube_Number','Data_Type','Light_Sensor','data_1','data_2','data_3','data_4','data_5','data_6','data_7','data_8','data_9','data_10','data_11','data_12','data_13','data_14','data_15','data_16','data_17','data_18','data_19','data_20','data_21','data_22','data_23','data_24','data_25','data_26','data_27','data_28','data_29','data_30','data_31','data_32']

                # Combine the date and time columns, it should look something like '23 Feb 24 11:03:00'
                df['Date'] = df['Date'] + ' ' + df['Time']
                # Get rid of the time column
                df = df.drop(columns=['Time'])
                # Rename the column to Date_Time
                df = df.rename(columns={'Date':'Date_Time'})

                # Convert df_copy Date_Time to a datetime object, the format is day Feb 24 time
                df['Date_Time'] = pd.to_datetime(df['Date_Time'], format='%d %b %y %H:%M:%S')
            
                # Filter on date between start_date & end_date, make sure you include the entire day of end_date
                df = df[(df['Date_Time'] >= pd.to_datetime(start_date)) & (df['Date_Time'] <= pd.to_datetime(end_date))]
            
                # Create a new column called "date" and just put the date in it
                df['Date'] = df['Date_Time'].dt.date

                # Create a new column called "time" and just put the time in it
                df['Time'] = df['Date_Time'].dt.time
                # Create a new column called "Condition" and put the condition in it
                df['Condition'] = condition_name

                # Create a new column called 'Light_Cycle' and just put LD_DD_Analysis in it
                df['Light_Cycle'] = LD_DD_Analysis

                # Rename the Data columns to ch columns, for example make Data_1 = ch1
                df = df.rename(columns={'data_1':'ch1','data_2':'ch2','data_3':'ch3','data_4':'ch4','data_5':'ch5','data_6':'ch6','data_7':'ch7','data_8':'ch8','data_9':'ch9','data_10':'ch10','data_11':'ch11','data_12':'ch12','data_13':'ch13','data_14':'ch14','data_15':'ch15','data_16':'ch16','data_17':'ch17','data_18':'ch18','data_19':'ch19','data_20':'ch20','data_21':'ch21','data_22':'ch22','data_23':'ch23','data_24':'ch24','data_25':'ch25','data_26':'ch26','data_27':'ch27','data_28':'ch28','data_29':'ch29','data_30':'ch30','data_31':'ch31','data_32':'ch32'})
           
                df_condition = df[['Date', 'Time', 'Condition', 'Light_Cycle'] + assigned_channels].copy()

                data_df_total = pd.DataFrame()

                # Get all the days selected in the date range
                days = df_condition['Date'].unique()

                for day in days:
                    # Filter the dataframe for the current day
                    data_df_day = df_condition[df_condition['Date'] == day]

                    # Drop the Date and Time columns
                    data_df_day = data_df_day.drop(columns=['Date', 'Time'])

                    # Add a row at the bottom of the dataframe that is the sum of all the columns
                    data_df_day.loc[day] = data_df_day.sum()

                    # Make Condition and Light_Cycle go back to normal
                    data_df_day['Condition'] = condition_name
                    data_df_day['Light_Cycle'] = LD_DD_Analysis

                    # Add the date back to the total row
                    data_df_day.loc[day, 'Date'] = day

                    # Move date to the front of the dataframe
                    data_df_day = data_df_day[['Date', 'Condition', 'Light_Cycle'] + assigned_channels]

                    # Add the total row to the data_df_total dataframe
                    data_df_total = pd.concat([data_df_total, data_df_day.tail(1)], ignore_index=True)

                # Create a new row that is the mean of all the ch columns
                numeric_cols = assigned_channels  # Exclude 'Condition', 'Light_Cycle', 'Name'
                st.session_state.numeric_cols = numeric_cols
                mean_row = pd.DataFrame(data_df_total[numeric_cols].mean()).T
                mean_row.index = ['Mean']
                mean_row['Date'] = 'Mean'
                mean_row['Condition'] = condition_name
                mean_row['Light_Cycle'] = LD_DD_Analysis
                mean_row = mean_row[['Date', 'Condition', 'Light_Cycle'] + list(numeric_cols)]

                # Append the mean row to the data_df_total dataframe
                data_df_total = pd.concat([data_df_total, mean_row], ignore_index=False)

                data_df_total.columns = [col.strip() for col in data_df_total.columns]
                print("CLEANED FINAL COLUMNS:", data_df_total.columns.tolist())

                n_of_all_flies = fly_count
                n_of_alive_flies = fly_count
                n_of_dead_flies = 0
                # Create a list of available channels
                channel_columns = [f'ch{i}' for i in range(fly_count)]
                available_channels = assigned_channels.copy()
                unavailable_channels = []
                available_channels = [ch.strip() for ch in available_channels]

                # Loop through all the rows except mean, if any of the ch columns is less than counts_per_day_alive, add 1 to n_of_dead_flies
                for index, row in data_df_total.iterrows():
                    if index != 'Mean':
                        for ch in available_channels:
                            if row[ch] < dead_fly_threshold:
                                n_of_dead_flies += 1
                                available_channels.remove(ch)
                                unavailable_channels.append(ch)
                                break
                n_of_alive_flies = n_of_all_flies - n_of_dead_flies
                st.session_state.unavailable_channels = unavailable_channels
                st.session_state.available_channels = available_channels

                # Strip whitespace just in case
                available_channels = [ch.strip() for ch in available_channels]

                # Create a row with the mean for each numeric column
                mean_row = pd.DataFrame(data_df_total[numeric_cols].mean()).T
                mean_row.index = ['Mean']

                # Append the row with a proper index
                data_df_total = pd.concat([data_df_total, mean_row])
                data_df_total.columns = [col.strip() for col in data_df_total.columns]
                available_channels = [ch.strip() for ch in available_channels]
                print("DF Columns:", data_df_total.columns.tolist())
                print("Available channels:", available_channels)
                # Find the Standard Deviation from the available_channels mean
                std = data_df_total[available_channels].std().mean()
                # Find the Standard Error of the Mean (SEM) from the available_channels mean
                sem = std / (n_of_alive_flies ** 0.5)

                mean = data_df_total[available_channels].mean().mean()
                # Create a new dataframe called Daily_locomotor_activity with the columns Condition, Light_Cycle, Mean, SD, SEM, N_of_alive_flies, N_of_dead_flies, N_of_all_flies
                Daily_locomotor_activity = pd.DataFrame(data={'Condition': [condition_name], 'Light_Cycle': [LD_DD_Analysis], 'Mean': [mean], 'SD': [std], 'SEM': [sem], 'N_of_alive_flies': [n_of_alive_flies], 'N_of_dead_flies': [n_of_dead_flies], 'N_of_all_flies': [n_of_all_flies]})

                # Individual Locomotor Activity by Day
                individual_locomotor_activity_day = data_df_total.reset_index()
                # Drop the mean row
                individual_locomotor_activity_day = individual_locomotor_activity_day.drop([individual_locomotor_activity_day.index[-1]])
                # Unpivot the dataframe with Date as the index and the columns as the data_1 - data_32
                locomotor_day_unpivoted = individual_locomotor_activity_day.melt(id_vars=['Date'], value_vars=assigned_channels, var_name='Channel', value_name='Counts')
                locomotor_day_unpivoted_alive = locomotor_day_unpivoted[locomotor_day_unpivoted['Channel'].isin(available_channels)]
                locomotor_activity_by_day = locomotor_day_unpivoted_alive.groupby('Date')['Counts'].agg(['mean', 'sum', 'std', 'sem']).reset_index()
                locomotor_activity_by_day['Condition'] = condition_name
                locomotor_activity_by_day = locomotor_activity_by_day[locomotor_activity_by_day['Date'] != 'Mean']
                locomotor_activity_by_day['Date'] = pd.to_datetime(locomotor_activity_by_day['Date'])

                # Nighttime daytime activity ratio
                new_df.columns = ['Index','Date','Time','LD-DD','Status','Monitor_Number','Extras','Tube_Number','Data_Type','Light_Sensor','data_1','data_2','data_3','data_4','data_5','data_6','data_7','data_8','data_9','data_10','data_11','data_12','data_13','data_14','data_15','data_16','data_17','data_18','data_19','data_20','data_21','data_22','data_23','data_24','data_25','data_26','data_27','data_28','data_29','data_30','data_31','data_32']

                new_df['Date_Time'] = new_df['Date'] + ' ' + new_df['Time']
                new_df['Date_Time'] = pd.to_datetime(new_df['Date_Time'], format='%d %b %y %H:%M:%S')

                # Change Date to date columns with format yyyy-mm-dd
                new_df['Date'] = pd.to_datetime(new_df['Date'], format='%d %b %y')
                new_df['LD_DD'] = new_df['Date_Time'].dt.time
                new_df['LD_DD'] = new_df['LD_DD'].apply(lambda x: 'LD' if x >= pd.to_datetime(LD_start).time() and x <= pd.to_datetime('18:00').time() else 'DD')
                new_df = new_df[(new_df['Date_Time'] >= pd.to_datetime(start_date)) & (new_df['Date_Time'] <= pd.to_datetime(end_date))]
                sleep_analysis_df = new_df.copy()
                sleep_analysis_df['Condition'] = condition_name
                all_sleep_analysis_df.append(sleep_analysis_df)
                new_df = new_df.rename(columns={'data_1':'ch1','data_2':'ch2','data_3':'ch3','data_4':'ch4','data_5':'ch5','data_6':'ch6','data_7':'ch7','data_8':'ch8','data_9':'ch9','data_10':'ch10','data_11':'ch11','data_12':'ch12','data_13':'ch13','data_14':'ch14','data_15':'ch15','data_16':'ch16','data_17':'ch17','data_18':'ch18','data_19':'ch19','data_20':'ch20','data_21':'ch21','data_22':'ch22','data_23':'ch23','data_24':'ch24','data_25':'ch25','data_26':'ch26','data_27':'ch27','data_28':'ch28','data_29':'ch29','data_30':'ch30','data_31':'ch31','data_32':'ch32'})
                df_ld_dd = new_df.groupby(['Date','LD_DD'])[numeric_cols].sum()
                df_ld_dd.reset_index(inplace=True)

                df_melt_ld_dd = df_ld_dd.melt(id_vars=['Date','LD_DD'], value_vars=numeric_cols, var_name='Channel', value_name='Counts')
                df_melt_ld_dd_alive = df_melt_ld_dd[df_melt_ld_dd['Channel'].isin(available_channels)]
                df_by_LD_DD = df_melt_ld_dd_alive.groupby('LD_DD')['Counts'].agg(['mean', 'sem']).reset_index()

                # Add Condition column to the final dataframe
                df_by_LD_DD['Condition'] = condition_name

                #create a session state for condition name
                st.session_state.condition_name = condition_name

                df_by_LD_DD = df_by_LD_DD.rename(columns={'LD_DD': 'Light_status'})

                # Reorder columns to show Condition, Light_status, Mean, and SEM
                df_by_LD_DD = df_by_LD_DD[['Condition', 'Light_status', 'mean', 'sem']]

                all_daily_locomotor_activity.append(Daily_locomotor_activity)
                all_locomotor_activity_by_day.append(locomotor_activity_by_day)
                all_df_by_LD_DD.append(df_by_LD_DD)

            combined_daily_locomotor_activity = pd.concat(all_daily_locomotor_activity, ignore_index=True)
            combined_locomotor_activity_by_day = pd.concat(all_locomotor_activity_by_day, ignore_index=True)
            combined_df_by_LD_DD = pd.concat(all_df_by_LD_DD, ignore_index=True)
            combined_sleep_analysis_df = pd.concat(all_sleep_analysis_df, ignore_index=True)
            st.session_state.sleep_analysis_df = combined_sleep_analysis_df

            ####################################################################################
            # Create summary figure for daily locomotor activity
            fig_summary = px.bar(
                combined_daily_locomotor_activity,
                x='Condition',
                y='Mean',
                color='Condition',
                error_y='SEM',
                labels={'Condition': 'Condition', 'Mean': 'Mean Activity'},
                title='Mean Activity per Day'
            )
            
            fig_summary.update_layout(
                bargap=0.5
            )

            
            # Create scatter plot for locomotor activity by day
            fig_by_day = px.scatter(
                combined_locomotor_activity_by_day,
                x='Date',
                y='mean',
                color='Condition',
                error_y='sem',
                labels={'Date': 'Date', 'mean': 'Locomotor Activity'},
                title='Locomotor Activity by Day' 
            )        

            # Create bar plot for locomotor activity by LD/DD
            color_map = {'LD': 'yellow', 'DD': 'blue'}  # Yellow for LD, Blue for DD

            fig_by_LD_DD = px.bar(
                combined_df_by_LD_DD,
                x='Condition',
                y='mean',
                color='Light_status',
                error_y='sem',
                color_discrete_map=color_map,
                barmode='group',
                labels={'Condition': 'Condition', 'mean': 'Locomotor Activity', 'Light_status': 'Light Cycle'},
                title='Daytime vs Nighttime Activity'
            )

            fig_by_LD_DD.update_layout(
                bargap=0.5,
            )

            #######################################################################################################################
            st.session_state.daily_locomotor_activity = combined_daily_locomotor_activity
            st.session_state.fig_summary = fig_summary
            st.session_state.locomotor_activity_by_day = combined_locomotor_activity_by_day
            st.session_state.fig_by_day = fig_by_day
            st.session_state.df_by_LD_DD = combined_df_by_LD_DD
            st.session_state.fig_by_LD_DD = fig_by_LD_DD

            tab, tab0, tab1, tab2, tab3, tab4 = st.tabs(["Daily Locomotor Activity", "Daily Sleep", "Average Sleep", "Individual Sleep", "Sleep Bout", "Raw Data"])

            # Prepare sleep analysis data
            sleep_analysis_df = combined_sleep_analysis_df  # This should have all conditions
            all_sleep_calc_df = []

            for condition_name in sleep_analysis_df['Condition'].unique():
                # Filter for this condition
                df_condition = sleep_analysis_df[sleep_analysis_df['Condition'] == condition_name].copy()
                # Get the assigned channels for this condition
                idx = [i for i, cond in enumerate(st.session_state.monitor_settings['conditions']) if cond['name'] == condition_name][0]
                assigned_channels = channel_assignments[idx]
                # Add zt_time
                df_condition['zt_time'] = df_condition['Date_Time'].apply(zeitgeber_time)
                # Only keep relevant columns
                df_condition = df_condition.reset_index(drop=True)
                # Rename the Data columns to ch columns, for example make Data_1 = ch1
                df_condition = df_condition.rename(columns={'data_1':'ch1','data_2':'ch2','data_3':'ch3','data_4':'ch4','data_5':'ch5','data_6':'ch6','data_7':'ch7','data_8':'ch8','data_9':'ch9','data_10':'ch10','data_11':'ch11','data_12':'ch12','data_13':'ch13','data_14':'ch14','data_15':'ch15','data_16':'ch16','data_17':'ch17','data_18':'ch18','data_19':'ch19','data_20':'ch20','data_21':'ch21','data_22':'ch22','data_23':'ch23','data_24':'ch24','data_25':'ch25','data_26':'ch26','data_27':'ch27','data_28':'ch28','data_29':'ch29','data_30':'ch30','data_31':'ch31','data_32':'ch32'})

                df_condition = df_condition[['Date_Time', 'zt_time'] + list(assigned_channels)]
                # Remove unavailable channels for this condition
                unavailable_channels = [ch for ch in assigned_channels if ch in st.session_state.unavailable_channels]
                available_channels = [ch for ch in assigned_channels if ch not in st.session_state.unavailable_channels]
                df_sleep_trim_alive = df_condition.drop(unavailable_channels, axis=1)
                df_sleep_trim_alive = df_sleep_trim_alive.set_index('Date_Time')
                numeric_df_sleep_trim_alive = df_sleep_trim_alive.select_dtypes(include=['number'])
                sleep_calc_df = numeric_df_sleep_trim_alive.rolling(5).sum().applymap(lambda x: 1 if x == 0 else 0)
                sleep_calc_df['zt_time'] = df_sleep_trim_alive.index.to_series().apply(zeitgeber_time)
                sleep_calc_df = sleep_calc_df.reset_index()
                sleep_calc_df['mean'] = sleep_calc_df[available_channels].mean(axis=1)
                sleep_calc_df['sem'] = sleep_calc_df[available_channels].sem(axis=1)
                sleep_calc_df['Condition'] = condition_name
                all_sleep_calc_df.append(sleep_calc_df)

            # Combine all conditions
            combined_sleep_calc_df = pd.concat(all_sleep_calc_df, ignore_index=True)

            ##########################################################################################

            st.session_state.sleep_analysis_df = combined_sleep_analysis_df

            with tab:
                st.header('Daily Locomotor Activity')
                col1, col2, col3 = st.columns(3)

                # Show summary plot in col1
                if 'fig_summary' in st.session_state and st.session_state.fig_summary is not None:
                    col1.plotly_chart(st.session_state.fig_summary, use_container_width=True)
                if 'daily_locomotor_activity' in st.session_state and st.session_state.daily_locomotor_activity is not None:
                    st.write("**Daily Locomotor Activity Data**")
                    st.dataframe(st.session_state.daily_locomotor_activity, use_container_width=True)
                    # Add a download button for the daily locomotor activity data
                    csv = st.session_state.daily_locomotor_activity.to_csv(index=False)
                    st.download_button(
                        label="Download daily locomotor activity data as CSV",
                        data=csv,
                        file_name='daily_locomotor_activity.csv',
                        mime='text/csv'
                    )
                # Show by day plot in col2
                if 'fig_by_day' in st.session_state and st.session_state.fig_by_day is not None:
                    col2.plotly_chart(st.session_state.fig_by_day, use_container_width=True)
                if 'locomotor_activity_by_day' in st.session_state and st.session_state.locomotor_activity_by_day is not None:
                    st.write("**Locomotor Activity by Day Data**")
                    st.dataframe(st.session_state.locomotor_activity_by_day, use_container_width=True)
                    # Add a download button for the locomotor activity by day data
                    csv = st.session_state.locomotor_activity_by_day.to_csv(index=False)
                    st.download_button(
                        label="Download locomotor activity by day data as CSV",
                        data=csv,
                        file_name='locomotor_activity_by_day.csv',
                        mime='text/csv'
                    )
                # Show by LD/DD plot in col3
                if 'fig_by_LD_DD' in st.session_state and st.session_state.fig_by_LD_DD is not None:
                    col3.plotly_chart(st.session_state.fig_by_LD_DD, use_container_width=True)
                if 'df_by_LD_DD' in st.session_state and st.session_state.df_by_LD_DD is not None:
                    st.write("**Locomotor Activity by LD/DD Data**")
                    st.dataframe(st.session_state.df_by_LD_DD, use_container_width=True)
                    # Add a download button for the locomotor activity by LD/DD data
                    csv = st.session_state.df_by_LD_DD.to_csv(index=False)
                    st.download_button(
                        label="Download locomotor activity by LD/DD data as CSV",
                        data=csv,
                        file_name='locomotor_activity_by_LD_DD.csv',
                        mime='text/csv'
                    )
            ##########################################################################################
            with tab0:
                st.header('Daily Sleep Profiles')
                daily_sleep_df = combined_sleep_calc_df.copy()
                # Get start and end date from session state
                ld_dd_settings = st.session_state.monitor_settings.get('ld_dd_settings', {})
                start_date_str = ld_dd_settings.get('start_date')
                end_date_str = ld_dd_settings.get('end_date')

                # Convert to datetime
                start_dt = pd.to_datetime(start_date_str, errors='coerce')
                end_dt = pd.to_datetime(end_date_str, errors='coerce')

                n_points = 250  # Number of points to plot per condition

                if plot_conditions == "Overlap":
                    # Prepare data for overlap plot
                    plot_df_list = []
                    for condition in daily_sleep_df['Condition'].unique():
                        cond_df = daily_sleep_df[daily_sleep_df['Condition'] == condition].copy()
                        total_points = len(cond_df)
                        if total_points > n_points:
                            indices = np.linspace(0, total_points - 1, n_points, dtype=int)
                            cond_df = cond_df.iloc[indices]
                        cond_df = cond_df.sort_values('Date_Time').reset_index(drop=True)
                        cond_df['Sequential_Index'] = range(len(cond_df))
                        cond_df['Time'] = cond_df['Date_Time'].dt.time
                        plot_df_list.append(cond_df)
                    plot_df = pd.concat(plot_df_list, ignore_index=True)

                    # Calculate points per day based on sampling interval
                    if len(plot_df) > 1:
                        intervals = plot_df['Date_Time'].diff().dt.total_seconds().dropna() / 60
                        interval_minutes = intervals.mode()[0] if not intervals.mode().empty else intervals.mean()
                        points_per_day = int(24 * 60 / interval_minutes)
                    else:
                        points_per_day = 24  # fallback

                    # Build tickvals and ticktext using start_dt
                    tickvals = []
                    ticktext = []
                    if pd.notnull(start_dt):
                        n_days = int(np.ceil(len(plot_df) / points_per_day))
                        for day in range(n_days):
                            for hour in [0, 6, 12, 18]:
                                idx = int(day * points_per_day + hour * (points_per_day / 24))
                                if idx < len(plot_df):
                                    tickvals.append(idx)
                                    tick_time = start_dt + pd.Timedelta(days=day, hours=hour)
                                    ticktext.append(tick_time.strftime('%b %d\n%H:%M'))
                    else:
                        # fallback to using actual data
                        date_times = plot_df['Date_Time']
                        for idx, dt in enumerate(date_times):
                            if dt.hour in [0, 6, 12, 18] and dt.minute == 0:
                                tickvals.append(idx)
                                ticktext.append(dt.strftime('%b %d\n%H:%M'))

                    fig = px.line(
                        plot_df,
                        x='Sequential_Index',
                        y='mean',
                        color='Condition',
                        labels={'mean': 'Sleep', 'Sequential_Index': 'Time (H)', 'Condition': 'Condition'},
                        title='Daily Sleep Profile'
                    )
                    fig.update_traces(
                        hovertemplate='Time: %{customdata[0]}<br>Mean Sleep: %{y:.2f}',
                        customdata=plot_df[['Time']]
                    )
                    fig.update_xaxes(
                        tickvals=tickvals,
                        ticktext=ticktext,
                        title='Date & Hour'
                    )

                    st.plotly_chart(fig, use_container_width=True)
                    st.session_state.fig_daily_sleep_profile = fig

                else:  # Split mode
                    for condition in daily_sleep_df['Condition'].unique():
                        cond_df = daily_sleep_df[daily_sleep_df['Condition'] == condition].copy()
                        total_points = len(cond_df)
                        if total_points > n_points:
                            indices = np.linspace(0, total_points - 1, n_points, dtype=int)
                            cond_df = cond_df.iloc[indices]
                        cond_df = cond_df.sort_values('Date_Time').reset_index(drop=True)
                        cond_df['Sequential_Index'] = range(len(cond_df))
                        cond_df['Time'] = cond_df['Date_Time'].dt.time

                        # Calculate points per day based on sampling interval
                        if len(cond_df) > 1:
                            intervals = cond_df['Date_Time'].diff().dt.total_seconds().dropna() / 60
                            interval_minutes = intervals.mode()[0] if not intervals.mode().empty else intervals.mean()
                            points_per_day = int(24 * 60 / interval_minutes)
                        else:
                            points_per_day = 24  # fallback

                        # Build tickvals and ticktext using start_dt
                        tickvals = []
                        ticktext = []
                        if pd.notnull(start_dt):
                            n_days = int(np.ceil(len(cond_df) / points_per_day))
                            for day in range(n_days):
                                for hour in [0, 6, 12, 18]:
                                    idx = int(day * points_per_day + hour * (points_per_day / 24))
                                    if idx < len(cond_df):
                                        tickvals.append(idx)
                                        tick_time = start_dt + pd.Timedelta(days=day, hours=hour)
                                        ticktext.append(tick_time.strftime('%b %d\n%H:%M'))
                        else:
                            date_times = cond_df['Date_Time']
                            for idx, dt in enumerate(date_times):
                                if dt.hour in [0, 6, 12, 18] and dt.minute == 0:
                                    tickvals.append(idx)
                                    ticktext.append(dt.strftime('%b %d\n%H:%M'))

                        fig = px.line(
                            cond_df,
                            x='Sequential_Index',
                            y='mean',
                            labels={'mean': 'Sleep', 'Sequential_Index': 'Time (H)'},
                            title=f'Daily Sleep Profile: {condition}'
                        )
                        fig.update_traces(
                            hovertemplate='Time: %{customdata[0]}<br>Mean Sleep: %{y:.2f}',
                            customdata=cond_df[['Time']]
                        )
                        fig.update_xaxes(
                            tickvals=tickvals,
                            ticktext=ticktext,
                            title='Date & Hour'
                        )

                        st.plotly_chart(fig, use_container_width=True)

                st.write("**Sleep Profile Data**")
                st.dataframe(combined_sleep_calc_df, use_container_width=True)
                csv = combined_sleep_calc_df.to_csv(index=False)
                st.download_button(
                    label="Download daily sleep profile data as CSV",
                    data=csv,
                    file_name='daily_sleep_profile.csv',
                    mime='text/csv'
                )
            ##########################################################################################
            with tab1:
                st.header('Average Sleep Analysis')

                all_avg_sleep_list_df = []

                for condition_name in combined_sleep_calc_df['Condition'].unique():
                    avg_sleep_df = combined_sleep_calc_df[combined_sleep_calc_df['Condition'] == condition_name].copy()
                    avg_sleep_df['time'] = avg_sleep_df['Date_Time'].dt.time
                    avg_sleep_df = avg_sleep_df[['time', 'mean']]
                    avg_sleep_df.sort_values('time', inplace=True)
                    avg_sleep_df.reset_index(drop=True, inplace=True)
                    bin = Bin_sleep_profile
                    avg_sleep_list = []
                    for i in range(0, len(avg_sleep_df), bin):
                        start_time = pd.to_datetime(i, unit='m').time()
                        end_time = pd.to_datetime(i+bin-1, unit='m').time()
                        mean_values = avg_sleep_df[(avg_sleep_df['time'] >= start_time) & (avg_sleep_df['time'] <= end_time)]['mean'].tolist()
                        if len(mean_values) == 0:
                            continue
                        bin_mean = sum(mean_values) / len(mean_values)
                        bin_sem = pd.Series(mean_values).sem()
                        avg_sleep_list.append([i, bin_mean, bin_sem])
                    avg_sleep_list_df = pd.DataFrame(avg_sleep_list, columns=['time', 'mean', 'sem'])
                    avg_sleep_list_df['zt_time'] = pd.to_datetime(avg_sleep_list_df['time'], unit='m').dt.time

                    # Only keep the first instances of each zt_time
                    avg_sleep_list_df = avg_sleep_list_df.drop_duplicates(subset='zt_time', keep='first')

                    # Add a Condition column with the condition name
                    avg_sleep_list_df['Condition'] = condition_name

                    # Make the columns go in the order of time, zt_time, condition, mean, sem
                    avg_sleep_list_df = avg_sleep_list_df[['time', 'zt_time', 'Condition', 'mean', 'sem']]
                    avg_sleep_list_df.columns = ['Dec_time', 'Dec_ZT_time', 'Condition', 'mean_binned_sleep','sem_binned_sleep']

                    # Convert zt_time to actual Zeitgeber time
                    avg_sleep_list_df['Dec_ZT_time'] = avg_sleep_list_df['Dec_time'].apply(lambda x: x/60)
                    avg_sleep_list_df['Dec_ZT_time'] = avg_sleep_list_df['Dec_ZT_time'] - 6
                    avg_sleep_list_df['Dec_ZT_time'] = avg_sleep_list_df['Dec_ZT_time'].apply(lambda x: x if x >= 0 else x + 24)
                    avg_sleep_list_df['Dec_ZT_time'] = avg_sleep_list_df['Dec_ZT_time'] * 60

                    # Sort Dec_ZT_time column in chronological order
                    avg_sleep_list_df = avg_sleep_list_df.sort_values(by="Dec_ZT_time")

                    # Convert Dec_ZT_time to hours
                    hours = avg_sleep_list_df['Dec_ZT_time'] / 60
                    avg_sleep_list_df['ZT_time_in_hours'] = hours

                    # Calculate Sleep_30min and SEM_30min
                    avg_sleep_list_df['Sleep_30min'] = avg_sleep_list_df['mean_binned_sleep'] * 30
                    avg_sleep_list_df['SEM_30min'] = avg_sleep_list_df['sem_binned_sleep'] * 30

                    all_avg_sleep_list_df.append(avg_sleep_list_df)

                # Combine all conditions
                combined_avg_sleep_list_df = pd.concat(all_avg_sleep_list_df, ignore_index=True)
                st.session_state.avg_sleep_list_df = combined_avg_sleep_list_df

                if plot_conditions == "Overlap":
                    fig = px.scatter(
                        combined_avg_sleep_list_df,
                        x='ZT_time_in_hours',
                        y='Sleep_30min',
                        color='Condition',
                        error_y='SEM_30min',
                        title='Average Sleep',
                        labels={'ZT_time_in_hours':'ZT time in hours', 'Sleep_30min':'Sleep per 30min'}
                    )
                    st.plotly_chart(fig)
                    st.session_state.fig_avg_sleep = fig
                else:  # Split mode
                    for condition in combined_avg_sleep_list_df['Condition'].unique():
                        cond_df = combined_avg_sleep_list_df[combined_avg_sleep_list_df['Condition'] == condition]
                        fig = px.scatter(
                            cond_df,
                            x='ZT_time_in_hours',
                            y='Sleep_30min',
                            error_y='SEM_30min',
                            title=f'Average Sleep: {condition}',
                            labels={'ZT_time_in_hours':'ZT time in hours', 'Sleep_30min':'Sleep per 30min'}
                        )
                        st.plotly_chart(fig)

                st.write("**Average Sleep Data**")
                st.dataframe(combined_avg_sleep_list_df, use_container_width=True)

                # Add a download button
                csv = combined_avg_sleep_list_df.to_csv(index=False)
                st.download_button(
                    label="Download average sleep list as CSV",
                    data=csv,
                    file_name='avg_sleep_list.csv',
                    mime='text/csv'
                )
            with tab2:
                st.header('Individual Sleep Analysis')
                col1, col2, col3 = st.columns(3)

                all_ind_day_night_mean = []

                for condition_name in combined_sleep_calc_df['Condition'].unique():
                    cond_df = combined_sleep_calc_df[combined_sleep_calc_df['Condition'] == condition_name].copy()
                    idx = [i for i, cond in enumerate(st.session_state.monitor_settings['conditions']) if cond['name'] == condition_name][0]
                    assigned_channels = channel_assignments[idx]
                    available_channels = [ch for ch in assigned_channels if ch not in st.session_state.unavailable_channels]

                    def day_night(dt):
                        if dt.time() >= pd.to_datetime('06:00').time() and dt.time() <= pd.to_datetime('18:00').time():
                            return 'Day'
                        else:
                            return 'Night'

                    ind_day_night = cond_df.copy()
                    ind_day_night['Day_Night'] = ind_day_night['Date_Time'].apply(day_night)
                    ind_day_night = ind_day_night[['Day_Night'] + available_channels]
                    ind_day_night_unpivoted = ind_day_night.melt(id_vars=['Day_Night'], value_vars=available_channels, var_name='Channel', value_name='Counts')
                    ind_day_night_mean = ind_day_night_unpivoted.groupby(['Day_Night', 'Channel'])['Counts'].mean().reset_index()
                    ind_day_night_mean.sort_values(['Channel', 'Day_Night'], inplace=True)
                    ind_day_night_mean.reset_index(drop=True, inplace=True)
                    ind_day_night_mean['Condition'] = condition_name
                    ind_day_night_mean = ind_day_night_mean[['Channel', 'Condition', 'Day_Night', 'Counts']]
                    ind_day_night_mean.columns = ['Channel', 'Condition', 'Light_status', 'mean_sleep_per_ind']
                    all_ind_day_night_mean.append(ind_day_night_mean)

                # Combine all conditions
                combined_ind_day_night_mean = pd.concat(all_ind_day_night_mean, ignore_index=True)
                st.session_state.ind_day_night_mean = combined_ind_day_night_mean

                # Overlap or Split plotting
                if plot_conditions == "Overlap":
                    # Box plot: Total Sleep in LD
                    fig = px.box(
                        combined_ind_day_night_mean,
                        x='Condition',
                        y='mean_sleep_per_ind',
                        color='Condition',
                        points=False,
                        labels={'Condition': 'Condition', "mean_sleep_per_ind": "Mean Sleep per Individual"},
                        title="Total Sleep in LD"
                    )
                    col1.plotly_chart(fig, use_container_width=True)

                    st.session_state.fig_total_sleep_in_LD = fig
                    # Daytime and Nighttime Sleep
                    day_df = combined_ind_day_night_mean[combined_ind_day_night_mean['Light_status'] == 'Day']
                    night_df = combined_ind_day_night_mean[combined_ind_day_night_mean['Light_status'] == 'Night']

                    fig_day = px.box(
                        day_df,
                        x='Condition',
                        y='mean_sleep_per_ind',
                        color='Condition',
                        points=False,
                        labels={"Condition": "Condition", "mean_sleep_per_ind": "Day Mean Sleep per Individual"},
                        title="Daytime Sleep in LD"
                    )
                    col2.plotly_chart(fig_day, use_container_width=True)
                    st.session_state.fig_daytime_sleep_in_LD = fig_day

                    fig_night = px.box(
                        night_df,
                        x='Condition',
                        y='mean_sleep_per_ind',
                        color='Condition',
                        points=False,
                        labels={"Condition": "Condition", "mean_sleep_per_ind": "Night Mean Sleep per Individual"},
                        title="Nighttime Sleep in LD"
                    )
                    col3.plotly_chart(fig_night, use_container_width=True)
                    st.session_state.fig_nighttime_sleep_in_LD = fig_night
                else:  # Split mode
                    for condition in combined_ind_day_night_mean['Condition'].unique():
                        cond_df = combined_ind_day_night_mean[combined_ind_day_night_mean['Condition'] == condition]
                        # Box plot: Total Sleep in LD
                        fig = px.box(
                            cond_df,
                            x='Light_status',
                            y='mean_sleep_per_ind',
                            color='Light_status',
                            points=False,
                            labels={'Light_status': 'Day/Night', "mean_sleep_per_ind": "Mean Sleep per Individual"},
                            title=f"Total Sleep in LD: {condition}"
                        )
                        st.plotly_chart(fig, use_container_width=True)

                st.write("**Individual Day/Night Mean Data**")
                st.dataframe(combined_ind_day_night_mean, use_container_width=True)
                csv = combined_ind_day_night_mean.to_csv(index=False)
                st.download_button(
                    label="Download individual day/night mean data as CSV",
                    data=csv,
                    file_name='individual_day_night_mean.csv',
                    mime='text/csv'
                )
            with tab3:
                st.header("Sleep Bout Analysis")

                all_bout_data = []
                all_grouped = []
                all_grouped2 = []

                # Calculate sleep bouts and grouped data for each condition
                for condition_name in combined_sleep_calc_df['Condition'].unique():
                    cond_df = combined_sleep_calc_df[combined_sleep_calc_df['Condition'] == condition_name].copy()
                    idx = [i for i, cond in enumerate(st.session_state.monitor_settings['conditions']) if cond['name'] == condition_name][0]
                    assigned_channels = channel_assignments[idx]
                    available_channels = [ch for ch in assigned_channels if ch not in st.session_state.unavailable_channels]

                    # --- Sleep Bout Calculation ---
                    bout_data = []
                    for col in available_channels:
                        changes = cond_df[col].diff().fillna(0).apply(lambda x: 1 if x != 0 else 0)
                        change_indices = changes[changes == 1].index
                        prev_value = cond_df.at[change_indices[0], col] if change_indices.size > 0 else None
                        prev_time = cond_df.at[change_indices[0], 'Date_Time'] if change_indices.size > 0 else None
                        for idx2 in change_indices:
                            current_value = cond_df.at[idx2, col]
                            current_time = cond_df.at[idx2, 'Date_Time']
                            zt_time = zeitgeber_time(prev_time)
                            if prev_value is not None and prev_value != current_value:
                                bout_length = (current_time - prev_time).total_seconds() / 60
                                bout_data.append({
                                    'Channel': col,
                                    'Condition': condition_name,
                                    'Date': prev_time.date() if prev_time is not None else None,
                                    'Time': prev_time,
                                    'ZT_Time': zt_time,
                                    'Dec_ZT_Time': convert_zt_to_dec(zt_time),
                                    'Value': prev_value,
                                    'Sleep_Count': fill_sleep_counts(prev_value),
                                    'Bout': fill_bouts(bout_length),
                                    'Bout_Length': bout_length
                                })
                            prev_value = current_value
                            prev_time = current_time

                    ind_sleep_bout_df = pd.DataFrame(bout_data)
                    if ind_sleep_bout_df.empty:
                        continue

                    # --- Filtering and feature engineering ---
                    ind_sleep_bout_df['Time'] = pd.to_datetime(ind_sleep_bout_df['Time'])
                    ind_sleep_bout_df['Date'] = ind_sleep_bout_df['Time'].dt.date
                    ind_sleep_bout_df['Time'] = ind_sleep_bout_df['Time'].dt.time
                    ind_sleep_bout_df['ZT_Time'] = ind_sleep_bout_df['ZT_Time'].dt.time
                    ind_sleep_bout_df['day_or_night'] = ind_sleep_bout_df['Dec_ZT_Time'].apply(lambda x: 'day' if x < 720 else 'night')
                    ind_sleep_bout_df['bout_length_per_sleep_counts'] = ind_sleep_bout_df['Bout_Length'] / ind_sleep_bout_df['Sleep_Count']
                    ind_sleep_bout_df['channel_num'] = ind_sleep_bout_df['Channel'].apply(lambda x: int(x.split('ch')[-1]))

                    # --- Grouped by day ---
                    grouped = ind_sleep_bout_df.groupby(
                        ['day_or_night', 'Channel', 'channel_num', 'Condition', 'Date']
                    ).agg({'Bout': ['sum'], 'Bout_Length': ['sum', 'mean']}).reset_index()
                    grouped = grouped.sort_values(['day_or_night', 'channel_num', 'Date'])
                    grouped.columns = ['_'.join(col).strip() for col in grouped.columns.values]
                    grouped.columns = grouped.columns.str.replace('_$', '', regex=True)
                    grouped['Bout_Length_mean'] = grouped['Bout_Length_mean'].apply(lambda x: round(x, 2))

                    # --- Grouped by channel ---
                    grouped2 = grouped.groupby(
                        ['day_or_night', 'Channel', 'channel_num', 'Condition']
                    ).agg({'Bout_sum': ['mean'], 'Bout_Length_mean': ['mean']}).reset_index()
                    grouped2 = grouped2.sort_values(['day_or_night', 'channel_num'])
                    grouped2.columns = ['_'.join(col).strip() for col in grouped2.columns.values]
                    grouped2.columns = grouped2.columns.str.replace('_$', '', regex=True)
                    grouped2['Bout_sum_mean'] = grouped2['Bout_sum_mean'].apply(lambda x: round(x, 2))
                    grouped2['Bout_Length_mean_mean'] = grouped2['Bout_Length_mean_mean'].apply(lambda x: round(x, 2))

                    # Store for later combination
                    all_bout_data.append(ind_sleep_bout_df)
                    all_grouped.append(grouped)
                    all_grouped2.append(grouped2)

                # --- Combine all conditions ---
                combined_bout_df = pd.concat(all_bout_data, ignore_index=True) if all_bout_data else pd.DataFrame()
                combined_grouped = pd.concat(all_grouped, ignore_index=True) if all_grouped else pd.DataFrame()
                combined_grouped2 = pd.concat(all_grouped2, ignore_index=True) if all_grouped2 else pd.DataFrame()

                st.session_state.ind_sleep_bout_df = combined_bout_df
                st.session_state.grouped = combined_grouped
                st.session_state.grouped2 = combined_grouped2

                combined_grouped = combined_grouped.sort_values(by='Condition')
                combined_grouped2 = combined_grouped2.sort_values(by='Condition')

                col1, col2 = st.columns(2)

                # Display the grouped dataframe
                col1.subheader(f'Grouped By Day')

                # create plotly express density plot
                fig = px.density_contour(combined_grouped, x='Bout_Length_mean', y='Bout_sum', marginal_x='histogram', marginal_y='histogram',
                                    title=f'Sleep Bout Analysis by Day')
                st.session_state.fig_sleep_bout_by_day = fig
                col1.plotly_chart(fig) 

                # Display the grouped2 dataframe
                col2.subheader(f'Grouped By Channel')
                        
                # create plotly express density plot
                fig = px.density_contour(combined_grouped2, x='Bout_sum_mean', y='Bout_Length_mean_mean', marginal_x='histogram', marginal_y='histogram',
                                    title=f'Sleep Bout Analysis by Channel')
                st.session_state.fig_sleep_bout_by_channel = fig
                col2.plotly_chart(fig)


                # --- BOUT LENGTH ANALYSIS ---
                col1.subheader(f"Sleep/Activity Bout Length Analysis")
                col2.subheader("")
                # Use the filtered data instead of the original data
                # Filter for Sleep_Count == 1 (sleep bouts)
                bout_df_1 = combined_bout_df[combined_bout_df['Sleep_Count'] == 1]
                print(f"bout_df_1: {bout_df_1}")
                if not bout_df_1.empty:
                    bout_stats_1 = bout_df_1.groupby('Condition').agg(
                        Avg_Bout_Length=('Bout_Length', 'mean'),
                        SEM_Bout_Length=('Bout_Length', lambda x: x.std(ddof=1) / np.sqrt(len(x)))

                    ).reset_index()
                    fig_avg_length_1 = px.bar(
                        bout_stats_1,
                        x='Condition',
                        y='Avg_Bout_Length',
                        color='Condition',
                        error_y='SEM_Bout_Length',
                        labels={"Condition": "Condition", "Avg_Bout_Length": "Average Bout Length [min]"},
                        title="Sleep Bout Length in LD"
                    )
                    fig_avg_length_1.update_layout(bargap=0.75)
                    col1.plotly_chart(fig_avg_length_1, use_container_width=True)
                    st.session_state.fig_avg_bout_length_1 = fig_avg_length_1
                else:
                    col1.info(f"No sleep bouts found.")
                
                # Filter for Sleep_Count == 0 (activity bouts)
                bout_df_0 = combined_bout_df[combined_bout_df['Sleep_Count'] == 0]
                print(f"bout_df_0: {bout_df_0}")
                if not bout_df_0.empty:
                    bout_stats_0 = bout_df_0.groupby('Condition').agg(
                        Avg_Bout_Length=('Bout_Length', 'mean'),
                        SEM_Bout_Length=('Bout_Length', lambda x: x.std(ddof=1) / np.sqrt(len(x))) 
                    ).reset_index()
                    fig_avg_length_0 = px.bar(
                        bout_stats_0,
                        x='Condition',
                        y='Avg_Bout_Length',
                        color='Condition',
                        error_y='SEM_Bout_Length',
                        labels={"Condition": "Condition", "Avg_Bout_Length": "Average Bout Length [min]"},
                        title="Activity Bout Length in LD"
                    )
                    fig_avg_length_0.update_layout(bargap=0.75)
                    col2.plotly_chart(fig_avg_length_0, use_container_width=True)
                    st.session_state.fig_avg_bout_length_0 = fig_avg_length_0
                else:
                    col2.info("No activity bouts found.")

                # --- Grouped by Day Bar Chart ---
                if not combined_grouped.empty:
                    agg_day = combined_grouped.groupby(['Condition', 'Date']).agg({'Bout_Length_mean': 'mean'}).reset_index()
                    fig_sleep_bout_by_day = px.bar(
                        agg_day,
                        x='Date',
                        y='Bout_Length_mean',
                        color='Condition',
                        barmode='group',
                        title="Mean Bout Length by Day"
                    )
                    col1.plotly_chart(fig_sleep_bout_by_day, use_container_width=True)
                    st.session_state.fig_sleep_bout_by_day = fig_sleep_bout_by_day

                # --- Grouped by Channel Bar Chart ---
                if not combined_grouped2.empty:
                     # Ensure Channel is ordered ch1, ch2, ..., ch32
                    channel_order = [f'ch{i}' for i in range(1, 33)]
                    combined_grouped2['Channel'] = pd.Categorical(combined_grouped2['Channel'], categories=channel_order, ordered=True)
                    agg_channel = combined_grouped2.groupby(['Condition', 'Channel']).agg({'Bout_Length_mean_mean': 'mean'}).reset_index()
                    agg_channel = agg_channel.sort_values(by=['Channel', 'Condition'])  # Sort by channel order

                    agg_channel = combined_grouped2.groupby(['Condition', 'Channel']).agg({'Bout_Length_mean_mean': 'mean'}).reset_index()
                    fig_sleep_bout_by_channel = px.bar(
                        agg_channel,
                        x='Channel',
                        y='Bout_Length_mean_mean',
                        color='Condition',
                        barmode='group',
                        title="Mean Bout Length by Available Channel"
                    )
                    col2.plotly_chart(fig_sleep_bout_by_channel, use_container_width=True)
                    st.session_state.fig_sleep_bout_by_channel = fig_sleep_bout_by_channel

                if not combined_bout_df.empty:
                    st.dataframe(combined_bout_df, use_container_width=True)
                    st.download_button('Download Sleep Bout Data as CSV', combined_bout_df.to_csv(index=False), 'sleep_bout_data.csv', 'text/csv')

                # --- Grouped by Day ---
                if not combined_grouped.empty:
                    st.subheader("Grouped By Day")
                    st.dataframe(combined_grouped, use_container_width=True)
                    st.download_button('Download Grouped by Day Data as CSV', combined_grouped.to_csv(index=False), 'grouped.csv', 'text/csv')

                # --- Grouped by Channel ---
                if not combined_grouped2.empty:
                    st.subheader("Grouped By Channel")
                    st.dataframe(combined_grouped2, use_container_width=True)
                    st.download_button('Download Grouped by Channel Data as CSV', combined_grouped2.to_csv(index=False), 'grouped2.csv', 'text/csv')
            save_analysis()
    ##########################################################################################
    st.markdown("### Download All Results")
    # Collect all CSV tables you want to include
    csv_tables = {
        "daily_locomotor_activity.csv": st.session_state.get("daily_locomotor_activity", pd.DataFrame()),
        "locomotor_activity_by_day.csv": st.session_state.get("locomotor_activity_by_day", pd.DataFrame()),
        "df_by_LD_DD.csv": st.session_state.get("df_by_LD_DD", pd.DataFrame()),
        'sleep_analysis_df': st.session_state.get('sleep_analysis_df', pd.DataFrame()),
        "avg_sleep_list.csv": st.session_state.get("avg_sleep_list_df", pd.DataFrame()),
        "ind_day_night_mean.csv": st.session_state.get("ind_day_night_mean", pd.DataFrame()),
        "sleep_grouped.csv": st.session_state.get("grouped1", pd.DataFrame()),
        "sleep_grouped2.csv": st.session_state.get("grouped2_1", pd.DataFrame()),
    }

    # Create a zip in memory
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as zip_file:
        for fname, df in csv_tables.items():
            if isinstance(df, pd.DataFrame) and not df.empty:
                zip_file.writestr(fname, df.to_csv(index=False))
    zip_buffer.seek(0)

    st.download_button(
        label="Download All CSV Tables (ZIP)",
        data=zip_buffer,
        file_name="all_experiment_tables.zip",
        mime="application/zip"
    )


    if 'analysis_ran' not in st.session_state:
        st.session_state.analysis_ran = False

    if st.session_state.get("analysis_ran"):
        Daily_locomotor_activity = st.session_state.daily_locomotor_activity

with tabB:
    import os
    import pickle

    with st.expander("Saved Analyses", expanded=True):
        st.subheader("List of Saved Analyses")
        analyses_dir = "saved_analysis"
        if os.path.exists(analyses_dir):
            files = [f for f in os.listdir(analyses_dir) if f.endswith(".pkl")]
            if files:
                selected_file = st.selectbox("Select an analysis to view:", files)
                if selected_file:
                    file_path = os.path.join(analyses_dir, selected_file)
                    try:
                        with open(file_path, "rb") as f:
                            analysis_obj = pickle.load(f)
                        st.write(f"**Contents of {selected_file}:**")
                        st.header("📋 Metadata")
                        metadata = analysis_obj.get('metadata', {})
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

                        # --- Show tables and graphs under 5 tabs ---
                        tab, tab0, tab1, tab2, tab3, tab4 = st.tabs(
                            ["Daily Locomotor Activity", "Daily Sleep", "Average Sleep", "Individual Sleep", "Sleep Bout", "Raw Data"]
                        )
                        # --- Tab: Daily Locomotor Activity ---
                        with tab:
                            st.subheader("Daily Locomotor Activity")
                            col1, col2, col3 = st.columns(3)
                            if 'fig_summary_locomotor' in analysis_obj:
                                col1.plotly_chart(analysis_obj['fig_summary_locomotor'], use_container_width=True)
                            if "daily_locomotor_activity" in analysis_obj:
                                st.write("Daily Locomotor Activity DataFrame")
                                st.dataframe(analysis_obj["daily_locomotor_activity"])
                            if 'fig_by_day_activity' in analysis_obj:
                                col2.plotly_chart(analysis_obj['fig_by_day_activity'], use_container_width=True)
                            if "locomotor_activity_by_day" in analysis_obj:
                                st.write("Locomotor Activity by Day DataFrame")
                                st.dataframe(analysis_obj["locomotor_activity_by_day"])
                            if 'fig_by_LD_DD_activity' in analysis_obj:
                                col3.plotly_chart(analysis_obj['fig_by_LD_DD_activity'], use_container_width=True)
                            if "df_by_LD_DD" in analysis_obj:
                                st.write("DF by LD/DD DataFrame")
                                st.dataframe(analysis_obj["df_by_LD_DD"])
                        # --- Tab 0: Daily Sleep ---
                        with tab0:
                            st.subheader("Daily Sleep")                         
                            if "daily_sleep_profile" in analysis_obj:
                                st.write("Daily Sleep Profile")
                                st.plotly_chart(analysis_obj["daily_sleep_profile"], use_container_width=True)
                            if "sleep_analysis_df" in analysis_obj:
                                st.write("Sleep Analysis DataFrame")
                                st.dataframe(analysis_obj["sleep_analysis_df"])
                        # --- Tab 1: Average Sleep ---
                        with tab1:
                            st.subheader("Average Sleep")
                            if "average_sleep_profile" in analysis_obj:
                                st.write("Average Sleep Profile")
                                st.plotly_chart(analysis_obj["average_sleep_profile"], use_container_width=True)
                            if "avg_sleep_list_df" in analysis_obj:
                                st.write("Average Sleep List DataFrame")
                                st.dataframe(analysis_obj["avg_sleep_list_df"])
                        # --- Tab 2: Individual Sleep ---
                        with tab2:
                            st.subheader("Individual Sleep")
                            col1, col2, col3 = st.columns(3)
                            if "total_sleep_in_LD" in analysis_obj:
                                col1.plotly_chart(analysis_obj["total_sleep_in_LD"], use_container_width=True)
                            if "daytime_sleep_in_LD" in analysis_obj:
                                col2.plotly_chart(analysis_obj["daytime_sleep_in_LD"], use_container_width=True)
                            if "nighttime_sleep_in_LD" in analysis_obj:
                                col3.plotly_chart(analysis_obj["nighttime_sleep_in_LD"], use_container_width=True)
                            if "ind_day_night_mean" in analysis_obj:
                                st.write("Individual Day/Night Mean DataFrame")
                                st.dataframe(analysis_obj["ind_day_night_mean"])
                        # --- Tab 3: Sleep Bout ---
                        with tab3:
                            st.subheader("Sleep Bout")
                            col1, col2 = st.columns(2)
                            if "fig_sleep_bout_by_day" in analysis_obj:
                                col1.plotly_chart(analysis_obj["fig_sleep_bout_by_day"], use_container_width=True)
                            if "fig_sleep_bout_by_channel" in analysis_obj:
                                col2.plotly_chart(analysis_obj["fig_sleep_bout_by_channel"], use_container_width=True)
                            if "fig_avg_bout_length_1" in analysis_obj:
                                col1.plotly_chart(analysis_obj["fig_avg_bout_length_1"], use_container_width=True)
                            if "fig_avg_bout_length_0" in analysis_obj:
                                col2.plotly_chart(analysis_obj["fig_avg_bout_length_0"], use_container_width=True)
                            if "ind_sleep_bout_df" in analysis_obj:
                                st.write("Sleep Bout DataFrame")
                                st.dataframe(analysis_obj["ind_sleep_bout_df"])
                        # --- Tab 4: Raw Data ---
                        with tab4:
                            st.subheader("Raw Data")
                            if "daily_locomotor_activity" in analysis_obj:
                                st.write("Daily Locomotor Activity")
                                st.dataframe(analysis_obj["daily_locomotor_activity"])
                            if "locomotor_activity_by_day" in analysis_obj:
                                st.write("Locomotor Activity by Day")
                                st.dataframe(analysis_obj["locomotor_activity_by_day"])
                            if "df_by_LD_DD" in analysis_obj:
                                st.write("DF by LD/DD")
                                st.dataframe(analysis_obj["df_by_LD_DD"])
                            if "sleep_grouped" in analysis_obj:
                                st.write("Sleep Grouped")
                                st.dataframe(analysis_obj["sleep_grouped"])
                            if "sleep_grouped2" in analysis_obj:
                                st.write("Sleep Grouped2")
                                st.dataframe(analysis_obj["sleep_grouped2"])

                    except Exception as e:
                        st.error(f"Could not load {selected_file}: {e}")
            else:
                st.info("No analyses found in the directory.")
        else:
            st.info("No analyses have been saved yet.")

with tabC:
    import os
    import pickle
    import pandas as pd
    import numpy as np
    import plotly.express as px

    SAVE_ANALYSIS_PATH = "saved_analysis"

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

    st.title("Monitor Analysis Comparison")

    all_experiments = list_saved_analyses()
    selected_experiments = st.multiselect("Select two or more monitor analyses to compare", all_experiments)

    if len(selected_experiments) >= 1:
        # Load all analyses
        loaded_analyses = [load_analysis(exp) for exp in selected_experiments if load_analysis(exp) is not None]

        tab, tab0, tab1, tab2, tab3, tab4 = st.tabs(
            ["Daily Locomotor Activity", "Daily Sleep", "Average Sleep", "Individual Sleep", "Sleep Bout", "Raw Data"]
        )
    
        # --- Tab: Daily Locomotor Activity ---
        with tab:
            st.subheader("Daily Locomotor Activity")
            col1, col2, col3 = st.columns(3)

            # --- Combine Summary Bar Plots ---
            figs_summary = []
            combined_summary_df = pd.DataFrame()
            for analysis in loaded_analyses:
                fig = analysis.get("fig_summary_locomotor")
                label = analysis.get("Condition", analysis.get("Experiment", ""))
                df = analysis.get("daily_locomotor_activity")
                if fig is not None and hasattr(fig, "data"):
                    figs_summary.append((fig, label))
                if df is not None:
                    df = df.copy()
                    combined_summary_df = pd.concat([combined_summary_df, df], ignore_index=True)
            if figs_summary:
                import plotly.graph_objs as go
                
                combined_fig = go.Figure()
                for idx, (fig, label) in enumerate(figs_summary):
                    color = px.colors.qualitative.Plotly[idx % len(px.colors.qualitative.Plotly)]
                    for trace in fig.data:
                        if hasattr(trace, "marker"):
                            trace.marker.color = color
                        if hasattr(trace, "line"):
                            trace.line.color = color
                        combined_fig.add_trace(trace)
                combined_fig.update_layout(
                    title="Combined Mean Activity per Day",
                    xaxis_title="Condition",
                )
                col1.plotly_chart(combined_fig, use_container_width=True)

                # --- Combine By Day Plots ---
            figs_by_day = []
            combined_by_day_df = pd.DataFrame()
            for analysis in loaded_analyses:
                fig = analysis.get("fig_by_day_activity")
                label = analysis.get("Condition", analysis.get("Experiment", ""))
                df = analysis.get("locomotor_activity_by_day")
                if fig is not None and hasattr(fig, "data"):
                    figs_by_day.append((fig, label))
                if df is not None:
                    df = df.copy()
                    combined_by_day_df = pd.concat([combined_by_day_df, df], ignore_index=True)
            if figs_by_day:
                import plotly.graph_objs as go
                combined_fig = go.Figure()
                for idx, (fig, label) in enumerate(figs_by_day):
                    color = px.colors.qualitative.Plotly[idx % len(px.colors.qualitative.Plotly)]
                    for trace in fig.data:
                        if hasattr(trace, "marker"):
                            trace.marker.color = color
                        if hasattr(trace, "line"):
                            trace.line.color = color
                        combined_fig.add_trace(trace)
                combined_fig.update_layout(
                    title="Combined Locomotor Activity by Day",
                    xaxis_title="Date",
                    yaxis_title="Locomotor Activity"
                )
                col2.plotly_chart(combined_fig, use_container_width=True)

            # --- Combine By LD/DD Plots ---
            combined_ld_dd = pd.DataFrame()
            for analysis in loaded_analyses:
                df = analysis.get("df_by_LD_DD")
                if df is not None:
                    df = df.copy()
                    combined_ld_dd = pd.concat([combined_ld_dd, df], ignore_index=True)

            if not combined_ld_dd.empty:
                # Ensure correct color mapping and grouping
                color_map = {'LD': 'yellow', 'DD': 'blue'}
                fig = px.bar(
                    combined_ld_dd,
                    x='Condition',
                    y='mean',
                    color='Light_status',
                    error_y='sem',
                    color_discrete_map=color_map,
                    barmode='group',
                    labels={'Condition': 'Condition', 'mean': 'Locomotor Activity', 'Light_status': 'Light Cycle'},
                    title='Combined Daytime vs Nighttime Activity'
                )
                col3.plotly_chart(fig, use_container_width=True)

             # --- Show all three dataframes in a line under the charts ---
            st.write("**Combined Daily Locomotor Activity Data**")
            st.dataframe(combined_summary_df, use_container_width=True)
            st.write("**Combined Locomotor Activity by Day Data**")
            st.dataframe(combined_by_day_df, use_container_width=True)
            st.write("**Combined Locomotor Activity by LD/DD Data**")
            st.dataframe(combined_ld_dd, use_container_width=True)
        # --- Tab 0: Daily Sleep ---
        with tab0:
            st.subheader("Daily Sleep")
            combined_sleep_analysis = pd.DataFrame()
    
            figs = []
            start_dates = []
            for analysis in loaded_analyses:
                df = analysis.get("sleep_analysis_df")
                if df is not None:
                    df = df.copy()
                    combined_sleep_analysis = pd.concat([combined_sleep_analysis, df], ignore_index=True)
                fig = analysis.get("daily_sleep_profile")
                if fig is not None and hasattr(fig, "data"):
                    figs.append((fig, analysis['Condition']))
                    # Try to get the start date from metadata for tick labels
                    meta = analysis.get("metadata", {})
                    start_date_str = meta.get("start_date")
                    try:
                        start_dates.append(pd.to_datetime(start_date_str, errors='coerce'))
                    except Exception:
                        start_dates.append(None)

            if figs:
                import plotly.graph_objs as go
                combined_fig = go.Figure()
                legend_items = []

                # Use the Date_Time column from the first available sleep_analysis_df
                date_times = None
                for analysis in loaded_analyses:
                    if "sleep_analysis_df" in analysis:
                        df = analysis["sleep_analysis_df"]
                        if "Date_Time" in df:
                            date_times = pd.to_datetime(df["Date_Time"])
                            break

                # Build tickvals and ticktext just like in tabA
                tickvals = []
                ticktext = []
                if date_times is not None:
                    for idx, dt in enumerate(date_times):
                        if dt.hour in [0, 6, 12, 18] and dt.minute == 0:
                            tickvals.append(idx)
                            ticktext.append(dt.strftime('%b %d\n%H:%M'))
                else:
                    # Fallback: just show 0, 6, 12, 18 for the first day
                    n_points = len(figs[0][0].data[0].x)
                    for hour in [0, 6, 12, 18]:
                        idx = int(hour * (n_points / 24))
                        if idx < n_points:
                            tickvals.append(idx)
                            ticktext.append(f"{hour}:00")

                for idx, (fig, label) in enumerate(figs):
                    color = px.colors.qualitative.Plotly[idx % len(px.colors.qualitative.Plotly)]
                    for trace in fig.data:
                        if hasattr(trace, "marker"):
                            trace.marker.color = color
                        if hasattr(trace, "line"):
                            trace.line.color = color
                        combined_fig.add_trace(trace)
                    legend_items.append((label, color))
                combined_fig.update_layout(
                    title="Combined Daily Sleep Profile",
                    xaxis_title="Date & Hour",
                    yaxis_title="Sleep"
                )
                combined_fig.update_xaxes(
                    tickvals=tickvals,
                    ticktext=ticktext,
                    title='Date & Hour'
                )
                st.plotly_chart(combined_fig, use_container_width=True)

                if not combined_sleep_analysis.empty:
                    st.write("**Combined Daily Sleep Analysis Data**")
                    st.dataframe(combined_sleep_analysis)
        # --- Tab 1: Average Sleep ---
        with tab1:
            st.subheader("Average Sleep")
            combined_avg_sleep = pd.DataFrame()
            for analysis in loaded_analyses:
                df = analysis.get("avg_sleep_list_df")
                if df is not None:
                    df = df.copy()
                    combined_avg_sleep = pd.concat([combined_avg_sleep, df], ignore_index=True)
            
            figs = []
            for analysis in loaded_analyses:
                fig = analysis.get("average_sleep_profile")
                if fig is not None and hasattr(fig, "data"):
                    figs.append((fig, analysis['Condition']))
            if figs:
                import plotly.graph_objs as go
                color_map = px.colors.qualitative.Plotly
                combined_fig = go.Figure()
                legend_items = []
                for idx, (fig, label) in enumerate(figs):
                    color = px.colors.qualitative.Plotly[idx % len(px.colors.qualitative.Plotly)]
                    for trace in fig.data:
                        if hasattr(trace, "marker"):
                            trace.marker.color = color
                        if hasattr(trace, "line"):
                            trace.line.color = color
                        combined_fig.add_trace(trace)
                    legend_items.append((label, color))
                combined_fig.update_layout(
                    title="Combined Average Sleep Profile",
                    xaxis_title="ZT Time (hours)",
                    yaxis_title="Sleep per 30min"
                )
                st.plotly_chart(combined_fig, use_container_width=True)

            if not combined_avg_sleep.empty:
                st.write("**Combined Average Sleep Data**")
                st.dataframe(combined_avg_sleep)
        # --- Tab 2: Individual Sleep ---
        with tab2:
            st.subheader("Individual Sleep")
            col1, col2, col3 = st.columns(3)
            combined_ind = pd.DataFrame()
            for analysis in loaded_analyses:
                df = analysis.get("ind_day_night_mean")
                if df is not None:
                    df = df.copy()
                    combined_ind = pd.concat([combined_ind, df], ignore_index=True)
            
            # Box plot: Total Sleep in LD
            if "mean_sleep_per_ind" in combined_ind.columns:
                fig = px.box(
                    combined_ind,
                    x='Condition',
                    y='mean_sleep_per_ind',
                    color='Condition',  # Color by condition, not Light_status
                    points=False,
                    labels={'Condition': 'Condition', "mean_sleep_per_ind": "Mean Sleep per Individual"},
                    title="Total Sleep in LD"
                )
                col1.plotly_chart(fig, use_container_width=True)

            # --- Daytime and Nighttime Sleep: x=Condition, color=Condition ---
            # Prepare day and night dataframes
            day_df = combined_ind[combined_ind['Light_status'] == 'Day']
            night_df = combined_ind[combined_ind['Light_status'] == 'Night']

            if not day_df.empty:
                fig_day = px.box(
                    day_df,
                    x='Condition',
                    y='mean_sleep_per_ind',
                    color='Condition',  # Color by condition
                    points=False,
                    labels={"Condition": "Condition", "mean_sleep_per_ind": "Day Mean Sleep per Individual"},
                    title="Daytime Sleep in LD"
                )
                col2.plotly_chart(fig_day, use_container_width=True)

            if not night_df.empty:
                fig_night = px.box(
                    night_df,
                    x='Condition',
                    y='mean_sleep_per_ind',
                    color='Condition',  # Color by condition
                    points=False,
                    labels={"Condition": "Condition", "mean_sleep_per_ind": "Night Mean Sleep per Individual"},
                    title="Nighttime Sleep in LD"
                )
                col3.plotly_chart(fig_night, use_container_width=True)

            if not combined_ind.empty:
                st.write("**Combined Individual Sleep Data**")
                st.dataframe(combined_ind)
        # --- Tab 3: Sleep Bout ---
        with tab3:
            st.subheader("Sleep Bout")
            combined_bout = pd.DataFrame()
            for analysis in loaded_analyses:
                df = analysis.get("ind_sleep_bout_df")
                if df is not None:
                    df = df.copy()
                    combined_bout = pd.concat([combined_bout, df], ignore_index=True)
            
            col1, col2 = st.columns(2)
            # Sleep Bout Length (Sleep_Count == 1)
            bout_df_1 = combined_bout[combined_bout['Sleep_Count'] == 1]
            if not bout_df_1.empty:
                bout_stats_1 = bout_df_1.groupby('Condition').agg(
                    Avg_Bout_Length=('Bout_Length', 'mean'),
                    SEM_Bout_Length=('Bout_Length', lambda x: x.std(ddof=1) / np.sqrt(len(x)))
                ).reset_index()
                fig_avg_length_1 = px.bar(
                    bout_stats_1,
                    x='Condition',
                    y='Avg_Bout_Length',
                    color='Condition',
                    error_y='SEM_Bout_Length',
                    labels={"Condition": "Condition", "Avg_Bout_Length": "Average Bout Length [min]"},
                    title="Sleep Bout Length in LD"
                )
                fig_avg_length_1.update_layout(bargap=0.75)
                col1.plotly_chart(fig_avg_length_1, use_container_width=True)
                st.session_state.fig_avg_bout_length_1 = fig_avg_length_1
            else:
                col1.info(f"No sleep bouts found.")

            # Filter for Sleep_Count == 0 (activity bouts)
            bout_df_0 = combined_bout[combined_bout['Sleep_Count'] == 0]
            if not bout_df_0.empty:
                bout_stats_0 = bout_df_0.groupby('Condition').agg(
                    Avg_Bout_Length=('Bout_Length', 'mean'),
                    SEM_Bout_Length=('Bout_Length', lambda x: x.std(ddof=1) / np.sqrt(len(x))) 
                ).reset_index()
                fig_avg_length_0 = px.bar(
                    bout_stats_0,
                    x='Condition',
                    y='Avg_Bout_Length',
                    color='Condition',
                    error_y='SEM_Bout_Length',
                    labels={"Condition": "Condition", "Avg_Bout_Length": "Average Bout Length [min]"},
                    title="Activity Bout Length in LD"
                )
                fig_avg_length_0.update_layout(bargap=0.75)
                col2.plotly_chart(fig_avg_length_0, use_container_width=True)
                st.session_state.fig_avg_bout_length_0 = fig_avg_length_0
            else:
                col2.info("No activity bouts found for the selected time period(s).")
            
            col3, col4 = st.columns(2)
            # --- Combined Grouped by Day ---
            grouped_day_combined = pd.DataFrame()
            for analysis in loaded_analyses:
                df = analysis.get('sleep_grouped')
                if df is not None:
                    df = df.copy()
                    grouped_day_combined = pd.concat([grouped_day_combined, df], ignore_index=True)

            
            if not grouped_day_combined.empty:
                agg_day = grouped_day_combined.groupby(['Condition', 'Date']).agg({'Bout_Length_mean': 'mean'}).reset_index()
                fig3 = px.bar(
                    agg_day,
                    x='Date',
                    y='Bout_Length_mean',
                    color='Condition',
                    barmode='group',
                    title="Mean Bout Length by Day"
                )
                col3.plotly_chart(fig3, use_container_width=True)

             # --- Combined Grouped by Channel ---
            grouped_channel_combined = pd.DataFrame()
            for analysis in loaded_analyses:
                df = analysis.get('sleep_grouped2')
                if df is not None:
                    df = df.copy()
                    grouped_channel_combined = pd.concat([grouped_channel_combined, df], ignore_index=True)

            if not grouped_channel_combined.empty:
                # Ensure Channel is ordered ch1, ch2, ..., ch32
                channel_order = [f'ch{i}' for i in range(1, 33)]
                grouped_channel_combined['Channel'] = pd.Categorical(grouped_channel_combined['Channel'], categories=channel_order, ordered=True)
                agg_channel = grouped_channel_combined.groupby(['Condition', 'Channel']).agg({'Bout_Length_mean_mean': 'mean'}).reset_index()
                agg_channel = agg_channel.sort_values(by=['Channel', 'Condition'])  # Sort by channel order

                fig4 = px.bar(
                    agg_channel,
                    x='Channel',
                    y='Bout_Length_mean_mean',
                    color='Condition',
                    barmode='group',
                    title="Mean Bout Length by Channel"
                )
                col4.plotly_chart(fig4, use_container_width=True)

            # --- Tables Below All Graphs ---
            st.markdown("### Combined Sleep Bout Data")
            if not combined_bout.empty:
                st.dataframe(combined_bout)
            if not grouped_day_combined.empty:
                st.markdown("### Sleep Bouts Grouped by Day")
                st.dataframe(grouped_day_combined)
            if not grouped_channel_combined.empty:
                st.markdown("### Sleep Bouts Grouped by Channel")
                st.dataframe(grouped_channel_combined)

        # --- Tab 4: Raw Data ---
        with tab4:
            st.subheader("Raw Data")
            for key in [
                "daily_locomotor_activity",
                "locomotor_activity_by_day",
                "df_by_LD_DD",
                "sleep_grouped",
                "sleep_grouped2"
            ]:
                combined_df = pd.DataFrame()
                for analysis in loaded_analyses:
                    df = analysis.get(key)
                    if df is not None:
                        df = df.copy()
                        df['Condition'] = analysis['Condition']
                        combined_df = pd.concat([combined_df, df], ignore_index=True)
                if not combined_df.empty:
                    st.write(key.replace("_", " ").title())
                    st.dataframe(combined_df)
