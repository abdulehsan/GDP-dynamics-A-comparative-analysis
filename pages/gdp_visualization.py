import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import scipy.stats as stats
from pathlib import Path

@st.cache_data
def load_data():
    file_path = Path(__file__).parent.parent / 'Datasets' / 'New_folder' / 'GDP_1960_to_2022.csv'#'./Datasets/New_folder/GDP_1960_to_2022.csv'  # Adjust this path as needed
    data = pd.read_csv(file_path)
    data_long = data.melt(
        id_vars=["Country", "Country Code"],
        var_name="Year",
        value_name="GDP"
    )
    data_long["Year"] = pd.to_numeric(data_long["Year"], errors="coerce")
    data_long["GDP"] = pd.to_numeric(data_long["GDP"], errors="coerce")

    exclude_list = [
        "World", "High income", "Low income", "OECD members", "Post-demographic dividend",
        "IDA & IBRD total", "IDA total", "IBRD only", "Middle income", "Upper middle income",
        "Low & middle income", "East Asia & Pacific", "Late-demographic dividend", "Early default dividend"
    ]
    data_long = data_long[~data_long["Country"].isin(exclude_list)]
    return data_long.dropna(subset=["GDP"])

gdp_data = load_data()

st.sidebar.title("Navigation")
menu = st.sidebar.radio(
    "Go to",
    ["Dashboard", "Country Analysis", "Comparison", "Top/Bottom Performers", "World Map"]
)

st.sidebar.header("Key Metrics")
selected_year = st.sidebar.slider("Select Year", min_value=int(gdp_data["Year"].min()), max_value=int(gdp_data["Year"].max()), value=2022)
global_gdp_year = gdp_data[gdp_data["Year"] == selected_year]["GDP"].sum()
top_country_data = gdp_data[gdp_data["Year"] == selected_year].sort_values(by="GDP", ascending=False).iloc[0]

