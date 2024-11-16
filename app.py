import streamlit as st

st.title("Interactive GDP Analysis Dashboard")
st.sidebar.title("Navigation")
page = st.sidebar.selectbox("Select a page", ["Home", "Visualization", "Reports"])

if page == "Home":
    st.write("Welcome to the GDP Analysis Dashboard!")
elif page == "Visualization":
    st.write("Navigate to Visualizations")
    # import pages.visualization
elif page == "Reports":
    st.write("Navigate to Reports")
    # import reports.report
