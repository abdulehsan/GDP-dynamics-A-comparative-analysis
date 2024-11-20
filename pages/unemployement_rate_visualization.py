import streamlit as st
import pandas as pd
import plotly.express as px
import requests
from pathlib import Path

# Load the dataset
@st.cache_data(ttl=60)  # Updated caching method
def load_data():

    # Dynamically resolve the dataset path relative to this script
    #file_path = Path(__file__).parent / 'Datasets' / 'New folder' / 'unemployment-rate-imf.csv'
    file_path = Path(__file__).parent.parent / 'Datasets' / 'New_folder' / 'unemployment-rate-imf.csv'


    # Check if the file exists
    if not file_path.exists():
        st.error(f"Dataset file not found at: {file_path}")
        st.stop()  # Stop execution if the file is not found

<<<<<<< HEAD
    # Load the data
=======
    # Load the dataset
>>>>>>> unemployment
    data = pd.read_csv(file_path)
    data.rename(columns={
        'Entity': 'Country',
        'Code': 'ISO_Code',
        'Year': 'Year',
        'Unemployment rate - Percent of total labor force - Observations': 'Observations',
        'Unemployment rate - Percent of total labor force - Forecasts': 'Forecasts'
    }, inplace=True)
    data['Year'] = pd.to_numeric(data['Year'], errors='coerce')
    data['Observations'] = pd.to_numeric(data['Observations'], errors='coerce')
    data['Forecasts'] = pd.to_numeric(data['Forecasts'], errors='coerce')

    # Map countries to their respective regions
    region_mapping = {
<<<<<<< HEAD
        "Algeria": "Africa", "Angola": "Africa", "Benin": "Africa", "Botswana": "Africa",
        # (Rest of the region_mapping here...)
        "United States": "North America", "Argentina": "South America", "Australia": "Oceania"
    }

    # Map countries to their respective regions
=======
        # Add your complete region mapping here as in your original code
        "United States": "North America", "Argentina": "South America", "Australia": "Oceania",
    }
>>>>>>> unemployment
    data['Region'] = data['Country'].map(region_mapping).fillna("Other")

    # Fill missing data with regional averages
    data['Observations'].fillna(data.groupby('Region')['Observations'].transform('mean'), inplace=True)
<<<<<<< HEAD
    data['Observations'].fillna(0, inplace=True)
=======
    data['Observations'].fillna(0, inplace=True)  # If no average is available, set to 0
>>>>>>> unemployment

    return data, region_mapping

# Load data and region mapping
data, region_mapping = load_data()

# Streamlit app title
st.title("Global Unemployment Rates Dashboard")
st.markdown("Analyze and visualize unemployment rates with interactive features.")

# Sidebar for filters
st.sidebar.header("Filter Options")
years = sorted(data['Year'].dropna().unique())
selected_year = st.sidebar.slider("Select Year", int(min(years)), int(max(years)), int(max(years)))

# Region Filter
regions = data['Region'].unique()
selected_region = st.sidebar.selectbox("Select Region", options=["All"] + sorted(regions))

# Country Filter
if selected_region == "All":
    available_countries = list(region_mapping.keys())
else:
    available_countries = [country for country, region in region_mapping.items() if region == selected_region]

selected_countries = st.sidebar.multiselect("Select Countries", options=["All"] + available_countries, default="All")

# Filter data
filtered_data = data.copy()
if selected_region != "All":
    filtered_data = filtered_data[filtered_data['Region'] == selected_region]
if "All" not in selected_countries:
    filtered_data = filtered_data[filtered_data['Country'].isin(selected_countries)]

# Visualization: Choropleth Map
st.subheader(f"Unemployment Rates in {selected_year}")
year_filtered_data = filtered_data[filtered_data['Year'] == selected_year]
fig_map = px.choropleth(
    year_filtered_data,
    locations="ISO_Code",
    color="Observations",
    hover_name="Country",
    title=f"Global Unemployment Rates in {selected_year}",
    color_continuous_scale=px.colors.sequential.Plasma,
    labels={"Observations": "Unemployment Rate (%)"}
)
st.plotly_chart(fig_map)

# Visualization: Line Chart for Trends
st.subheader("Unemployment Rate Trends")
fig_line = px.line(
    filtered_data,
    x="Year",
    y="Observations",
    color="Country",
    title="Unemployment Trends by Country",
    labels={"Observations": "Unemployment Rate (%)"}
)
st.plotly_chart(fig_line)

# Visualization: Area Chart
st.subheader("Global Unemployment Rates Over Time")
fig_area = px.area(
    filtered_data,
    x="Year",
    y="Observations",
    color="Country",
    title="Global Unemployment Rate Trends by Country",
    labels={"Observations": "Unemployment Rate (%)", "Year": "Year"}
)
st.plotly_chart(fig_area)

# Visualization: Box Plot
st.subheader("Distribution of Unemployment Rates Over Years")
fig_box = px.box(
    filtered_data.dropna(subset=['Observations']),
    x="Year",
    y="Observations",
    title="Distribution of Unemployment Rates",
    labels={"Year": "Year", "Observations": "Unemployment Rate (%)"}
)
st.plotly_chart(fig_box)

# Visualization: Top 10 Countries with Highest Unemployment Rates
st.subheader(f"Top 10 Countries with Highest Unemployment Rates in {selected_year}")
top_countries = year_filtered_data.nlargest(10, 'Observations')
fig_top10 = px.bar(
    top_countries,
    x='Observations',
    y='Country',
    orientation='h',
    title="Top 10 Countries with Highest Unemployment Rates",
    labels={"Observations": "Unemployment Rate (%)", "Country": "Country"}
)
st.plotly_chart(fig_top10)

# Visualization: Pie Chart
st.subheader(f"Unemployment Rate Distribution by Country in {selected_year}")
fig_pie = px.pie(
    year_filtered_data,
    names='Country',
    values='Observations',
    title=f"Unemployment Rate Distribution Across Countries in {selected_year}",
    hole=0.3
)
st.plotly_chart(fig_pie)

# Footer
st.markdown("**Data Source:** International Monetary Fund")
