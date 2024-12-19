import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from pathlib import Path

# File path for your dataset
file_path = Path(__file__).parent.parent / 'Datasets' / 'New folder' / 'Cleaned_GDP_Per_Capita.csv'

# Load the dataset
@st.cache_data(ttl=60)  # Updated caching method
def load_data():
    try:
        # Check if the file exists at the specified path
        if not file_path.exists():
            raise FileNotFoundError(f"Dataset file not found at: {file_path}")
        raw_data = pd.read_csv(file_path)
        return raw_data
    except Exception as e:
        st.error(f"Error loading data: {e}")
        st.stop()

# Data cleaning and processing
@st.cache_data(ttl=60)  # Updated caching method
def clean_data():
    raw_data = load_data()

    # Strip leading/trailing spaces from column names
    raw_data.columns = raw_data.columns.str.strip()

    # Step 1: Remove columns with all missing values
    cleaned_data = raw_data.dropna(axis=1, how='all')

    # Step 2: Retain only relevant columns (Country Name, Country Code, Indicator Name, Indicator Code, and years 1990-2023)
    columns_to_keep = ['Country Name', 'Country Code', 'Indicator Name', 'Indicator Code'] + \
                      [str(year) for year in range(1990, 2024)]
    cleaned_data = cleaned_data[columns_to_keep]

    # Step 3: Strip whitespace from column names and text fields
    cleaned_data.columns = cleaned_data.columns.str.strip()
    for col in ['Country Name', 'Country Code', 'Indicator Name', 'Indicator Code']:
        cleaned_data[col] = cleaned_data[col].str.strip()

    # Step 4: Interpolate missing values for year columns using linear interpolation
    cleaned_data[cleaned_data.columns[4:]] = cleaned_data[cleaned_data.columns[4:]].interpolate(axis=1, method='linear')

    # Step 5: Fill any remaining gaps in numeric fields with 0
    cleaned_data[cleaned_data.columns[4:]] = cleaned_data[cleaned_data.columns[4:]].fillna(0)

    # Step 6: Rename columns for easier use in analysis
    cleaned_data = cleaned_data.rename(columns={'Country Name': 'Country', 'Country Code': 'ISO_Code'})

    # Step 7: Drop rows where essential columns like 'Country' or 'ISO_Code' are missing
    cleaned_data = cleaned_data.dropna(subset=['Country', 'ISO_Code'])

    return cleaned_data

# Load the cleaned data
cleaned_data = clean_data()

# Sidebar Widgets (Year & Country Filters)
if 'selected_year' not in st.session_state:
    st.session_state.selected_year = 2023
if 'selected_countries' not in st.session_state:
    st.session_state.selected_countries = ["All"]

years = [str(year) for year in range(1990, 2024)]
st.session_state.selected_year = st.sidebar.slider("Select Year", 1990, 2023, st.session_state.selected_year)
available_countries = sorted(cleaned_data['Country'].dropna().unique())
st.session_state.selected_countries = st.sidebar.multiselect("Select Countries", options=["All"] + available_countries, default=st.session_state.selected_countries)

# Filter data based on selected countries
filtered_data = cleaned_data.copy()
if "All" not in st.session_state.selected_countries:
    filtered_data = filtered_data[filtered_data['Country'].isin(st.session_state.selected_countries)]

# Convert selected year to string for column access
selected_year_str = str(st.session_state.selected_year)

# Ensure that the selected year exists in the dataset columns
if selected_year_str not in cleaned_data.columns:
    st.error(f"Data for the year {st.session_state.selected_year} is not available in the dataset.")
    st.stop()

# Calculate World Median for the selected year
world_median_gdp = cleaned_data[selected_year_str].median()

# Sidebar Buttons
show_gdp_info = st.sidebar.button("GDP per Capita")
graphical_analysis_button = st.sidebar.button("Graphical Analysis")
statistical_analysis_button = st.sidebar.button("Statistical Analysis")
measures_of_tendency_button = st.sidebar.button("Measures of Tendency")

