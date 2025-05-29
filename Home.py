import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta, time
import os
import json
import pickle

# set wide layout mode
st.set_page_config(layout="wide")

# Create a directory to save monitor files and settings
SAVE_DIR = "saved_monitors"
if not os.path.exists(SAVE_DIR):
    os.makedirs(SAVE_DIR)

def get_default_monitor_settings():
    return {
        "conditions": [{
            "name": "wt",
            "fly_count": 32,
            "monitor_order": ["Monitor 1"],
            "plot_colors": ["#BEBEBE"]
        }],
        "ld_dd_analysis": "LD",
        "dam_settings": {
            "dam_frequency": 1,
            "dead_fly_threshold": 100,
            "light_onset_time": "06:00"
        },
        "ld_dd_settings": {
            "start_date": "01 Jan 24 00:00:00",
            "end_date": "01 Jan 24 23:59:59",
            "LD_DD_Analysis": "LD"
        }
    }

def save_monitor_settings(monitor_name, settings):
    filepath = os.path.join(SAVE_DIR, "all_monitor_settings.json")

    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            all_settings = json.load(f)
    else:
        all_settings = {}

    all_settings[monitor_name] = settings

    with open(filepath, 'w') as f:
        json.dump(all_settings, f, indent=2)

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

def load_monitor_settings(monitor_name):
    filepath = os.path.join(SAVE_DIR, "all_monitor_settings.json")
    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            all_settings = json.load(f)
        return all_settings.get(monitor_name)
    return None

def load_monitor_file(monitor_name):
    """Load monitor file data"""
    filepath = os.path.join(SAVE_DIR, f"{monitor_name}.pkl")
    if os.path.exists(filepath):
        with open(filepath, 'rb') as f:
            return pickle.load(f)
    return None

def get_saved_monitors():
    filepath = os.path.join(SAVE_DIR, "all_monitor_settings.json")
    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            all_settings = json.load(f)
        return list(all_settings.keys())
    return []

def delete_monitor_settings(monitor_name):
    filepath = os.path.join(SAVE_DIR, "all_monitor_settings.json")
    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            all_settings = json.load(f)
        if monitor_name in all_settings:
            del all_settings[monitor_name]
            with open(filepath, 'w') as f:
                json.dump(all_settings, f, indent=2)

#Create a header
st.write("# Settings and Daily Locomotor Activity Analysis")

# Monitor dropdown
st.sidebar.subheader("Saved Monitors")
saved_monitors = get_saved_monitors()
selected_monitor = st.sidebar.selectbox("Select Saved Monitor", ["None"] + saved_monitors)


# Initialize session state for current monitor
if 'current_monitor' not in st.session_state:
    st.session_state.current_monitor = None
    st.session_state.monitor_settings = {}
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

        # Prepopulate widget session state
        for key, value in settings.items():
            if key == "conditions":
                for i, cond in enumerate(value):
                    st.session_state[f'condition_{i}_name'] = cond["name"]
                    st.session_state[f'condition_{i}_fly_count'] = cond["fly_count"]
                    for j, monitor_order in enumerate(cond["monitor_order"]):
                        st.session_state[f'condition_{i}_monitor_{j}_order'] = monitor_order
                    for j, color in enumerate(cond["plot_colors"]):
                        st.session_state[f'condition_{i}_monitor_{j}_color'] = color
            elif key == "ld_dd_analysis":
                st.session_state["ld_dd_analysis"] = value
            elif key == "dam_settings":
                st.session_state["dam_frequency"] = value.get("dam_frequency", 1)
                st.session_state["dead_fly_threshold"] = value.get("dead_fly_threshold", 100)
                st.session_state["light_onset_time"] = datetime.strptime(value.get("light_onset_time", "06:00"), "%H:%M").time()
            elif key == "ld_dd_settings":
                st.session_state["ld_start_date"] = datetime.strptime(value.get("start_date", "01 Jan 24 00:00:00"), "%d %b %y %H:%M:%S").date()
                st.session_state["ld_end_date"] = datetime.strptime(value.get("end_date", "01 Jan 24 23:59:59"), "%d %b %y %H:%M:%S").date()
                st.session_state["dd_start_date"] = st.session_state["ld_end_date"] + timedelta(days=1)
                st.session_state["dd_end_date"] = st.session_state["dd_start_date"] + timedelta(days=7)
        # Force app to rerun with updated state
        st.rerun()   

