import streamlit as st

st.title('Sleep Analysis')
st.write('This is a Streamlit app that analyzes sleep data.')
st.write('Upstream Analysis (coming soon)')

# add hyperlink to sleep bout page
st.page_link("pages/1_Sleep_Bout.py", label="Sleep Bout")

st.page_link("pages/2_Individual_Sleep.py", label="Individual Sleep")

st.page_link("pages/3_Average_Sleep.py", label="Average Sleep")