# Statistical Analysis: Measures of Central Tendency & Dispersion
if statistical_analysis_button:
    st.title(f"Statistical Analysis of GDP per Capita for year {st.session_state.selected_year}")
    
    # Extract the relevant data for the selected year
    selected_year_data = cleaned_data[selected_year_str].dropna()

    # Measures of Central Tendency
    mean_value = selected_year_data.mean()
    median_value = selected_year_data.median()
    mode_value = selected_year_data.mode()[0]  # Taking the first mode value

    # Measures of Dispersion
    range_value = selected_year_data.max() - selected_year_data.min()
    variance_value = selected_year_data.var()
    std_deviation_value = selected_year_data.std()
    iqr_value = selected_year_data.quantile(0.75) - selected_year_data.quantile(0.25)

    st.subheader("Measures of Central Tendency")
    st.write(f"**Mean**: {mean_value:,.2f}")
    st.write(f"**Median**: {median_value:,.2f}")
    st.write(f"**Mode**: {mode_value:,.2f}")

    st.subheader("Measures of Dispersion")
    st.write(f"**Range**: {range_value:,.2f}")
    st.write(f"**Variance**: {variance_value:,.2f}")
    st.write(f"**Standard Deviation**: {std_deviation_value:,.2f}")
    st.write(f"**Interquartile Range (IQR)**: {iqr_value:,.2f}")
    st.title("Time Series Statistical Analysis of GDP per Capita")

    # Time series analysis for three periods
    periods = [(1990, 2000), (2001, 2010), (2011, 2023)]
    
    for period_start, period_end in periods:
        # Extract the relevant data for the period (years in the given range)
        period_years = [str(year) for year in range(period_start, period_end + 1)]
        period_data = cleaned_data[period_years].dropna(axis=1, how='all')  # Drop any columns that are fully NaN
        
        # Perform the statistical analysis for this period
        st.subheader(f"Time Series Analysis of GDP per Capita for Years {period_start} to {period_end}")

        # Measures of Central Tendency (Mean, Median, Mode)
        mean_value = period_data.mean().mean()  # Mean across all countries and years
        median_value = period_data.median().median()  # Median across all countries and years
        mode_value = period_data.mode().iloc[0].mean()  # Taking the first mode across all countries and years

        # Measures of Dispersion (Range, Variance, Standard Deviation, IQR)
        range_value = period_data.max().max() - period_data.min().min()  # Range across all countries and years
        variance_value = period_data.var().mean()  # Variance across all countries and years
        std_deviation_value = period_data.std().mean()  # Standard deviation across all countries and years
        iqr_value = period_data.quantile(0.75).mean() - period_data.quantile(0.25).mean()  # IQR across all countries and years

        # Display Measures of Central Tendency
        st.write(f"**Mean GDP per Capita**: {mean_value:,.2f}")
        st.write(f"**Median GDP per Capita**: {median_value:,.2f}")
        st.write(f"**Mode GDP per Capita**: {mode_value:,.2f}")

        # Display Measures of Dispersion
        st.write(f"**Range of GDP per Capita**: {range_value:,.2f}")
        st.write(f"**Variance of GDP per Capita**: {variance_value:,.2f}")
        st.write(f"**Standard Deviation of GDP per Capita**: {std_deviation_value:,.2f}")
        st.write(f"**Interquartile Range (IQR) of GDP per Capita**: {iqr_value:,.2f}")

        # Add space between periods for readability
        st.markdown("---")