# Initialize monitor settings if not already set
    if settings:
        st.session_state.monitor_settings = settings
        st.session_state.current_monitor = selected_monitor
        
        # Force populate widget states
        for i, cond in enumerate(settings.get("conditions", [])):
            st.session_state[f'condition_{i}_name'] = cond["name"]
            st.session_state[f'condition_{i}_fly_count'] = cond["fly_count"]
            # Similarly for other condition fields
            
        st.session_state["ld_dd_analysis"] = settings.get("ld_dd_analysis", "LD")
        # Similarly for other settings
        
        # Force rerun to apply the loaded settings
        st.rerun()

    

# --- File Upload ---
uploaded_files = st.sidebar.file_uploader("Upload New DAM Monitor File", accept_multiple_files=True, type=['txt'])

if uploaded_files:
    # Store uploaded files in session state
    st.session_state.uploaded_files = uploaded_files
    st.session_state.current_monitor = None  # Reset current monitor when new files are uploaded

# --- Save Monitor Section ---
if st.session_state.uploaded_files:
    st.sidebar.subheader("Save Monitor")
    monitor_name = st.sidebar.text_input(
        "Monitor Name",
        value=st.session_state.current_monitor if st.session_state.get("current_monitor") else ""
)
    
    if st.sidebar.button("Save Monitor and Settings"):
        if monitor_name:
            # Save the file data
            save_monitor_file(monitor_name, st.session_state.uploaded_files[0])
            
            # Save the settings
            save_monitor_settings(monitor_name, st.session_state.monitor_settings)
            
            st.sidebar.success(f"Monitor '{monitor_name}' saved successfully!")
        else:
            st.sidebar.error("Please enter a monitor name")

#Reset settings to default button
if selected_monitor != "None":
    if st.sidebar.button("Reset Settings to Default"):
        # 1. Get default settings
        default_settings = get_default_monitor_settings()
        
        # 2. Save to file
        save_monitor_settings(selected_monitor, default_settings)
        
        # 3. Clear ALL relevant widget states
        keys_to_clear = [
            k for k in st.session_state.keys() 
            if (k.startswith("condition_") or 
                k in ["ld_dd_analysis", "dam_frequency", "dead_fly_threshold", 
                      "light_onset_time", "ld_start_date", "ld_end_date",
                      "dd_start_date", "dd_end_date", "num_conditions_input"])
        ]
        for key in keys_to_clear:
            if key in st.session_state:
                del st.session_state[key]
        
        # 4. Preload default values into session state
        st.session_state.monitor_settings = default_settings
        st.session_state.update({
            "ld_dd_analysis": default_settings["ld_dd_analysis"],
            "dam_frequency": default_settings["dam_settings"]["dam_frequency"],
            "dead_fly_threshold": default_settings["dam_settings"]["dead_fly_threshold"],
            "light_onset_time": datetime.strptime(
                default_settings["dam_settings"]["light_onset_time"], 
                "%H:%M"
            ).time()
        })
        
        # 5. Force immediate visual update
        st.rerun()

LD_start = '06:00'
DD_start = '18:00'

