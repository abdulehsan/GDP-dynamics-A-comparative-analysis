import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path
from scipy.stats import skew, kurtosis
import numpy as np

# Cache the data loading function for efficiency
@st.cache_data(ttl=60)
def load_cleaned_data():
    # Resolve the path to the cleaned dataset
    file_path = Path(__file__).parent.parent / 'Datasets' / 'New folder' / 'final_cleaned_unemployment_dataset_karlene.csv'

    # Check if the file exists
    if not file_path.exists():
        st.error(f"Dataset file not found at: {file_path}")
        st.stop()

    # Load the cleaned data
    data = pd.read_csv(file_path)

    # Rename columns to match expected names
    data.rename(columns={
        'Entity': 'Country',
        'Code': 'ISO_Code',
        'Year': 'Year',
        'Unemployment rate - Percent of total labor force - Observations': 'Observations'
    }, inplace=True)

    # Comprehensive region mapping with all countries
    region_mapping = {
        # Africa
        "Algeria": "Africa", "Angola": "Africa", "Benin": "Africa", "Botswana": "Africa",
        "Burkina Faso": "Africa", "Burundi": "Africa", "Cameroon": "Africa",
        "Cape Verde": "Africa", "Chad": "Africa", "Congo": "Africa", "Djibouti": "Africa",
        "Egypt": "Africa", "Ethiopia": "Africa", "Gabon": "Africa", "Ghana": "Africa",
        "Kenya": "Africa", "Libya": "Africa", "Madagascar": "Africa", "Malawi": "Africa",
        "Morocco": "Africa", "Mozambique": "Africa", "Nigeria": "Africa", "Rwanda": "Africa",
        "Senegal": "Africa", "South Africa": "Africa", "Sudan": "Africa", "Tanzania": "Africa",
        "Tunisia": "Africa", "Uganda": "Africa", "Zambia": "Africa", "Zimbabwe": "Africa",

        # Asia
        "Afghanistan": "Asia", "Bangladesh": "Asia", "China": "Asia", "India": "Asia",
        "Indonesia": "Asia", "Iran": "Asia", "Iraq": "Asia", "Japan": "Asia",
        "Kazakhstan": "Asia", "Malaysia": "Asia", "Pakistan": "Asia", "Philippines": "Asia",
        "Saudi Arabia": "Asia", "Singapore": "Asia", "South Korea": "Asia",
        "Sri Lanka": "Asia", "Thailand": "Asia", "Turkey": "Asia", "Uzbekistan": "Asia",
        "Vietnam": "Asia", "Yemen": "Asia",

        # Europe
        "Austria": "Europe", "Belgium": "Europe", "Bulgaria": "Europe", "Croatia": "Europe",
        "Czech Republic": "Europe", "Denmark": "Europe", "Estonia": "Europe",
        "Finland": "Europe", "France": "Europe", "Germany": "Europe", "Greece": "Europe",
        "Hungary": "Europe", "Ireland": "Europe", "Italy": "Europe", "Latvia": "Europe",
        "Lithuania": "Europe", "Netherlands": "Europe", "Norway": "Europe", "Poland": "Europe",
        "Portugal": "Europe", "Romania": "Europe", "Russia": "Europe", "Serbia": "Europe",
        "Slovakia": "Europe", "Slovenia": "Europe", "Spain": "Europe", "Sweden": "Europe",
        "Switzerland": "Europe", "Ukraine": "Europe", "United Kingdom": "Europe",

        # North America
        "Canada": "North America", "Mexico": "North America", "United States": "North America",

        # South America
        "Argentina": "South America", "Brazil": "South America", "Chile": "South America",
        "Colombia": "South America", "Ecuador": "South America", "Paraguay": "South America",
        "Peru": "South America", "Uruguay": "South America", "Venezuela": "South America",

        # Oceania
        "Australia": "Oceania", "New Zealand": "Oceania",

        # Other/Unknown
        "Other": "Other"
    }

    # Assign regions to each country
    data['Region'] = data['Country'].map(region_mapping).fillna("Other")
    return data

# Load the cleaned dataset
data = load_cleaned_data()

# Streamlit app setup
st.title("Global Unemployment Rates Dashboard")
st.markdown("Explore unemployment rates globally with interactive visualizations.")

# Sidebar filters
st.sidebar.header("Filter Options")
years = sorted(data['Year'].unique())
selected_year = st.sidebar.slider("Select Year", int(min(years)), int(max(years)), int(max(years)))

regions = sorted(data['Region'].unique())
selected_region = st.sidebar.selectbox("Select Region", options=["All"] + regions)

# Filter data by region first
if selected_region != "All":
    filtered_data = data[data['Region'] == selected_region]
else:
    filtered_data = data

# Dynamically update available countries based on the selected region
available_countries = sorted(filtered_data['Country'].unique())
selected_countries = st.sidebar.multiselect(
    "Select Countries", options=available_countries, default=[]
)