# Measures of Tendency (Skewness & Kurtosis)
# Measures of Tendency (Skewness & Kurtosis) with Line Graph
# Measures of Tendency (Skewness & Kurtosis) with Line Graph
# Measures of Tendency (Skewness & Kurtosis) with Line Graph
if graphical_analysis_button:
    st.title("Graphical Analysis of GDP per Capita")
    
    # Extract the relevant data based on whether "All" or specific countries are selected
    if "All" in st.session_state.selected_countries:
        year_data = cleaned_data[['Country', str(st.session_state.selected_year)]].dropna()
        # Show the full dataset if 'All' is selected
        st.write("### Showing Data for All Countries")
        
        # **Line Chart for All Countries**
        st.subheader(f"GDP per Capita Trends Over Time for All Countries")
        all_countries_data = cleaned_data[['Country'] + [str(year) for year in range(1990, 2024)]]
        all_countries_data = all_countries_data.melt(id_vars=["Country"], 
                                                     value_vars=[str(year) for year in range(1990, 2024)], 
                                                     var_name="Year", 
                                                     value_name="GDP per Capita")
        
        fig_line_all = px.line(all_countries_data, x="Year", y="GDP per Capita", color="Country",
                               title=f"GDP per Capita Trends Over Time for All Countries ({st.session_state.selected_year})",
                               labels={"GDP per Capita": "GDP per Capita (USD)", "Year": "Year"})
        st.plotly_chart(fig_line_all)

    else:
        year_data = cleaned_data[cleaned_data['Country'].isin(st.session_state.selected_countries)]
        year_data = year_data[['Country', str(st.session_state.selected_year)]].dropna()
        st.write(f"### Showing Data for Selected Countries: {', '.join(st.session_state.selected_countries)}")

    # Histogram of GDP per Capita for the selected year
    st.subheader(f"Histogram of GDP per Capita for {st.session_state.selected_year}")
    fig_hist = px.histogram(year_data, x=str(st.session_state.selected_year), nbins=20, title=f"GDP per Capita Distribution ({st.session_state.selected_year})")
    st.plotly_chart(fig_hist)

    # Line Chart for GDP per Capita Trends Over Time (for selected countries)
    # st.subheader(f"GDP per Capita Trends Over Time for Selected Countries")
    selected_countries_data = cleaned_data[cleaned_data['Country'].isin(st.session_state.selected_countries)]

    # Reshaping the data for line chart
    line_chart_data = selected_countries_data.melt(id_vars=["Country"], 
                                                   value_vars=[str(year) for year in range(1990, 2024)], 
                                                   var_name="Year", 
                                                   value_name="GDP per Capita")

    # Filter data for the selected countries and the year range
    # line_chart_data = line_chart_data[line_chart_data['Country'].isin(st.session_state.selected_countries)]

    # Plotting the Line Chart (for selected countries)
    # fig_line = px.line(line_chart_data, x="Year", y="GDP per Capita", color="Country",
                    #    title=f"GDP per Capita Trends Over Time for Selected Countries",
                    #    labels={"GDP per Capita": "GDP per Capita (USD)", "Year": "Year"})
    # st.plotly_chart(fig_line)

    # **Bar Graph**: Top 10 Countries by GDP per Capita (only if "All" countries are selected)
    if "All" in st.session_state.selected_countries:
        top_10_gdp = year_data.sort_values(by=str(st.session_state.selected_year), ascending=False).head(10)
        st.subheader(f"Top 10 Countries by GDP per Capita in {st.session_state.selected_year}")
        fig_bar = px.bar(top_10_gdp, x='Country', y=str(st.session_state.selected_year), title=f"Top 10 Countries by GDP per Capita ({st.session_state.selected_year})")
        st.plotly_chart(fig_bar)

    # Pie Chart: GDP Distribution among Countries
    st.subheader(f"Pie Chart of GDP Distribution in {st.session_state.selected_year}")
    fig_pie = px.pie(year_data, names='Country', values=str(st.session_state.selected_year), title=f"GDP Distribution by Country in {st.session_state.selected_year}")
    st.plotly_chart(fig_pie)

    # Box Plot: GDP per Capita Distribution
    st.subheader(f"Box Plot of GDP per Capita for {st.session_state.selected_year}")
    fig_box = px.box(year_data, y=str(st.session_state.selected_year), title=f"Box Plot of GDP per Capita ({st.session_state.selected_year})")
    st.plotly_chart(fig_box)

    # Scatter Plot: Country vs GDP per Capita
    st.subheader(f"Scatter Plot of Country vs GDP per Capita in {st.session_state.selected_year}")
    fig_scatter = px.scatter(year_data, x='Country', y=str(st.session_state.selected_year), title=f"Country vs GDP per Capita ({st.session_state.selected_year})")
    st.plotly_chart(fig_scatter)

    # Display the GDP per Capita insights and analysis for the selected year
    st.subheader(f"GDP per Capita Insights for {st.session_state.selected_year}")
    year_filtered_data = (
        year_data.rename(columns={str(st.session_state.selected_year): 'GDP per Capita'})
        .dropna(subset=['GDP per Capita'])
    )

    # Display the average GDP per Capita
    average_gdp = year_filtered_data['GDP per Capita'].mean()
    st.write(f"### Average GDP per Capita in {st.session_state.selected_year}: ${average_gdp:,.2f}")

    # Display world median GDP per Capita (only for specific countries)
    if "All" not in st.session_state.selected_countries:
        world_median_gdp = cleaned_data[str(st.session_state.selected_year)].median()
        st.write(f"### World Median GDP per Capita for {st.session_state.selected_year}: ${world_median_gdp:,.2f}")

        # Visualize comparison between selected countries and world median
        comparison_data = year_filtered_data[['Country', 'GDP per Capita']].copy()
        comparison_data['World Median'] = world_median_gdp
        comparison_data = comparison_data.melt(id_vars=["Country"], value_vars=["GDP per Capita", "World Median"], 
                                               var_name="Metric", value_name="Value")

        fig_comparison = px.bar(comparison_data, x='Country', y='Value', color='Metric', 
                                title=f"Comparison of Selected Countries' GDP per Capita with World Median ({st.session_state.selected_year})")
        st.plotly_chart(fig_comparison)

    # **Time Series Graphical Analysis - Additional Section**
        st.title("Time Series Analysis of GDP per Capita")

    # Time series analysis for three periods
    periods = [(1990, 2000), (2001, 2010), (2011, 2023)]

    for period_start, period_end in periods:
        # Extract the relevant data for the period (years in the given range)
        period_years = [str(year) for year in range(period_start, period_end + 1)]
        period_data = cleaned_data[period_years].dropna(axis=1, how='all')  # Drop any columns that are fully NaN
    
        # Calculate the mean GDP per capita across all countries for each year in the period
        mean_gdp_per_year = period_data.mean(axis=0)  # Get the mean GDP for each year across all countries
     
        # Convert the Series to a DataFrame for plotting
        mean_gdp_df = mean_gdp_per_year.reset_index()
        mean_gdp_df.columns = ['Year', 'Mean GDP per Capita']  # Rename columns
    
        # **Line Chart for Time Series Trends in the Given Period**
        st.subheader(f"GDP per Capita Trends for {period_start} to {period_end}")
    
        # Plot the mean GDP per capita for the given period
        fig_line_period = px.line(mean_gdp_df, x="Year", y="Mean GDP per Capita", 
                                title=f"Mean GDP per Capita for {period_start} to {period_end}",
                                labels={"Year": "Year", "Mean GDP per Capita": "GDP per Capita (USD)"})
        st.plotly_chart(fig_line_period)

