import streamlit as st
import pandas as pd
import plotly.express as px
import requests
from pathlib import Path

# Load the dataset
@st.cache_data(ttl=60)  # Updated caching method
def load_data():
    # Resolve the file path dynamically
    file_path = Path(__file__).parent / 'Datasets' / 'New folder' / 'unemployment-rate-imf.csv'

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
    data['Year'] = pd.to_numeric(data['Year'], errors='coerce')
    data['Observations'] = pd.to_numeric(data['Observations'], errors='coerce')
    data['Forecasts'] = pd.to_numeric(data['Forecasts'], errors='coerce')

    # Complete Region Mapping for All Countries in the World
    region_mapping = {
        "Algeria": "Africa", "Angola": "Africa", "Benin": "Africa", "Botswana": "Africa",
        # (Rest of the region_mapping here...)
        "United States": "North America", "Argentina": "South America", "Australia": "Oceania"
    }

    # Map countries to their respective regions
    data['Region'] = data['Country'].map(region_mapping).fillna("Other")

    # Fill missing data with regional averages
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

# Streamlit app title
st.title("Global Unemployment Rates Dashboard")
st.markdown("Analyze and visualize unemployment rates with interactive features.")

# Sidebar for filters
st.sidebar.header("Filter Options")
years = sorted(data['Year'].dropna().unique())
selected_year = st.sidebar.slider("Select Year", int(min(years)), int(max(years)), int(max(years)))

# Region Filter
regions = data['Region'].unique()
selected_region = st.sidebar.selectbox("Select Region", options=["All"] + sorted([region for region in regions if region != "Other"]))

# Get all countries in the selected region from the region_mapping
if selected_region == "All":
    available_countries = list(region_mapping.keys())
else:
    available_countries = [country for country, region in region_mapping.items() if region == selected_region]

# Country Filter
selected_countries = st.sidebar.multiselect("Select Countries or Regions", options=["All"] + available_countries, default="All")

# Filter data by region and countries
filtered_data = data.copy()
if selected_region != "All":
    filtered_data = filtered_data[filtered_data['Region'] == selected_region]

if "All" not in selected_countries:
    filtered_data = filtered_data[filtered_data['Country'].isin(selected_countries)]

# Ensure all countries from the selected region are included in visualizations, even if data is missing
if selected_region != "All":
    missing_countries = [country for country in available_countries if country not in filtered_data['Country'].values]
    for country in missing_countries:
        filtered_data = pd.concat([filtered_data, pd.DataFrame([{'Country': country, 'Year': selected_year, 'Observations': 0, 'Region': selected_region}])])

# Country Search Box for quick lookup
st.sidebar.header("Country Search")
country_search = st.sidebar.selectbox("Select a Country", options=[""] + sorted(available_countries))

# Display missing countries for selected region
if selected_region != "All":
    st.sidebar.subheader("Countries with No Data Available")
    if missing_countries:
        st.sidebar.markdown(", ".join(missing_countries))
    else:
        st.sidebar.markdown("All countries in the selected region have data available.")

    # Visualization of countries with no data available
    st.subheader("Visualization of Countries with No Data Available")
    if missing_countries:
        missing_countries_df = pd.DataFrame(missing_countries, columns=['Country'])
        fig_missing_countries = px.bar(
            missing_countries_df,
            x='Country',
            title=f"Countries with No Data Available in {selected_region}",
            labels={'Country': 'Country'}
        )
        st.plotly_chart(fig_missing_countries)

# If a country is searched, display data for that country only
if country_search:
    st.subheader(f"Unemployment Data for {country_search}")
    country_data = filtered_data[filtered_data['Country'] == country_search]

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

        # Area Chart: Showing the changes in unemployment rates over time for the searched country
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

