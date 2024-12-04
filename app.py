import streamlit as st
# Title
st.set_page_config(initial_sidebar_state="collapsed")
st.title("Interactive GDP Analysis Dashboard")
st.subheader("Navigation")
page = st.selectbox("Go to", ["Home", "Visualization", "Reports"])

if page == "Home":
    st.write("Welcome to the GDP Analysis Dashboard!")

elif page == "Visualization":
    st.write("Navigate to Visualization")
    visualization_page = st.selectbox("Select a page", ["GDP", "GDP-Per-Capita","GDP Growth" , "Unemployement"])
    if visualization_page == "GDP Growth":
        import pages.gdp_growth_visualization
    elif visualization_page == "GDP":
        import pages.gdp_visualization
    elif visualization_page == "GDP-Per-Capita":
        import pages.GDP_Per_Capita
    elif visualization_page == "Unemployement":
        import pages.unemployement_rate_visualization

elif page == "Reports":
    st.write("Navigate to Reports")
elif page =="Unemployement":
    st.write("Navigate to Unemployment")
    import pages.unemployement_rate_visualization
    # import reports.report
