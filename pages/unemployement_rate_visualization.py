import streamlit as st
import pandas as pd
import plotly.express as px

from pathlib import Path

# Cache the data loading function for efficiency
@st.cache_data(ttl=60)
def load_data():

    # Dynamically resolve the dataset path relative to this script
    #file_path = Path(__file__).parent / 'Datasets' / 'New folder' / 'unemployment-rate-imf.csv'
    file_path = Path(__file__).parent.parent / 'Datasets' / 'New_folder' / 'unemployment_rate_updated_final_10va.csv'


    # Check if the file exists
    if not file_path.exists():
        st.error(f"Dataset file not found at: {file_path}")
        st.stop()  # Stop execution if the file is not found

    # Load the data
    data = pd.read_csv(file_path)
    data.rename(columns={
        'Entity': 'Country',
        'Code': 'ISO_Code',
        'Year': 'Year',
        'Unemployment rate - Percent of total labor force - Observations': 'Observations',
        'Unemployment rate - Percent of total labor force - Forecasts': 'Forecasts'
    }, inplace=True)

    # Convert columns to numeric
    data['Year'] = pd.to_numeric(data['Year'], errors='coerce')
    data['Observations'] = pd.to_numeric(data['Observations'], errors='coerce')
    data['Forecasts'] = pd.to_numeric(data['Forecasts'], errors='coerce')

    # Fill missing observations with country averages or set to 0
    data['Observations'] = data.groupby('Country')['Observations'].transform(
        lambda x: x.fillna(x.mean())
    ).fillna(0)

    # Add region mapping
    region_mapping = {
        "Algeria": "Africa", "India": "Asia", "United States": "North America",  # Sample regions, add as needed
        # Add complete region mapping here
    }
    data['Region'] = data['Country'].map(region_mapping).fillna("Other")
    return data

# Load the data
data = load_data()

# Streamlit app setup
st.title("Global Unemployment Rates Dashboard")
st.markdown("Explore unemployment rates globally with interactive visualizations.")

# Sidebar filters
st.sidebar.header("Filter Options")
years = sorted(data['Year'].dropna().unique())
selected_year = st.sidebar.slider("Select Year", int(min(years)), int(max(years)), int(max(years)))

regions = sorted(data['Region'].unique())
selected_region = st.sidebar.selectbox("Select Region", options=["All"] + regions)

available_countries = data['Country'].unique()
selected_countries = st.sidebar.multiselect(
    "Select Countries", options=["All"] + sorted(available_countries), default="All"
)

# Sidebar country search
country_search = st.sidebar.selectbox("Search Country", options=[""] + sorted(available_countries))

# If a country is selected in the search box, show a dedicated page for that country
if country_search:
    st.subheader(f"Unemployment Data for {country_search}")

    # Filter data for the selected country
    country_data = data[data['Country'] == country_search]

    if country_data.empty:
        st.warning("No data available for the selected country.")
    else:
        # Line chart: Unemployment trends for the searched country
        st.subheader(f"Unemployment Trends for {country_search}")
        fig_line_country = px.line(
            country_data,
            x="Year",
            y="Observations",
            title=f"Unemployment Rate Trends in {country_search}",
            labels={"Observations": "Unemployment Rate (%)", "Year": "Year"}
        )
        st.plotly_chart(fig_line_country)

        # Area chart: Showing the changes in unemployment rates over time for the searched country
        st.subheader(f"Area Chart of Unemployment Rates in {country_search}")
        fig_area_country = px.area(
            country_data,
            x="Year",
            y="Observations",
            title=f"Unemployment Rate Over Time in {country_search}",
            labels={"Year": "Year", "Observations": "Unemployment Rate (%)"},
            color_discrete_sequence=["#FF6347"]
        )
        st.plotly_chart(fig_area_country)

        # Pie chart: Unemployment rate distribution for the searched country (static since it's a single country)
        st.subheader(f"Unemployment Distribution in {country_search}")
        fig_pie_country = px.pie(
            country_data,
            names='Year',
            values='Observations',
            title=f"Unemployment Distribution Over Time in {country_search}",
            hole=0.3
        )
        st.plotly_chart(fig_pie_country)

else:
    # General visualizations when no specific country is selected
    st.subheader(f"Unemployment Rates in {selected_year}")
    year_filtered_data = data[data['Year'] == selected_year]

    # Interactive choropleth map
    fig_map = px.choropleth(
        year_filtered_data,
        locations="ISO_Code",
        color="Observations",
        hover_name="Country",
        title=f"Unemployment Rates ({selected_year})",
        labels={"Observations": "Unemployment Rate (%)"},
        color_continuous_scale="Plasma"
    )
    st.plotly_chart(fig_map, use_container_width=True)

    # Line chart for unemployment trends
    st.subheader("Unemployment Trends Over Time")
    fig_line = px.line(
        data,
        x="Year",
        y="Observations",
        color="Country",
        title="Unemployment Trends by Country",
        labels={"Observations": "Unemployment Rate (%)", "Year": "Year"}
    )
    st.plotly_chart(fig_line)

    # Area chart for global trends
    st.subheader("Global Trends by Country")
    fig_area = px.area(
        data,
        x="Year",
        y="Observations",
        color="Country",
        title="Global Unemployment Trends",
        labels={"Observations": "Unemployment Rate (%)", "Year": "Year"}
    )
    st.plotly_chart(fig_area)

# Footer
st.markdown("**Data Source:** International Monetary Fund")