if show_gdp_info:
    st.title("What is GDP per Capita?")
    st.subheader("Definition")
    st.write("""
        **GDP per Capita** is a metric used to measure the economic output (Gross Domestic Product) per person in a given country. 
        It is calculated by dividing the country's GDP by its population.
    """)

    st.subheader("Why is it Important?")
    st.write("""
        GDP per capita is important because it allows for a comparison of the standard of living between countries or over time. 
        It provides a snapshot of the economic health of a country and is often used to compare the prosperity of nations.
    """)

    st.subheader("Formula")
    st.write("""
        The formula for calculating GDP per Capita is:
        
        **GDP per Capita** = **GDP** ÷ **Population**
        
        Where:
        - **GDP** is the total value of goods and services produced by a country within a year.
        - **Population** is the total number of people in that country.
    """)

    st.subheader("Example Calculation")
    st.write("""
        Let’s take the example of Country A:
        
        - GDP of Country A = \$1,000,000,000 (1 billion dollars)
        - Population of Country A = 50,000 people
        
        Using the formula:
        
        **GDP per Capita** = 1,000,000,000 ÷ 50,000 = **\$20,000**
        
        This means the average economic output per person in Country A is \$20,000.
    """)

    st.subheader("Visualizing GDP per Capita")
    st.write("""
        By analyzing GDP per capita, we can observe which countries are wealthier and which are struggling economically. This can help governments, businesses, and policymakers make informed decisions about investments, development strategies, and economic policies.""")
        