else:
    # Filter data for the selected year
    year_filtered_data = filtered_data[filtered_data['Year'] == selected_year]

    # Interactive World Map
    st.subheader(f"Unemployment Rates in {selected_year}")
    fig_map = px.choropleth(
        year_filtered_data,
        locations="ISO_Code",
        color="Observations",
        hover_name="Country",
        hover_data={"Observations": True, "Year": False},
        title=f"Global Unemployment Rates ({selected_year})",
        labels={"Observations": "Unemployment Rate (%)"},
        color_continuous_scale=px.colors.sequential.Plasma,
        height=600
    )

    # Set missing values to be represented as gray for better visual distinction
    fig_map.update_traces(marker_line_color='gray')

    st.plotly_chart(fig_map, use_container_width=True)

    # Add legend description
    st.markdown("""
    **Legend Description**:  
    The choropleth map above uses color intensity to represent the unemployment rate for each country in the selected year.  
    - **Dark colors** represent higher unemployment rates.  
    - **Light colors** represent lower unemployment rates.  
    - **Gray areas** represent countries for which no data is available.  
    """)

    # Line chart: Unemployment trend for selected countries
    if selected_countries and "All" not in selected_countries:
        st.subheader("Unemployment Trends Over Time")
        trend_data = data[data['Country'].isin(available_countries)]
        fig_line = px.line(
            trend_data,
            x="Year",
            y="Observations",
            color="Country",
            title="Unemployment Rate Trends by Country",
            labels={"Observations": "Unemployment Rate (%)", "Year": "Year"}
        )
        st.plotly_chart(fig_line)

    # Area Chart: Global unemployment rates over time responding to regions
    st.subheader("Global Unemployment Rates Over Time")
    region_filtered_data = filtered_data.dropna(subset=['Observations'])
    fig_area = px.area(
        region_filtered_data,
        x="Year",
        y="Observations",
        color="Country",
        title="Global Unemployment Rate Trends by Country",
        labels={"Observations": "Unemployment Rate (%)", "Year": "Year"}
    )
    st.plotly_chart(fig_area)

    # Box plot: Distribution of unemployment rates over years
    st.subheader("Distribution of Unemployment Rates Over Years")
    fig_box = px.box(
        filtered_data.dropna(subset=['Observations']),
        x="Year",
        y="Observations",
        title="Distribution of Unemployment Rates",
        labels={"Year": "Year", "Observations": "Unemployment Rate (%)"}
    )
    st.plotly_chart(fig_box)

    # Horizontal bar chart: Top 10 countries with the highest unemployment rates for the selected year
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

    # Pie Chart: Unemployment rate distribution across countries for the selected year
    st.subheader(f"Unemployment Rate Distribution by Country in {selected_year}")
    if not year_filtered_data.empty:
        fig_pie = px.pie(
            year_filtered_data,
            names='Country',
            values='Observations',
            title=f"Unemployment Rate Distribution Across Countries in {selected_year}",
            hole=0.3
        )
        st.plotly_chart(fig_pie)
    else:
        st.warning(f"No data available for the selected year {selected_year}.")

    # Missing Data Analysis for the entire dataset
    st.subheader("Missing Data Analysis for Entire Dataset")
    missing_data = data[['Observations', 'Forecasts']].isnull().mean() * 100
    fig_missing = px.bar(
        missing_data,
        x=missing_data.index,
        y=missing_data.values,
        title="Percentage of Missing Data",
        labels={"x": "Data Type", "y": "Percentage Missing"}
    )
    st.plotly_chart(fig_missing)

    # Missing Data Analysis by Region
    st.subheader("Missing Data Analysis by Region")
    missing_data_by_region = data.groupby('Region')[['Observations', 'Forecasts']].apply(lambda x: x.isnull().mean() * 100).reset_index()
    fig_missing_region = px.bar(
        missing_data_by_region.melt(id_vars="Region", var_name="Data Type", value_name="Percentage Missing"),
        x="Region",
        y="Percentage Missing",
        color="Data Type",
        barmode="group",
        title="Percentage of Missing Data by Region",
        labels={"Percentage Missing": "Percentage Missing (%)", "Region": "Region", "Data Type": "Data Type"}
    )
    st.plotly_chart(fig_missing_region)

# Footer
st.markdown("**Data Source:** International Monetary Fund")