st.sidebar.markdown(
    """
    <style>
    .metric-container {
        font-size: 0.85rem !important;
    }
    .metric-value {
        font-size: 1rem !important;
        color: #f5f5f5;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.sidebar.markdown(
    f"""
    <div class="metric-container">
        <p><strong>Global GDP (USD):</strong></p>
        <p class="metric-value">{global_gdp_year:,.2f}</p>
        <p><strong>Top Country:</strong></p>
        <p class="metric-value">{top_country_data['Country']}</p>
        <p><strong>Top Country GDP:</strong></p>
        <p class="metric-value">{top_country_data['GDP']:,.2f} USD</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# Sidebar: Dataset Information
st.sidebar.header("Dataset Information")
st.sidebar.write(f"Number of Records: {len(gdp_data):,}")
st.sidebar.write(f"Number of Countries: {gdp_data['Country'].nunique()}")

# App Title
st.title("Global GDP Analysis Dashboard (1960-2022)")

if menu == "Dashboard":
    st.header("Global GDP Trends")
    global_gdp = gdp_data.groupby("Year")["GDP"].sum().reset_index()
    fig = px.line(global_gdp, x="Year", y="GDP", title="Total Global GDP Over Time", labels={"GDP": "Total GDP (USD)"})
    st.plotly_chart(fig)
    st.write("""
    **Insights:**
    - Consistent global GDP growth indicates economic development over decades.
    - Significant dips reflect global financial crises or events.
    """)

    # Donut Chart for GDP Contribution by Top Countries
    st.header("Top Contributors to GDP")
    top_countries = gdp_data[gdp_data["Year"] == selected_year].sort_values(by="GDP", ascending=False).head(10)
    fig = px.pie(top_countries, names="Country", values="GDP", title="Top 10 Countries' Contribution to Global GDP", hole=0.4)
    st.plotly_chart(fig)
    st.write("""
    **Insights:**
    - The top 10 countries contribute a major portion to global GDP, reflecting their industrial and economic strength.
    """)


elif menu == "Country Analysis":
    st.header("Country-Specific Analysis")
    countries = gdp_data["Country"].unique()
    selected_country = st.selectbox("Select a Country", options=countries)
    country_data = gdp_data[gdp_data["Country"] == selected_country]

    # Line Chart for GDP Trends
    fig = px.line(country_data, x="Year", y="GDP", title=f"GDP Trends for {selected_country}", labels={"GDP": "GDP (USD)"})
    st.plotly_chart(fig)

    # Calculate previous statistical metrics
    mean_gdp = country_data["GDP"].mean()
    median_gdp = country_data["GDP"].median()
    std_gdp = country_data["GDP"].std()

    # Calculate new statistical metrics
    gdp_values = country_data.dropna(subset=["GDP"])["GDP"]

    # Quartile Deviation
    q1 = gdp_values.quantile(0.25)
    q3 = gdp_values.quantile(0.75)
    quartile_deviation = (q3 - q1) / 2

    # Mean Deviation
    mean_deviation = (gdp_values - mean_gdp).abs().mean()

    # Kurtosis and Skewness
    kurtosis = stats.kurtosis(gdp_values)
    skewness = stats.skew(gdp_values)

    # Function to format GDP in both full and shortened form
    def format_gdp(value):
        if value >= 1e12:
            return f"{value:,.2f} USD ({value/1e12:.1f} Trillion)"
        elif value >= 1e9:
            return f"{value:,.2f} USD ({value/1e9:.1f} Billion)"
        elif value >= 1e6:
            return f"{value:,.2f} USD ({value/1e6:.1f} Million)"
        else:
            return f"{value:,.2f} USD"

    st.subheader("Statistical Metrics")

    # Display previous metrics with both full and shortened formats
    st.metric("Mean GDP", format_gdp(mean_gdp))
    st.metric("Median GDP", format_gdp(median_gdp))
    st.metric("Standard Deviation", format_gdp(std_gdp))

    # Display new statistical concepts
    st.metric("Quartile Deviation", format_gdp(quartile_deviation))
    st.metric("Mean Deviation", format_gdp(mean_deviation))
    st.metric("Kurtosis", f"{kurtosis:.2f}")
    st.metric("Skewness", f"{skewness:.2f}")

    st.write("""
    **Insights:**
    - **GDP Trends**: The line graph shows the growth or contraction of the country's economy over time. 
    - **Quartile Deviation**: This metric provides a measure of how spread out the middle 50% of the GDP values are, offering insight into the country’s economic stability.
    - **Mean Deviation**: The average of the absolute deviations from the mean GDP provides an overall idea of how much the country's GDP fluctuates around the average.
    - **Standard Deviation**: A high standard deviation suggests greater fluctuations in GDP, whereas a low standard deviation indicates a more stable economy.
    - **Kurtosis**: The kurtosis measures the "tailedness" of the GDP distribution, with values greater than 3 indicating a heavy-tailed distribution and values below 3 indicating a light-tailed distribution.
    - **Skewness**: Skewness indicates the asymmetry of the GDP distribution. Positive skew indicates that the right tail is longer or fatter than the left, while negative skew suggests the opposite.
    """)


# elif menu == "Comparison":
#     st.header("Multi-Country Comparison")
#     selected_countries = st.multiselect("Select Countries for Comparison", options=gdp_data["Country"].unique(), default=gdp_data["Country"].unique()[:5])
#     comparison_data = gdp_data[gdp_data["Country"].isin(selected_countries)]
#     fig = px.line(comparison_data, x="Year", y="GDP", color="Country", title="GDP Comparison Across Selected Countries")
#     st.plotly_chart(fig)

#     st.header("Bar Chart Comparison")
#     latest_comparison = comparison_data[comparison_data["Year"] == selected_year]
#     fig = px.bar(latest_comparison, x="Country", y="GDP", color="Country", title=f"GDP in {selected_year}")
#     st.plotly_chart(fig)

#     st.write("""
#     **Insights:**
#     - Comparison highlights economic growth trajectories of selected countries.
#     - Divergences in GDP trends may reflect differing industrialization and policy impacts.
#     """)

elif menu == "Comparison":
    st.header("Multi-Country Comparison")
    selected_countries = st.multiselect("Select Countries for Comparison", options=gdp_data["Country"].unique(), default=gdp_data["Country"].unique()[:5])
    comparison_data = gdp_data[gdp_data["Country"].isin(selected_countries)]
    
    # Line Chart for GDP Trends across selected countries
    fig = px.line(comparison_data, x="Year", y="GDP", color="Country", title="GDP Comparison Across Selected Countries")
    st.plotly_chart(fig)

    with st.expander("Insights for Line Chart"):
        st.write("""
        - The **line chart** compares the economic growth of the selected countries over time, providing an overview of long-term trends.
        - The chart helps in identifying patterns such as upward or downward trends in the GDP.
        - **Upward trends** suggest economic growth, while **downward trends** signal potential economic challenges or recessions.
        - **Sharp dips or peaks** may indicate key economic events (e.g., global crises or national economic policies).
        """)

    # Bar Chart for GDP Comparison in the selected year
    latest_comparison = comparison_data[comparison_data["Year"] == selected_year]
    fig = px.bar(latest_comparison, x="Country", y="GDP", color="Country", title=f"GDP in {selected_year}")
    st.plotly_chart(fig)

    with st.expander("Insights for Bar Chart"):
        st.write("""
        - The **bar chart** for the selected year highlights the GDP values in that specific year, making it easier to compare countries directly.
        - It visually represents how different countries performed in terms of GDP for that particular year.
        - This chart can help you quickly identify which countries have the largest or smallest economies in the selected year.
        """)

    # Scatterplot to compare GDP values across countries in a specific year (selected_year)
    fig = px.scatter(latest_comparison, x="Country", y="GDP", size="GDP", color="Country", hover_name="Country", title=f"GDP Scatter Plot for {selected_year}")
    st.plotly_chart(fig)

    with st.expander("Insights for Scatter Plot"):
        st.write("""
        - The **scatter plot** compares the GDP values of the selected countries in a specific year (selected_year).
        - The size of the bubbles is proportional to the GDP values, which visually indicates which countries have a larger economy.
        - This chart helps you see not only the GDP values but also how they compare in scale and position across the selected countries.
        """)

    # Pie Chart to visualize GDP distribution across the selected countries in the chosen year
    fig = px.pie(latest_comparison, names="Country", values="GDP", title=f"GDP Distribution Among Selected Countries in {selected_year}")
    st.plotly_chart(fig)

    with st.expander("Insights for Pie Chart"):
        st.write("""
        - The **pie chart** visualizes how the GDP is distributed among the selected countries for the chosen year.
        - It helps to see which countries dominate the GDP share in the selected group.
        - A larger slice indicates a higher GDP contribution of that country relative to the others.
        """)

    # Donut chart for GDP distribution among selected countries
    fig = px.pie(latest_comparison, names="Country", values="GDP", hole=0.4, title=f"GDP Distribution Among Selected Countries (Donut Chart) in {selected_year}")
    st.plotly_chart(fig)

    with st.expander("Insights for Donut Chart"):
        st.write("""
        - The **donut chart** is a variation of the pie chart, offering the same information but with a visually appealing "hole" in the middle.
        - It provides the same insight as the pie chart: which countries have the largest share of GDP within the selected group.
        - The donut chart is often considered more visually appealing and is useful for presentations.
        """)

    # General Insights for all charts
    with st.expander("General Insights"):
        st.write("""
        - These visualizations give a multi-faceted view of GDP data for the selected countries.
        - By using various chart types (line, bar, scatter, pie, and donut), you can identify trends, compare values, and understand the relative economic positions of the selected countries.
        - Each chart provides a different perspective on the GDP data, whether you're comparing over time, across countries, or by year.
        """)



# elif menu == "Top/Bottom Performers":
#     st.header("Top/Bottom Performers")
#     year_data = gdp_data[gdp_data["Year"] == selected_year].sort_values(by="GDP", ascending=False)
#     top_performers = year_data.head(10)
#     bottom_performers = year_data.tail(10)

#     st.subheader(f"Top 10 Performers in {selected_year}")
#     fig = px.bar(top_performers, x="Country", y="GDP", title="Top 10 Performing Countries", text="GDP")
#     st.plotly_chart(fig)
#     st.write("""
#     **Explanation:**
#     - Top performers indicate the largest economies, reflecting industrial strength and policy effectiveness.
#     """)

#     st.subheader(f"Bottom 10 Performers in {selected_year}")
#     fig = px.bar(bottom_performers, x="Country", y="GDP", title="Bottom 10 Performing Countries", text="GDP")
#     st.plotly_chart(fig)
#     st.write("""
#     **Explanation:**
#     - Bottom performers represent smaller or struggling economies with limited resources or challenges.
#     """)

elif menu == "Top/Bottom Performers":
    st.header("Top/Bottom Performers")
    year_data = gdp_data[gdp_data["Year"] == selected_year].sort_values(by="GDP", ascending=False)
    top_performers = year_data.head(10)
    bottom_performers = year_data.tail(10)

    # Function to format GDP values in a shortened format
    def format_value(value):
        if value >= 1e12:
            return f"{value/1e12:.1f} Trillion"
        elif value >= 1e9:
            return f"{value/1e9:.1f} Billion"
        elif value >= 1e6:
            return f"{value/1e6:.1f} Million"
        else:
            return f"{value:,.2f}"

    # Top Performers
    st.subheader(f"Top 10 Performers in {selected_year}")
    top_performers["Formatted GDP"] = top_performers["GDP"].apply(format_value)
    fig = px.bar(top_performers, x="Country", y="GDP", title="Top 10 Performing Countries", text="Formatted GDP")
    st.plotly_chart(fig)

    # Explanation inside an expander for Top Performers
    with st.expander("Top Performers Insights"):
        st.write("""
        - **Top economies** with **strong industrial bases** and **advanced infrastructure**.
        - Leaders in sectors like **technology, finance**, and **manufacturing**.
        - Countries like **China** and **India** are rising fast due to rapid growth and **industrialization**.
        - High **global influence** and **economic stability**.
        """)

    # Bottom Performers
    st.subheader(f"Bottom 10 Performers in {selected_year}")
    bottom_performers["Formatted GDP"] = bottom_performers["GDP"].apply(format_value)
    fig = px.bar(bottom_performers, x="Country", y="GDP", title="Bottom 10 Performing Countries", text="Formatted GDP")
    st.plotly_chart(fig)

    # Explanation inside an expander for Bottom Performers
    with st.expander("Bottom Performers Insights"):
        st.write("""
        - **Smaller economies** facing **political instability**, **underdeveloped infrastructure**, and **limited resources**.
        - High dependence on sectors like **agriculture** or **natural resources**.
        - Vulnerable to **global market fluctuations** and **commodity price changes**.
        - **Growth potential** exists through **investments in infrastructure** and **economic reforms**.
        """)


elif menu == "World Map":
    st.header("Interactive World Map")

    # Select Year for the map
    selected_year = st.sidebar.selectbox("Select Year", gdp_data["Year"].unique())

    # Filter data for selected year
    year_data = gdp_data[gdp_data["Year"] == selected_year]

    # Customizable Color Scale
    color_scale = st.sidebar.selectbox(
        "Select Color Scale", 
        ['Plasma', 'Viridis', 'Cividis', 'Inferno', 'Blues', 'RdYlGn', 'YlGnBu', 'Turbo']
    )

    # Interactive Choropleth Map with user-selected color scale
    fig = px.choropleth(
        year_data,
        locations="Country Code",
        color="GDP",
        hover_name="Country",
        title=f"World GDP Distribution in {selected_year}",
        color_continuous_scale=color_scale,
        labels={"GDP": "GDP (USD)"}
    )

    # Display Map
    st.plotly_chart(fig)

    # Add Color Customization Description
    st.subheader("Color Customization")
    st.write("""
    You can select different color scales for the map to view the GDP distribution across countries. 
    Choose a scale that best fits your visualization needs!
    """)

    # Additional Insights (Expanded explanation)
    with st.expander("Hover Insights"):
        st.write("""
        Hover over a country to see detailed GDP insights. This map provides a global perspective of economic performance.
        You can adjust the color scale and download a detailed report that includes key GDP information and charts.
        """)