if st.session_state.uploaded_files:
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

            for j, file in enumerate(st.session_state.uploaded_files):
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

        # First try to read the file to get date range
        try:
            # Read the first uploaded file as bytes and decode
            bytes_data = st.session_state.uploaded_files[0].getvalue()
            string_data = bytes_data.decode('utf-8')
            
            # Use StringIO to create a file-like object
            from io import StringIO
            df_temp = pd.read_csv(StringIO(string_data), sep='\t', header=None)
            
            # Check if we got data
            if not df_temp.empty:
                # Assign column names (adjust based on your actual format)
                df_temp.columns = ['Index','Date','Time','LD-DD','Status','Extras','Monitor_Number',
                                 'Tube_Number','Data_Type','Light_Sensor'] + [f'data_{i}' for i in range(1, 33)]
                
                # Create datetime column
                df_temp['DateTime'] = pd.to_datetime(df_temp['Date'] + ' ' + df_temp['Time'], 
                                                    format='%d %b %y %H:%M:%S', errors='coerce')
                
                # Get min and max dates
                min_date = df_temp['DateTime'].min().date()
                max_date = df_temp['DateTime'].max().date()
            else:
                min_date = datetime(2024, 1, 1).date()
                max_date = datetime(2024, 1, 31).date()
                st.warning("File appears empty, using default dates")
                
        except Exception as e:
            st.error(f"Error reading file: {str(e)}")
            min_date = datetime(2024, 1, 1).date()
            max_date = datetime(2024, 1, 31).date()

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
    with col3:
        st.subheader("DAM System Settings")

        # DAM system data acquisition frequency
        dam_frequency = st.number_input("Enter the frequency in minutes", 
                                      min_value=1, max_value=60, 
                                      value=st.session_state.monitor_settings.get('dam_frequency', 1),
                                      key='dam_frequency')

        # Threshold for identifying dead flies
        dead_fly_threshold = st.number_input("Threshold of Counts per Day", 
                                            min_value=0, 
                                            value=st.session_state.monitor_settings.get('dead_fly_threshold', 100),
                                            key='dead_fly_threshold')

        # Light onset time
        light_onset_time = st.time_input("Enter the light onset time", 
                                       value=st.session_state.monitor_settings.get('light_onset_time', time(6, 0)),
                                       key='light_onset_time')

        # Save DAM settings to session state
        st.session_state.monitor_settings['dam_settings'] = {
            'dam_frequency': dam_frequency,
            'dead_fly_threshold': dead_fly_threshold,
            'light_onset_time': light_onset_time.strftime('%H:%M') if isinstance(light_onset_time, time) else light_onset_time
        }


    
    if st.button("Start Analysis"):
        # Save all settings to session state
        st.session_state.monitor_settings.update({
            'num_conditions': num_conditions,
            'conditions': conditions,
            'ld_dd_analysis': LD_DD_Analysis,
            'dam_frequency': dam_frequency,
            'dead_fly_threshold': dead_fly_threshold,
            'light_onset_time': light_onset_time.strftime('%H:%M') if isinstance(light_onset_time, time) else light_onset_time
        })

        st.session_state.analysis_ran = True
        df = pd.read_csv(st.session_state.uploaded_files[0], sep='\t', header=None)
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

if 'analysis_ran' not in st.session_state:
    st.session_state.analysis_ran = False

if st.session_state.get("analysis_ran"):
    Daily_locomotor_activity = st.session_state.daily_locomotor_activity
    locomotor_activity_by_day = st.session_state.locomotor_activity_by_day
    df_by_LD_DD = st.session_state.df_by_LD_DD.sort_values(by='Light_status', key=lambda x: x.map({'LD': 0, 'DD': 1}))
    
    fig_summary = st.session_state.fig_summary
    fig_by_day = st.session_state.fig_by_day
    fig_by_LD_DD = st.session_state.fig_by_LD_DD

    tab1, tab2, tab3 = st.tabs([
        "Locomotor activity in LD",
        "Locomotor activity by day",
        "Daytime vs Nighttime activity in LD"
    ])

    with tab1:
        st.header("Locomotor activity in LD")
        st.write(Daily_locomotor_activity)
        st.pyplot(fig_summary)

        csv = Daily_locomotor_activity.to_csv(index=False)
        st.download_button(
            label="Download Daily Locomotor Activity as CSV",
            data=csv,
            file_name='Daily_Locomotor_Activity.csv',
            mime='text/csv',
            key='download_daily_locomotor_activity'
        )

    with tab2:
        st.header("Locomotor activity by day")

        # Drop any non-dates
        locomotor_activity_by_day = locomotor_activity_by_day[locomotor_activity_by_day['Date'] != 'Mean']
        locomotor_activity_by_day['Date'] = pd.to_datetime(locomotor_activity_by_day['Date'])

        st.write(locomotor_activity_by_day)
        st.pyplot(fig_by_day)

        csv = locomotor_activity_by_day.to_csv(index=False)
        st.download_button(
            label="Download Locomotor Activity by Day as CSV",
            data=csv,
            file_name='Locomotor_Activity_by_Day.csv',
            mime='text/csv',
            key='download_locomotor_activity_by_day'
        )

    with tab3:
        st.header("Daytime vs Nighttime activity in LD")
        st.write(df_by_LD_DD)
        st.pyplot(fig_by_LD_DD)

        csv = df_by_LD_DD.to_csv(index=False)
        st.download_button(
            label="Download Daytime vs Nighttime Activity in LD as CSV",
            data=csv,
            file_name='Daytime_vs_Nighttime_Activity_in_LD.csv',
            mime='text/csv',
            key='download_daytime_vs_nighttime_activity_in_LD'
        )