# Dynamically update search options for countries
country_search = st.sidebar.selectbox("Search Country", options=[""] + available_countries)

# Further filter data based on selected countries
if selected_countries:
    filtered_data = filtered_data[filtered_data['Country'].isin(selected_countries)]

# Further filter data based on selected country from the search box
if country_search:
    filtered_data = filtered_data[filtered_data['Country'] == country_search]

# Filter data for the selected year
year_filtered_data = filtered_data[filtered_data['Year'] == selected_year]

# **INSIGHTS SECTION**
# Check if insights should be based on region or the entire world
if selected_region != "All" and not year_filtered_data.empty:
    st.subheader(f"Insights for {selected_region} in {selected_year}")
else:
    st.subheader(f"Global Insights for {selected_year}")

# Display insights for the selected region or all countries
if selected_region != "All":
    if not year_filtered_data.empty:
        highest_country = year_filtered_data.loc[year_filtered_data['Observations'].idxmax()]
        st.write(f"**Country with the highest unemployment rate globally in {selected_year}:** {highest_country['Country']} ({highest_country['Observations']}%)")

        lowest_country = year_filtered_data.loc[year_filtered_data['Observations'].idxmin()]
        st.write(f"**Country with the lowest unemployment rate globally in {selected_year}:** {lowest_country['Country']} ({lowest_country['Observations']}%)")
    else:
        st.write(f"No data available for the selected year: {selected_year}")

    avg_rate = year_filtered_data['Observations'].mean()
    st.write(f"**Average unemployment rate in {selected_region}:** {avg_rate:.2f}%")

    std_dev = year_filtered_data['Observations'].std()
    st.write(f"**Standard deviation of unemployment rates in {selected_region}:** {std_dev:.2f}%")

    # Calculate skewness and kurtosis for the selected year
    skewness_value = skew(year_filtered_data['Observations'], nan_policy='omit')
    kurt_value = kurtosis(year_filtered_data['Observations'], nan_policy='omit')

    st.write(f"**Skewness (Karl Pearson):** {skewness_value:.2f}")
    st.write(f"**Kurtosis:** {kurt_value:.2f}")

    # **Relevant Graph for Skewness and Kurtosis**
    st.subheader(f"Distribution of Unemployment Rates in {selected_region} ({selected_year})")
    fig_hist = px.histogram(
        year_filtered_data,
        x="Observations",
        nbins=10,
        title=f"Distribution of Unemployment Rates in {selected_region} ({selected_year})",
        labels={"Observations": "Unemployment Rate (%)"},
    )
    st.plotly_chart(fig_hist, use_container_width=True)

else:
    if not year_filtered_data.empty:
        highest_country = year_filtered_data.loc[year_filtered_data['Observations'].idxmax()]
        st.write(f"**Country with the highest unemployment rate globally in {selected_year}:** {highest_country['Country']} ({highest_country['Observations']}%)")

        lowest_country = year_filtered_data.loc[year_filtered_data['Observations'].idxmin()]
        st.write(f"**Country with the lowest unemployment rate globally in {selected_year}:** {lowest_country['Country']} ({lowest_country['Observations']}%)")

    avg_rate = year_filtered_data['Observations'].mean()
    st.write(f"**Global average unemployment rate in {selected_year}:** {avg_rate:.2f}%")

    std_dev = year_filtered_data['Observations'].std()
    st.write(f"**Global standard deviation of unemployment rates in {selected_year}:** {std_dev:.2f}%")

        # Calculate skewness and kurtosis for the selected year
    skewness_value = skew(year_filtered_data['Observations'], nan_policy='omit')
    kurt_value = kurtosis(year_filtered_data['Observations'], nan_policy='omit')

    st.write(f"**Skewness (Karl Pearson):** {skewness_value:.2f}")
    st.write(f"**Kurtosis:** {kurt_value:.2f}")

# **WORLD MAP**

# Choropleth map for selected year
st.subheader(f"Unemployment Rates in {selected_year}")
fig_map = px.choropleth(
    year_filtered_data,
    locations="ISO_Code",
    color="Observations",
    hover_name="Country",
    title=f"Unemployment Rates ({selected_year})",
    labels={"Observations": "Unemployment Rate (%)"},
    hover_data={"Country": True, "Observations": True},
    color_continuous_scale="Viridis"
)
fig_map.update_geos(fitbounds="locations", visible=True)
st.plotly_chart(fig_map, use_container_width=True)

# **TRENDS AND COMPARISONS**
# **TRENDS AND COMPARISONS**