if measures_of_tendency_button:
    st.title("Measures of Tendency")

    # Extract the relevant data for the selected countries (use all countries if "All" is selected)
    if "All" in st.session_state.selected_countries:
        selected_countries_data = cleaned_data  # Use all data when "All" is selected
    else:
        selected_countries_data = cleaned_data[cleaned_data['Country'].isin(st.session_state.selected_countries)]

    # Calculate Skewness and Kurtosis over time (for each year)
    skewness_values = []
    kurtosis_values = []
    years = [str(year) for year in range(1990, 2024)]
    
    for year in years:
        year_data = selected_countries_data[year].dropna()

        # **Skewness**: Karl Pearson's Method
        mean_value = year_data.mean()
        median_value = year_data.median()
        std_deviation_value = year_data.std()
        skewness_karl_pearson = 3 * (mean_value - median_value) / std_deviation_value
        skewness_values.append(skewness_karl_pearson)
        
        # **Skewness**: Bowley's Method (using Quartiles)
        Q1 = year_data.quantile(0.25)
        Q2 = year_data.median()
        Q3 = year_data.quantile(0.75)
        skewness_bowley = (Q3 + Q1 - 2 * Q2) / (Q3 - Q1)
        kurtosis_value = year_data.kurtosis()  # Pearson’s method

        # Store the results for plotting
        kurtosis_values.append(kurtosis_value)

    # Create a DataFrame for plotting skewness and kurtosis over time
    tendency_data = pd.DataFrame({
        'Year': years,
        'Skewness (Karl Pearson)': skewness_values,
        'Kurtosis': kurtosis_values
    })
    
    # Line Chart for Skewness and Kurtosis over Time
    fig_tendency = px.line(tendency_data, x='Year', y=['Skewness (Karl Pearson)', 'Kurtosis'],
                           title="Skewness and Kurtosis over Time",
                           labels={"Year": "Year", "value": "Value", "variable": "Measure"})
    
    st.plotly_chart(fig_tendency)

    # Display the skewness and kurtosis values for the selected year
    selected_year_data = selected_countries_data[selected_year_str].dropna()

    # **Skewness**: Karl Pearson's Method for the selected year
    mean_value = selected_year_data.mean()
    median_value = selected_year_data.median()
    std_deviation_value = selected_year_data.std()

    skewness_karl_pearson = 3 * (mean_value - median_value) / std_deviation_value
    st.subheader("Skewness (Karl Pearson's Method)")
    st.write(f"Skewness (Karl Pearson's Method) = 3 * (Mean - Median) / Standard Deviation")
    st.write(f"Skewness: {skewness_karl_pearson:.2f}")

    # **Skewness**: Bowley's Method for the selected year
    Q1 = selected_year_data.quantile(0.25)
    Q2 = selected_year_data.median()
    Q3 = selected_year_data.quantile(0.75)

    skewness_bowley = (Q3 + Q1 - 2 * Q2) / (Q3 - Q1)
    st.subheader("Skewness (Bowley's Method)")
    st.write(f"Skewness (Bowley's Method) = (Q3 + Q1 - 2 * Q2) / (Q3 - Q1)")
    st.write(f"Skewness: {skewness_bowley:.2f}")

    # **Kurtosis**: Pearson’s method for the selected year
    kurtosis_value = selected_year_data.kurtosis()
    st.subheader("Kurtosis")
    st.write(f"Kurtosis: {kurtosis_value:.2f}")

    st.write("""
        **Detailed Understanding of Measures**:
        
        - **Skewness** tells us about the asymmetry of the distribution. A positive skew means the data is concentrated on the left side, and a negative skew means the data is concentrated on the right side.
        - **Kurtosis** helps us understand the shape of the distribution, specifically how fat or thin the tails are and whether the peak is higher or lower than the normal distribution. High kurtosis means more extreme outliers, and low kurtosis means fewer extremes.

    """)


# else:
#     # If the "GDP per Capita" button is not clicked, show the rest of the content
#     # Insights and GDP per Capita Section
#     st.title("GDP per Capita Analysis")

