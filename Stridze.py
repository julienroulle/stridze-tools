import streamlit as st

st.set_page_config(
    page_title="Hello",
    page_icon="👋",
)

system = st.sidebar.radio("Unit System", ('Metric', 'Imperial'), index=0)
if system is not None:
    st.session_state['system'] = system

st.write("# Welcome to Stridze Tools!")\

st.markdown(
    """
    Stridze Tools is an open-source app built specifically for Runners.

    **👈 Select a tool from the sidebar** to see some examples of what Stridze can do!
"""
)