# Check if a single country is searched using the search feature
if country_search and len(selected_countries) == 0:
    st.subheader(f"Insights for {country_search}")
    
    # Filter data for the searched country
    country_data = data[data['Country'] == country_search]
    
    # Display top 5 years with the highest unemployment rates
    top_5_years = country_data.nlargest(5, 'Observations')
    st.write(f"**Top 5 Years with the Highest Unemployment Rates for {country_search}:**")
    st.dataframe(top_5_years[['Year', 'Observations']])

    # Display unemployment trends for the searched country
    st.subheader(f"Unemployment Trends Over Time for {country_search}")
    fig_line_single = px.line(
        country_data,
        x="Year",
        y="Observations",
        title=f"Unemployment Trends for {country_search}",
        labels={"Observations": "Unemployment Rate (%)", "Year": "Year"},
        markers=True
    )
    st.plotly_chart(fig_line_single, use_container_width=True)

else:
    # Proceed with regular multi-country trends and comparisons

    # Top and Bottom Performers in selected year
    st.subheader(f"Top and Bottom 5 Performers in {selected_year}")
    top_5 = year_filtered_data.nlargest(5, 'Observations')
    bottom_5 = year_filtered_data.nsmallest(5, 'Observations')

    col1, col2 = st.columns(2)
    with col1:
        st.write("**Top 5 Countries with Highest Unemployment Rates**")
        st.dataframe(top_5[['Country', 'Observations']])
    with col2:
        st.write("**Bottom 5 Countries with Lowest Unemployment Rates**")
        st.dataframe(bottom_5[['Country', 'Observations']])

    # Unemployment trends over time by country
    st.subheader("Unemployment Trends Over Time")
    fig_line = px.line(
        filtered_data,
        x="Year",
        y="Observations",
        color="Country",
        title="Unemployment Trends by Country",
        labels={"Observations": "Unemployment Rate (%)", "Year": "Year"},
        hover_data={"Year": True, "Observations": True}
    )
    st.plotly_chart(fig_line, use_container_width=True)

    # Global Trends by Country
    st.subheader("Global Trends by Country")
    fig_area = px.area(
        filtered_data,
        x="Year",
        y="Observations",
        color="Country",
        title="Global Unemployment Trends",
        labels={"Observations": "Unemployment Rate (%)", "Year": "Year"},
        hover_data={"Country": True, "Observations": True}
    )
    st.plotly_chart(fig_area, use_container_width=True)

    # Regional Comparison for selected year
    st.subheader(f"Regional Comparison for {selected_year}")
    regional_data = year_filtered_data.groupby('Region')['Observations'].mean().reset_index()
    fig_bar_region = px.bar(
        regional_data,
        x="Region",
        y="Observations",
        title=f"Average Unemployment Rates by Region ({selected_year})",
        labels={"Observations": "Average Unemployment Rate (%)", "Region": "Region"},
        hover_data={"Region": True, "Observations": True},
        color="Region"
    )
    st.plotly_chart(fig_bar_region, use_container_width=True)

    # Unemployment rates by country
    st.subheader(f"Unemployment Rates by Country in {selected_year}")
    fig_bar = px.bar(
        year_filtered_data,
        x="Country",
        y="Observations",
        title=f"Unemployment Rates in {selected_year}",
        labels={"Observations": "Unemployment Rate (%)", "Country": "Country"},
        hover_data={"Country": True, "Observations": True},
        color="Country"
    )
    st.plotly_chart(fig_bar, use_container_width=True)

    # **Skewness and Kurtosis Trends Responsive to Region and Year Range**

    # Year range slider
    year_range = st.slider(
        "Select Year Range",
        min_value=int(data['Year'].min()),
        max_value=int(data['Year'].max()),
        value=(int(data['Year'].min()), int(data['Year'].max()))
    )

    # Filter data by selected region and year range
    region_filtered_data = data[(data['Year'] >= year_range[0]) & (data['Year'] <= year_range[1])]
    if selected_region != "All":
        region_filtered_data = region_filtered_data[region_filtered_data['Region'] == selected_region]

    # Calculate skewness and kurtosis trends for the filtered data
    skewness_karl_trends = region_filtered_data.groupby('Year')['Observations'].apply(
        lambda x: 3 * (x.mean() - x.median()) / x.std() if x.std() else 0
    )
    kurtosis_trends = region_filtered_data.groupby('Year')['Observations'].apply(
        lambda x: kurtosis(x)
    )

    # Create a DataFrame to store skewness and kurtosis trends
    trends_df = pd.DataFrame({
        'Year': skewness_karl_trends.index,
        'Skewness (Karl Pearson)': skewness_karl_trends.values,
        'Kurtosis': kurtosis_trends.values
    })

    # Plot the skewness and kurtosis trends
    st.subheader(f"Skewness and Kurtosis Trends ({selected_region if selected_region != 'All' else 'Global'})")
    fig_skew_kurt = px.line(
        trends_df,
        x='Year',
        y=['Skewness (Karl Pearson)', 'Kurtosis'],
        title=f"Skewness and Kurtosis Trends ({selected_region if selected_region != 'All' else 'Global'})",
        labels={"Year": "Year", "value": "Metric Value", "variable": "Statistic"},
        markers=True
    )
    st.plotly_chart(fig_skew_kurt, use_container_width=True)
