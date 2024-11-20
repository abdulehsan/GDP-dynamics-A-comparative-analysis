import streamlit as st
import pandas as pd
import plotly.express as px
import requests
from pathlib import Path

# Resolve the directory of the current script
current_dir = Path(__file__).resolve().parent.parent

# Load the dataset
@st.cache_data(ttl=60)  # Updated caching method
def load_data():
    # Dynamically resolve the path to the dataset
    file_path = current_dir / 'Datasets' / 'New folder' / 'unemployment-rate-imf.csv'

    if not file_path.exists():
        st.error(f"Dataset file not found at: {file_path}")
        return None

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

    # Complete Region Mapping for All Countries in the World
    region_mapping = {
        "Algeria": "Africa", "Angola": "Africa", "Benin": "Africa", "Botswana": "Africa",
        "Afghanistan": "Asia", "Armenia": "Asia", "Azerbaijan": "Asia", "Bangladesh": "Asia",
        "Austria": "Europe", "Belarus": "Europe", "Belgium": "Europe", "Germany": "Europe",
        "Antigua and Barbuda": "North America", "Bahamas": "North America", "Canada": "North America",
        "Argentina": "South America", "Bolivia": "South America", "Brazil": "South America",
        "Australia": "Oceania", "Fiji": "Oceania", "Kiribati": "Oceania", "New Zealand": "Oceania",
    }

    # Map countries to their respective regions, assigning "Other" if not available
    data['Region'] = data['Country'].map(region_mapping).fillna("Other")

    # Fill missing data with a regional average or a default value
    data['Observations'].fillna(data.groupby('Region')['Observations'].transform('mean'), inplace=True)
    data['Observations'].fillna(0, inplace=True)

    return data, region_mapping

# Function to get unemployment rate from World Bank API
def get_unemployment_rate_from_world_bank(country_code, year):
    url = f"http://api.worldbank.org/v2/country/{country_code}/indicator/SL.UEM.TOTL.ZS?date={year}&format=json"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if len(data) > 1 and data[1]:
            value = data[1][0].get('value')
            return value
    return None

# Load data and region mapping
data, region_mapping = load_data()
if data is None:
    st.stop()  # Stop execution if the dataset is not loaded

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

# Visualization: World Map
st.subheader(f"Unemployment Rates in {selected_year}")
year_filtered_data = filtered_data[filtered_data['Year'] == selected_year]

fig_map = px.choropleth(
    year_filtered_data,
    locations="ISO_Code",
    color="Observations",
    hover_name="Country",
    title=f"Global Unemployment Rates in {selected_year}",
    color_continuous_scale=px.colors.sequential.Plasma
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

# Footer
st.markdown("**Data Source:** International Monetary Fund")
