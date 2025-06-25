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