#     # Insights based on selected year
#     st.subheader(f"GDP per Capita Insights for {st.session_state.selected_year}")
#     year_filtered_data = (
#         filtered_data[['Country', 'ISO_Code', str(st.session_state.selected_year)]]
#         .rename(columns={str(st.session_state.selected_year): 'GDP per Capita'})
#         .dropna(subset=['ISO_Code', 'GDP per Capita'])
#     )

#     # Display top 10 countries with the highest GDP per capita only when "All" is selected
#     if "All" in st.session_state.selected_countries:
#         top_gdp = year_filtered_data.sort_values(by='GDP per Capita', ascending=False).head(10)
#         st.write("### Top 10 Countries by GDP per Capita")
#         st.write(top_gdp[['Country', 'GDP per Capita']])

#     # Average GDP per Capita
#     average_gdp = year_filtered_data['GDP per Capita'].mean()
#     st.write(f"### Average GDP per Capita in {st.session_state.selected_year}: ${average_gdp:,.2f}")

#     # World Median Comparison (Only when specific countries are selected)
#     if "All" not in st.session_state.selected_countries:
#         # Add world median as a comparison
#         st.write(f"### World Median GDP per Capita for {st.session_state.selected_year}: ${world_median_gdp:,.2f}")

#         # Visualize comparison between selected countries and world median
#         comparison_data = year_filtered_data[['Country', 'GDP per Capita']].copy()
#         comparison_data['World Median'] = world_median_gdp
#         comparison_data = comparison_data.melt(id_vars=["Country"], value_vars=["GDP per Capita", "World Median"], 
#                                                var_name="Metric", value_name="Value")

#         fig_comparison = px.bar(comparison_data, x='Country', y='Value', color='Metric', 
#                                 title=f"Comparison of Selected Countries' GDP per Capita with World Median ({st.session_state.selected_year})")
#         st.plotly_chart(fig_comparison)

#     # Visualization: Choropleth Map
#     st.subheader(f"GDP per Capita Global Map ({st.session_state.selected_year})")
#     fig_map = px.choropleth(
#         year_filtered_data,
#         locations="ISO_Code",
#         color="GDP per Capita",
#         hover_name="Country",
#         title=f"Global GDP per Capita in {st.session_state.selected_year}",
#         color_continuous_scale=px.colors.sequential.Plasma,
#         labels={"GDP per Capita": "GDP per Capita (USD)"}
#     )
#     st.plotly_chart(fig_map)

#     # Visualization: GDP Distribution (Histogram)
#     st.subheader(f"GDP per Capita Distribution in {st.session_state.selected_year}")
    
#     # Dynamically adjust bins and range of histogram based on number of countries selected
#     num_bins = 20 if len(st.session_state.selected_countries) < 10 else 10  # Adjust number of bins based on selection size
#     fig_histogram = px.histogram(year_filtered_data, x="GDP per Capita", nbins=num_bins, title=f"GDP per Capita Distribution ({st.session_state.selected_year})")
#     fig_histogram.update_layout(xaxis_title="GDP per Capita (USD)", yaxis_title="Frequency")
#     st.plotly_chart(fig_histogram)

#     # Line Chart: GDP per Capita trends over time for selected countries
#     st.subheader(f"GDP per Capita Trends Over Time for Selected Countries")
#     selected_countries_data = cleaned_data[cleaned_data['Country'].isin(st.session_state.selected_countries)]

#     # Reshaping the data for line chart
#     line_chart_data = selected_countries_data.melt(id_vars=["Country"], 
#                                                    value_vars=[str(year) for year in range(1990, 2024)], 
#                                                    var_name="Year", 
#                                                    value_name="GDP per Capita")

#     # Filter data for the selected countries and the year range
#     line_chart_data = line_chart_data[line_chart_data['Country'].isin(st.session_state.selected_countries)]

#     # Plotting the Line Chart
#     fig_line = px.line(line_chart_data, x="Year", y="GDP per Capita", color="Country",
#                        title=f"GDP per Capita Trends Over Time for Selected Countries",
#                        labels={"GDP per Capita": "GDP per Capita (USD)", "Year": "Year"})
#     st.plotly_chart(fig_line)

#     # Footer
#     st.markdown("**Data Source:** Provided CSV File")

