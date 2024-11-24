import streamlit as st

# Title
st.title("Interactive GDP Analysis Dashboard")
st.sidebar.title("Navigation")

# Sidebar Navigation
page = st.sidebar.selectbox("Select a page", ["Home", "GDP per Capita", "Visualization", "Reports"])

# Page: Home
if page == "Home":
    st.write("Welcome to the GDP Analysis Dashboard!")

# Page: GDP per Capita
elif page == "GDP per Capita":
    st.subheader("GDP per Capita Analysis")
    # Import the GDP analysis module from the pages folder
    from pages.GDP_Per_Capita import show_gdp_per_capita_analysis
    show_gdp_per_capita_analysis()

# Page: Visualization (placeholder)
elif page == "Visualization":
    st.write("Navigate to Visualizations")

# Page: Reports (placeholder)
elif page == "Reports":
    st.write("Navigate to Reports")
