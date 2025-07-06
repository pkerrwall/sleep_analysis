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
        'bout_length_mean_by_condition': st.session_state.get('fig_bout_length_mean_by_condition'),
        'bout_sum_mean_by_condition': st.session_state.get('fig_bout_sum_mean_by_condition'),
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

tab0, tab1, tab2 = st.tabs(["Create Experiments", "Experiments List", "Experiment Comparison"])

with tab0:

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
            
            df = df[['Date','Time','Condition','Light_Cycle','ch1','ch2','ch3','ch4','ch5','ch6','ch7','ch8','ch9','ch10','ch11','ch12','ch13','ch14','ch15','ch16','ch17','ch18','ch19','ch20','ch21','ch22','ch23','ch24','ch25','ch26','ch27','ch28','ch29','ch30','ch31','ch32']]

            data_df_total = pd.DataFrame()

            # Get all the days selected in the date range
            days = df['Date'].unique()

            for day in days:
                # Filter the dataframe for the current day
                data_df_day = df[df['Date'] == day]

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
                data_df_day = data_df_day[['Date', 'Condition', 'Light_Cycle', 'ch1', 'ch2', 'ch3', 'ch4', 'ch5', 'ch6', 'ch7', 'ch8', 'ch9', 'ch10', 'ch11', 'ch12', 'ch13', 'ch14', 'ch15', 'ch16', 'ch17', 'ch18', 'ch19', 'ch20', 'ch21', 'ch22', 'ch23', 'ch24', 'ch25', 'ch26', 'ch27', 'ch28', 'ch29', 'ch30', 'ch31', 'ch32']]

                # Add the total row to the data_df_total dataframe
                data_df_total = pd.concat([data_df_total, data_df_day.tail(1)], ignore_index=True)

            # Create a new row that is the mean of all the ch columns
            numeric_cols = data_df_total.columns[3:]  # Exclude 'Condition', 'Light_Cycle', 'Name'
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

            n_of_all_flies = 32
            n_of_alive_flies = 32
            n_of_dead_flies = 0
            # Create a list of available channels
            channel_columns = [f'ch{i}' for i in range(1, 33)]
            available_channels = channel_columns.copy()
            unavailble_channels = []
            available_channels = [ch.strip() for ch in available_channels]

            # Loop through all the rows except mean, if any of the ch columns is less than counts_per_day_alive, add 1 to n_of_dead_flies
            for index, row in data_df_total.iterrows():
                if index != 'Mean':
                    for ch in available_channels:
                        if row[ch] < dead_fly_threshold:
                            n_of_dead_flies += 1
                            available_channels.remove(ch)
                            unavailble_channels.append(ch)
                            break
            n_of_alive_flies = n_of_all_flies - n_of_dead_flies
            st.session_state.unavailble_channels = unavailble_channels
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
            locomotor_day_unpivoted = individual_locomotor_activity_day.melt(id_vars=['Date'], value_vars=numeric_cols, var_name='Channel', value_name='Counts')
            locomotor_day_unpivoted_alive = locomotor_day_unpivoted[locomotor_day_unpivoted['Channel'].isin(available_channels)]
            locomotor_activity_by_day = locomotor_day_unpivoted_alive.groupby('Date')['Counts'].agg(['mean', 'sum', 'std', 'sem']).reset_index()
            

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
            st.session_state.sleep_analysis_df = sleep_analysis_df
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
            
            fig, ax = plt.subplots(figsize=(6, 3))  # Adjust the figure size
            ax.bar(Daily_locomotor_activity['Condition'], Daily_locomotor_activity['Mean'], yerr=Daily_locomotor_activity['SEM'], capsize=5, color='grey')
            ax.set_xlabel('Condition')
            ax.set_ylabel('Mean Activity')
            ax.set_title('Mean Activity by Condition')
            ax.set_yticks([3000, 6000, 9000])  # Set y-axis ticks
            st.session_state.fig_summary = fig
                    # Make a download button to download the Daily_locomotor_activity dataframe
                    # Convert the dataframe to a CSV
            csv = Daily_locomotor_activity.to_csv(index=False)

            fig, ax = plt.subplots(figsize=(8, 4))
            st.session_state.df_by_LD_DD = df_by_LD_DD
            st.session_state.fig_by_LD_DD = fig  # Save the graph too
                        # Plot individual points for mean activity
            locomotor_activity_by_day = locomotor_activity_by_day[locomotor_activity_by_day['Date'] != 'Mean']
            locomotor_activity_by_day['Date'] = pd.to_datetime(locomotor_activity_by_day['Date'])
            ax.scatter(locomotor_activity_by_day['Date'], locomotor_activity_by_day['mean'], color='black', marker='o', s=50, label='Mean Activity')
                        # Plot error bars for SEM
            for i, row in locomotor_activity_by_day.iterrows():
                ax.errorbar(row['Date'], row['mean'], yerr=row['sem'], fmt='none', ecolor='grey', elinewidth=2, capsize=5, alpha=0.5)
            ax.set_xlabel('Date')
            ax.set_ylabel('Mean Activity')
            ax.set_title('Mean Activity by Day')
            st.session_state.fig_by_day = fig
                    # Make the download button
                    # Convert the dataframe to a CSV
            csv = locomotor_activity_by_day.to_csv(index=False)

                        # Sort the data to ensure LD comes first and DD comes second
            df_by_LD_DD = df_by_LD_DD.sort_values(by='Light_status', key=lambda x: x.map({'LD': 0, 'DD': 1}))

                        # Make the graph for df_by_LD_DD
            fig, ax = plt.subplots(figsize=(6, 4))
            colors = {'LD': 'yellow', 'DD': 'blue'}
            edge_colors = 'black'  # Black borders around the bars
            ax.bar(df_by_LD_DD['Light_status'], df_by_LD_DD['mean'], yerr=df_by_LD_DD['sem'], capsize=5, 
                color=[colors[cycle] for cycle in df_by_LD_DD['Light_status']], edgecolor=edge_colors)
            ax.set_xlabel('Light Cycle')
            ax.set_ylabel('Mean Activity')
            ax.set_title('Mean Activity by Light Cycle')
            ax.set_yticks([2500, 5000, 7500])
            ax.legend(handles=[plt.Line2D([0], [0], color='yellow', lw=4, label='Day (LD)'),
                                        plt.Line2D([0], [0], color='blue', lw=4, label='Night (DD)')], loc='upper right')
            st.session_state.fig_by_LD_DD = fig
                    # Make the download button
                    # Convert the dataframe to a CSV
            csv = df_by_LD_DD.to_csv(index=False)

            st.session_state.daily_locomotor_activity = Daily_locomotor_activity
            st.session_state.locomotor_activity_by_day = locomotor_activity_by_day
            st.session_state.df_by_LD_DD = df_by_LD_DD
            st.session_state.fig_sleep_grouped_night = fig

            
            tab0, tab1, tab2, tab3, tab4 = st.tabs(["Daily Sleep", "Average Sleep", "Individual Sleep", "Sleep Bout", "Raw Data"])
        
            sleep_analysis_df = st.session_state.sleep_analysis_df
            sleep_analysis_df['zt_time'] = sleep_analysis_df['Date_Time'].apply(zeitgeber_time)
            numeric_cols = st.session_state.numeric_cols
            sleep_analysis_df.columns = ['Index', 'Date', 'Time', 'LDD-DD', 'Status', 'Monitor_Number', 'Extras', 'Tube_Number', 'Data_Type', 'Light_Sensor', 'ch1', 'ch2', 'ch3', 'ch4', 'ch5', 'ch6', 'ch7', 'ch8', 'ch9', 'ch10', 'ch11', 'ch12', 'ch13', 'ch14', 'ch15', 'ch16', 'ch17', 'ch18', 'ch19', 'ch20', 'ch21', 'ch22', 'ch23', 'ch24', 'ch25', 'ch26', 'ch27', 'ch28', 'ch29', 'ch30', 'ch31', 'ch32', 'Date_Time', 'LD_DD', 'zt_time']
            df_sleep_trim = sleep_analysis_df[['Date_Time', 'zt_time'] + list(numeric_cols)]
            unavailable_channels = st.session_state.unavailble_channels
            available_channels = st.session_state.available_channels
            df_sleep_trim_alive = df_sleep_trim.drop(unavailable_channels, axis=1)
            df_sleep_trim_alive = df_sleep_trim_alive.set_index('Date_Time')
            numeric_df_sleep_trim_alive = df_sleep_trim_alive.select_dtypes(include=['number'])
            sleep_calc_df = numeric_df_sleep_trim_alive.rolling(5).sum().applymap(lambda x: 1 if x == 0 else 0)
            sleep_calc_df['zt_time'] = df_sleep_trim_alive.index.to_series().apply(zeitgeber_time)
            sleep_calc_df = sleep_calc_df.reset_index()
            sleep_calc_df['mean'] = sleep_calc_df[available_channels].mean(axis=1)
            sleep_calc_df['sem'] = sleep_calc_df[available_channels].sem(axis=1)

            print(sleep_calc_df.columns.tolist())

            with tab0:
                st.header('Daily Sleep Profiles')
                # --- Concatenate all days into a single line profile (sequential index) ---
                # We'll use sleep_calc_df, which has 'Date_Time' and 'mean' columns (mean sleep across available channels)

                # Prepare data for plotting
                daily_sleep_df = sleep_calc_df.copy()

                n_points = 250  # Number of points to plot
                total_points = len(daily_sleep_df)
                if total_points > n_points:
                    indices = np.linspace(0, total_points - 1, n_points, dtype=int)
                    plot_df = sleep_calc_df.iloc[indices]
                else:
                    plot_df = sleep_calc_df

                plot_df = plot_df.sort_values('Date_Time').reset_index(drop=True)
                # Create a sequential index for the x-axis
                plot_df['Sequential_Index'] = range(len(plot_df))
                # Keep time of day for hover
                plot_df['Time'] = plot_df['Date_Time'].dt.time

                fig = px.line(
                    plot_df,
                    x='Sequential_Index',
                    y='mean',
                    labels={'mean': 'Mean Sleep', 'Sequential_Index': 'Time (H)'},
                    title='Daily Sleep Profile'
                )
                fig.update_traces(
                    hovertemplate='Time: %{customdata[0]}<br>Mean Sleep: %{y:.2f}',
                    customdata=plot_df[['Time']]
                )
                
                st.plotly_chart(fig, use_container_width=True)
                st.session_state.fig_daily_sleep_profile = fig

            with tab1:
                st.header('Average Sleep Analysis')
                col1, col2 = st.columns(2)

                with col1:
                    # Average Sleep List
                    
                    avg_sleep_df = sleep_calc_df.copy()
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
                        bin_mean = sum(mean_values) / len(mean_values)
                        bin_sem = pd.Series(mean_values).sem()
                        avg_sleep_list.append([i, bin_mean, bin_sem])
                    avg_sleep_list_df = pd.DataFrame(avg_sleep_list, columns=['time', 'mean', 'sem'])
                    avg_sleep_list_df['zt_time'] = pd.to_datetime(avg_sleep_list_df['time'], unit='m').dt.time

                    #only keep the first instances of each zt_time
                    avg_sleep_list_df = avg_sleep_list_df.drop_duplicates(subset='zt_time', keep='first')

                    #add a Condition column with the condition name
                    avg_sleep_list_df['Condition'] = condition_name

                    #Make the columns go in the order of time, zt_time, condition, mean, sem
                    avg_sleep_list_df = avg_sleep_list_df[['time', 'zt_time', 'Condition', 'mean', 'sem']]
                    st.session_state.avg_sleep_list_df = avg_sleep_list_df
                    avg_sleep_list_df.columns = ['Time', 'ZT_Time', 'Condition', 'Mean','SEM']

                    #change the names of the columns to Dec_time, Dec_ZT_time, Condition, mean_binned_sleep, sem_binned_sleep
                    avg_sleep_list_df.columns = ['Dec_time', 'Dec_ZT_time', 'Condition', 'mean_binned_sleep','sem_binned_sleep']

                    #convert zt_time to actual zeigterberg time. it should start at 0 when dec_time is at 360 and then add 30 to each interval after that
                    avg_sleep_list_df['Dec_ZT_time'] = avg_sleep_list_df['Dec_time'].apply(lambda x: x/60)
                    avg_sleep_list_df['Dec_ZT_time'] = avg_sleep_list_df['Dec_ZT_time'] - 6
                    avg_sleep_list_df['Dec_ZT_time'] = avg_sleep_list_df['Dec_ZT_time'].apply(lambda x: x if x >= 0 else x + 24)
                    #multiply Dec_zt_time by 60
                    avg_sleep_list_df['Dec_ZT_time'] = avg_sleep_list_df['Dec_ZT_time'] * 60

                    st.write("Average Sleep List")
                    st.write(avg_sleep_list_df)

                    csv = avg_sleep_list_df.to_csv(index=False)

                    #add a download button
                    st.download_button(
                        label="Download average sleep list as CSV",
                        data=csv,
                        file_name='avg_sleep_list.csv',
                        mime='text/csv'
                        )
                    
                    
                    # Sort Dec_ZT_time column in chronological order
                    avg_sleep_list_df = avg_sleep_list_df.sort_values(by="Dec_ZT_time")

                    # Convert Dec_ZT_time to hours
                    hours = avg_sleep_list_df['Dec_ZT_time'] / 60
                    avg_sleep_list_df['ZT_time_in_hours'] = hours

                    # Calculate Sleep_30min and SEM_30min
                    avg_sleep_list_df['Sleep_30min'] = avg_sleep_list_df['mean_binned_sleep'] * 30
                    avg_sleep_list_df['SEM_30min'] = avg_sleep_list_df['sem_binned_sleep'] * 30
            
                    # remove the 'Unamed: 0' column
                    #avg_sleep_list_df = avg_sleep_list_df.drop(columns=['Unnamed: 0'])

                    #Clone table
                    table1 = avg_sleep_list_df.copy()
                    st.write(avg_sleep_list_df)
                    #Make a download data button
                    st.download_button('Download Entire Table', avg_sleep_list_df.to_csv(), file_name='average_sleep.csv', mime='text/csv')

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
                    st.download_button('Download Specific Column', table1.to_csv(), file_name='average_sleep.csv', mime='text/csv')

                    # create plotly express scatter plot
                    fig = px.scatter(avg_sleep_list_df, x='ZT_time_in_hours', y='Sleep_30min', error_y='SEM_30min', title='Average Sleep', labels={'ZT_time_in_hours':'ZT time in hours', 'Sleep_30min':'Sleep per 30min'})
                    st.plotly_chart(fig)
                    st.session_state.fig_avg_sleep = fig

            with tab2:

                st.header('Individual Sleep Analysis')
                col1, col2 = st.columns(2)
                with col1:
                    # Individual Day/Night Mean
                    def day_night(dt):
                        if dt.time() >= pd.to_datetime('06:00').time() and dt.time() <= pd.to_datetime('18:00').time():
                            return 'Day'
                        else:
                            return 'Night'
                    ind_day_night = sleep_calc_df.copy()
                    ind_day_night['Day_Night'] = ind_day_night['Date_Time'].apply(day_night)
                    ind_day_night = ind_day_night[['Day_Night'] + available_channels]
                    ind_day_night_unpivoted = ind_day_night.melt(id_vars=['Day_Night'], value_vars=available_channels, var_name='Channel', value_name='Counts')
                    ind_day_night_mean = ind_day_night_unpivoted.groupby(['Day_Night', 'Channel'])['Counts'].mean().reset_index()
                    ind_day_night_mean.sort_values(['Channel', 'Day_Night'], inplace=True)
                    ind_day_night_mean.reset_index(drop=True, inplace=True)

                    #add the condition column
                    ind_day_night_mean['Condition'] = condition_name

                    #Make the columns go bo the order of Channel, Condition, Light_status, mean_sleep_per_ind
                    ind_day_night_mean = ind_day_night_mean[['Channel', 'Condition', 'Day_Night', 'Counts']]
                    ind_day_night_mean.columns = ['Channel', 'Condition', 'Light_status', 'mean_sleep_per_ind']
                    st.session_state.ind_day_night_mean = ind_day_night_mean

                    st.write("Individual Day/Night Mean")
                    st.write(ind_day_night_mean)

                    fig = px.box(
                        ind_day_night_mean,
                        x='Condition',
                        y='mean_sleep_per_ind',
                        points=False,
                        labels={'Condition': st.session_state.condition_name, "mean_sleep_per_ind": "Mean Sleep per Individual"},
                        title="Total Sleep in LD"
                    )
                    st.plotly_chart(fig, use_container_width=True)
                    st.session_state.fig_total_sleep_in_LD = fig

                with col2:
                    st.write("Individual Sleep Profiles in LD")
                    
                    df = ind_day_night_mean

                    #Get the number
                    df['Channel#'] = df['Channel'].str.extract(r'(\d+)$').astype(int)

                    #Sort it by Day/Night column and then by Channel# column
                    df = df.sort_values(by=['Light_status', 'Channel#'])

                    #Sort it by the column "Condition"

                    #Make a new dataframe takes each Channel# and its corresponding Light_stats sleep status
                    #This means that the new dataframe should only have 3 columns, the channel#, the day_mean_sleep_per_ind, and the night_mean_sleep_per_ind
                    #The day or night mean_slep_per_ind is the one that corresponds to the Light_status column
                    df_new = pd.DataFrame()
                    df_new['Channel#'] = df['Channel#'].unique()
                    day_df = df[df['Light_status'] == 'Day'][['Channel#', 'mean_sleep_per_ind']].rename(columns={'mean_sleep_per_ind': 'day_mean_sleep_per_ind'})
                    day_df['Condition'] = condition_name
                    night_df = df[df['Light_status'] == 'Night'][['Channel#', 'mean_sleep_per_ind']].rename(columns={'mean_sleep_per_ind': 'night_mean_sleep_per_ind'})
                    night_df['Condition'] = condition_name
                    df_new = pd.merge(day_df, night_df, on='Channel#', how='outer').fillna(0)


                    fig_day = px.box(
                        day_df,
                        x='Condition',
                        y='day_mean_sleep_per_ind',
                        points=False,
                        labels={"Channel#": st.session_state.condition_name, "day_mean_sleep_per_ind": "Day Mean Sleep per Individual"},
                        title="Daytime Sleep in LD"
                    )
                    st.plotly_chart(fig_day, use_container_width=True)
                    st.session_state.fig_daytime_sleep_in_LD = fig_day

                    fig_night = px.box(
                        night_df,
                        x='Condition',
                        y='night_mean_sleep_per_ind',
                        points=False,
                        labels={"Channel#": st.session_state.condition_name, "night_mean_sleep_per_ind": "Night Mean Sleep per Individual"},
                        title="Nighttime Sleep in LD"
                    )
                    st.plotly_chart(fig_night, use_container_width=True)
                    st.session_state.fig_nighttime_sleep_in_LD = fig_night

                    #Add on the "Condition" column to the new dataframe, sort it by that column
                    df_new = pd.merge(df_new, df[['Channel#', 'Condition']].drop_duplicates(), on='Channel#', how='outer').fillna(0)


                    #Make it so that the Channel# column is the index
                    df_new = df_new.set_index('Channel#')

                    #Multiply day/night mean_sleep_per_ind by 30 to get sleep/30 for both day and night
                    #label these columns day_sleep_per_30, night_sleep_per_30
                    df_new['day_sleep_per_30'] = df_new['day_mean_sleep_per_ind'] * 30
                    df_new['night_sleep_per_30'] = df_new['night_mean_sleep_per_ind'] * 30

                    #Multiply mean_sleep_per_ind by 720 to get total sleep(min) for botbh day and night data
                    #label these columns day_total_sleep(min), night_total_sleep(min)
                    df_new['day_total_sleep(min)'] = df_new['day_mean_sleep_per_ind'] * 720
                    df_new['night_total_sleep(min)'] = df_new['night_mean_sleep_per_ind'] * 720

                    #add both day_total_sleep(min) and night_total_sleep(min) to get total_sleep(min)
                    #Divide total_sleep(min) by 60 to get total_sleep_per_day
                    df_new['total_sleep(min)'] = df_new['day_total_sleep(min)'] + df_new['night_total_sleep(min)']
                    df_new['total_sleep_per_day'] = df_new['total_sleep(min)'] / 60

                    #Create a new dataframe called data_df that has the following columns: Channel#, day_sleep_per_30, night_sleep_per_30, total_sleep_per_day
                    data_df = pd.DataFrame()
                    data_df['Channel#'] = df_new.index

                    #Add back the condition column
                    data_df['Condition'] = df_new['Condition'].values

                    data_df['day_sleep_per_30'] = df_new['day_sleep_per_30'].values
                    data_df['night_sleep_per_30'] = df_new['night_sleep_per_30'].values
                    data_df['total_sleep_per_day'] = df_new['total_sleep_per_day'].values

                    #again, make it so that the Channel# column is the index
                    data_df = data_df.set_index('Channel#')

                    #Sort the data_df by the conditions column
                    data_df = data_df.sort_values(by='Condition')

                    data_df1 = data_df.copy()

                    #Get each unique condition
                    conditions = data_df['Condition'].unique()

                    #Make a drop down menu for the user to select the condition
                    condition = st.selectbox('Select Condition', conditions)

                    #Filter the data_df by the selected condition
                    data_df = data_df[data_df['Condition'] == condition]



                    #Show data_df dataframe on the streamlit with an option to download it
                    st.write(data_df)
                    st.download_button('Download Data', data_df.to_csv(), 'data.csv', 'text/csv')

                    #Add the conditions to the dataframe and print that one, make a button to download everything
                    st.write(data_df1)
                    st.download_button('Download Data with Conditions', data_df1.to_csv(), 'data_with_conditions.csv', 'text/csv')



            with tab3:
                # Individual Sleep Bout
                bout_data = []
                for col in available_channels:
                    changes = sleep_calc_df[col].diff().fillna(0).apply(lambda x: 1 if x != 0 else 0)
                    change_indices = changes[changes == 1].index
                    prev_value = sleep_calc_df.at[change_indices[0], col] if change_indices.size > 0 else None
                    prev_time = sleep_calc_df.at[change_indices[0], 'Date_Time'] if change_indices.size > 0 else None
                    for idx in change_indices:
                        current_value = sleep_calc_df.at[idx, col]
                        current_time = sleep_calc_df.at[idx, 'Date_Time']
                        zt_time = zeitgeber_time(prev_time)
                        if prev_value is not None and prev_value != current_value:
                            bout_length = (current_time - prev_time).total_seconds() / 60
                            bout_data.append({
                                'Channel': col,
                                'Condition': 'wt',
                                'Light_Cycle': 'LD',
                                'Date': 'NA',
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
                st.session_state.ind_sleep_bout_df = ind_sleep_bout_df
                st.header("Sleep Bout Analysis")
                
                

                # split the Time column into a Date and Time column
                ind_sleep_bout_df['Time'] = pd.to_datetime(ind_sleep_bout_df['Time'])
                ind_sleep_bout_df['Date'] = ind_sleep_bout_df['Time'].dt.date
                ind_sleep_bout_df['Time'] = ind_sleep_bout_df['Time'].dt.time
                ind_sleep_bout_df['ZT_Time'] = ind_sleep_bout_df['ZT_Time'].dt.time
                print(ind_sleep_bout_df)

                st.write(ind_sleep_bout_df)

                #give an option to download the data in this format
                st.download_button('Download Sleep Bout Table', ind_sleep_bout_df.to_csv(), 'sleep_bout.csv', 'text/csv')

                start_date = ind_sleep_bout_df['Date'].iloc[0]
                end_date = ind_sleep_bout_df['Date'].iloc[-1]

                # create list of unique Channel
                channels = ind_sleep_bout_df['Channel'].unique()
                
                # add multi-select for day, night, or both with both selected by default
                day_or_night = st.multiselect('Day or Night', ['day', 'night'], default=['day', 'night'])
            
                # check if day_or_night is empty and then add day and night back in
                if len(day_or_night) == 0:
                    day_or_night = ['day', 'night']

                # filter sleep_count = 0
                ind_sleep_bout_df = ind_sleep_bout_df[ind_sleep_bout_df['Sleep_Count'] != 0]

                # filter rows where bout_length < 5
                ind_sleep_bout_df = ind_sleep_bout_df[ind_sleep_bout_df['Bout_Length'] >= 5]

                # create column called 'day_or_night' where Dec_ZT_time = 0 to 720 is day, DecZT_time 721 to 1080 is night
                ind_sleep_bout_df['day_or_night'] = ind_sleep_bout_df['Dec_ZT_Time'].apply(lambda x: 'day' if x < 720 else 'night')

                # filter by day or night
                ind_sleep_bout_df = ind_sleep_bout_df[ind_sleep_bout_df['day_or_night'].isin(day_or_night)]

                
                # filter by date range - make sure to convert date_range to date format
                ind_sleep_bout_df = ind_sleep_bout_df[(ind_sleep_bout_df['Date'] >= start_date) & (ind_sleep_bout_df['Date'] <= end_date)]

                # create column bout_lengths/sleep_counts
                ind_sleep_bout_df['bout_length_per_sleep_counts'] = ind_sleep_bout_df['Bout_Length'] / ind_sleep_bout_df['Sleep_Count']

                # create a column called 'channel_num' where Monitor9_ch1 is 1, Monitor9_ch2 is 2, etc.
                ind_sleep_bout_df['channel_num'] = ind_sleep_bout_df['Channel'].apply(lambda x: int(x.split('ch')[-1]))

                # group by time_of_day, channel, date and then sum and average bout and bout_length
                grouped = ind_sleep_bout_df.groupby(['day_or_night', 'Channel', 'channel_num', 'Condition', 'Date']).agg({'Bout': ['sum'], 'Bout_Length': ['sum', 'mean']}).reset_index()

                # sort grouped by channel_num and date
                grouped = grouped.sort_values(['day_or_night','channel_num', 'Date'])

                # format bout_length mean to 2 decimal places
                grouped['Bout_Length', 'mean'] = grouped['Bout_Length', 'mean'].apply(lambda x: round(x, 2))

                # transform the multi-index columns to single index
                grouped.columns = ['_'.join(col).strip() for col in grouped.columns.values]

                # replace columns that end with '_' with ''
                grouped.columns = grouped.columns.str.replace('_$', '', regex=True)

                # create a new grouped dataframe that is grouped by day_or_night, channel_num and averages bout sum and bout_length mean
                grouped2 = grouped.groupby(['day_or_night', 'Channel', 'channel_num', 'Condition']).agg({'Bout_sum': ['mean'], 'Bout_Length_mean': ['mean']}).reset_index()

                # sort by channel_num
                grouped2 = grouped2.sort_values(['day_or_night', 'channel_num'])

                # transform the multi-index columns to single index
                grouped2.columns = ['_'.join(col).strip() for col in grouped2.columns.values]

                # replace columns that end with '_' with ''
                grouped2.columns = grouped2.columns.str.replace('_$', '', regex=True)

                # format bout_sum_mean and bout_length_mean_mean to 2 decimal places
                grouped2['Bout_sum_mean'] = grouped2['Bout_sum_mean'].apply(lambda x: round(x, 2))
                grouped2['Bout_Length_mean_mean'] = grouped2['Bout_Length_mean_mean'].apply(lambda x: round(x, 2))

                #Group the header by the collumn "Condition"
                grouped2 = grouped2.sort_values(by=['Condition'])

                st.session_state.grouped = grouped
                st.session_state.grouped2 = grouped2


                # create 2 streamlit columns
                col1, col2 = st.columns(2)

                
                #Move the condition collumn to the second collumn in both grouped and grouped2
                grouped = grouped[['day_or_night', 'Condition', 'Channel', 'channel_num', 'Date', 'Bout_sum', 'Bout_Length_sum', 'Bout_Length_mean']]
                grouped2 = grouped2[['day_or_night', 'Condition', 'Channel', 'channel_num', 'Bout_sum_mean', 'Bout_Length_mean_mean']]
                

                #make copies of grouped and grouped 2
                grouped1 = grouped.copy()
                grouped2_1 = grouped2.copy()


                #Sort each by the condition column
                grouped1 = grouped.sort_values(by='Condition')
                grouped2_1 = grouped2.sort_values(by='Condition')
                

                # print the grouped dataframe
                col1.header('Grouped By Day')

                # add download link for grouped dataframe
                col1.download_button('Download Grouped Data', grouped.to_csv(index=False), 'grouped.csv', 'text/csv')

                # create plotly express density plot
                fig = px.density_contour(grouped, x='Bout_Length_mean', y='Bout_sum', marginal_x='histogram', marginal_y='histogram')
                col1.plotly_chart(fig)

                # Box plot for Bout_Length_mean by Condition (from grouped)
                col1.subheader("Sleep Bout Length in LD")
                if not grouped.empty:
                    fig_bout_length = px.box(
                        grouped,
                        x='Condition',
                        y='Bout_Length_mean',
                        points=False,
                        labels={"Condition": "Condition", "Bout_Length_mean": "Bout Length Mean"},
                        title="Bout Length Mean in LD"
                    )
                    col1.plotly_chart(fig_bout_length, use_container_width=True)

                col1.dataframe(grouped, hide_index=True)
                st.session_state.fig_bout_length_mean_by_condition = fig_bout_length

                # print the grouped2 dataframe
                col2.header('Grouped By Channel')

                
                # add download link for grouped2 dataframe
                col2.download_button('Download Grouped2 Data', grouped2.to_csv(index=False), 'grouped2.csv', 'text/csv')

                # create plotly express density plot
                fig = px.density_contour(grouped2, x='Bout_sum_mean', y='Bout_Length_mean_mean', marginal_x='histogram', marginal_y='histogram')
                col2.plotly_chart(fig)

                # Box plot for Bout_sum_mean by Condition (from grouped2)
                col2.subheader("Sleep Bout Sum in LD")
                if not grouped2.empty:
                    fig_bout_sum = px.box(
                        grouped2,
                        x='Condition',
                        y='Bout_sum_mean',
                        points=False,
                        labels={"Condition": "Condition", "Bout_sum_mean": "Bout Sum Mean"},
                        title="Bout Sum Mean in LD"
                    )
                    col2.plotly_chart(fig_bout_sum, use_container_width=True)
                    st.session_state.fig_bout_sum_mean_by_condition = fig_bout_sum

                # print the dataframe without the index
                col2.dataframe(grouped2, hide_index=True)
                st.session_state.fig_sleep_bout_by_channel = fig
                #Get each unique conditions in grouped1
                conditions = grouped1['Condition'].unique()
                #Get each unique conditions in grouped2_1
                conditions2 = grouped2_1['Condition'].unique()
                #Make a drop down of both conditions and conditions2
                condition = col1.selectbox('Select Condition for day', conditions)
                condition2 = col2.selectbox('Select Condition for night', conditions2)
                #Filter the grouped1 dataframe by the selected condition
                grouped1 = grouped1[grouped1['Condition'] == condition]
                #Filter the grouped2_1 dataframe by the selected condition
                grouped2_1 = grouped2_1[grouped2_1['Condition'] == condition2]
                #Show the grouped1 dataframe
                col1.dataframe(grouped1, hide_index=True)
                #Show the grouped2_1 dataframe
                col2.dataframe(grouped2_1, hide_index=True)
                #Add a download button for both grouped1 and grouped2_1
                col1.download_button('Download Grouped Day Data', grouped1.to_csv(index=False), 'grouped1.csv', 'text/csv')
                col2.download_button('Download Grouped Night Data', grouped2_1.to_csv(index=False), 'grouped2_1.csv', 'text/csv')
                saved_time = st.session_state.get('saved_time', None)
                condition_name = st.session_state.get('condition_name', 'wt')
                save_analysis()

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

with tab1:
    import os
    import pickle
    import streamlit as st

    with st.expander("Saved Analyses", expanded=True):
        st.subheader("List of Saved Analyses")
        analyses_dir = "saved_analysis"
        analyses = []

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
                            
                        # Show tables (DataFrames)
                        for key, value in analysis_obj.items():
                            if hasattr(value, "to_csv"):  # Likely a DataFrame
                                st.write(f"**Table: {key}**")
                                st.dataframe(value)
                        # Show graphs (Plotly or Matplotlib figures)
                        for key, value in analysis_obj.items():
                            # Plotly Figure
                            try:
                                import plotly.graph_objs as go
                                if "plotly" in str(type(value)).lower():
                                    st.write(f"**Plotly Graph: {key}**")
                                    st.plotly_chart(value, use_container_width=True)
                            except ImportError:
                                pass
                            # Matplotlib Figure
                            try:
                                import matplotlib.pyplot as plt
                                from matplotlib.figure import Figure
                                if isinstance(value, Figure):
                                    st.write(f"**Matplotlib Graph: {key}**")
                                    st.pyplot(value)
                            except ImportError:
                                pass
                    except Exception as e:
                        st.error(f"Could not load {selected_file}: {e}")
            else:
                st.info("No analyses found in the directory.")
        else:
            st.info("No analyses have been saved yet.")

with tab2:
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

    st.title("Monitor Analysis Comparison")

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
