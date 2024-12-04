import streamlit as st

GDP = st.Page(
    "pages/gdp_visualization.py", title="GDP Visualization", icon=":material/insert_chart_outlined:"
)
GDP_Per_Capita = st.Page(
    "pages/GDP_Per_Capita.py", title="GDP Per Capita", icon=":material/insert_chart_outlined:"
)
GDP_Growth = st.Page(
    "pages/gdp_growth_visualization.py", title="GDP Growth", icon=":material/insert_chart_outlined:"
)
Unemployment = st.Page(
    "pages/unemployement_rate_visualization.py", title="Unemployment Rate", icon=":material/insert_chart_outlined:"
)
pg = st.navigation(
    {
        "Visualization":[GDP,GDP_Per_Capita,GDP_Growth,Unemployment],
    }
)
pg.run()
