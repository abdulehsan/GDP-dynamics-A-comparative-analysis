import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Load the dataset
@st.cache_data
def load_data():
    file_path = './Datasets/New_folder/GDP_1960_to_2022.csv'  # Adjust this path as needed
    data = pd.read_csv(file_path)
    data_long = data.melt(
        id_vars=["Country", "Country Code"],
        var_name="Year",
        value_name="GDP"
    )
    data_long["Year"] = pd.to_numeric(data_long["Year"], errors="coerce")
    data_long["GDP"] = pd.to_numeric(data_long["GDP"], errors="coerce")
    # Remove aggregate and non-country entries
    exclude_list = [
        "World", "High income", "Low income", "OECD members", "Post-demographic dividend",
        "IDA & IBRD total", "IDA total", "IBRD only", "Middle income", "Upper middle income",
        "Low & middle income", "East Asia & Pacific", "Late-demographic dividend", "Early default dividend"
    ]
    data_long = data_long[~data_long["Country"].isin(exclude_list)]
    return data_long.dropna(subset=["GDP"])

# Load and cache data
gdp_data = load_data()

# Sidebar Features
st.sidebar.title("Navigation")
menu = st.sidebar.radio(
    "Go to",
    ["Dashboard", "Country Analysis", "Comparison", "Top/Bottom Performers", "World Map"]
)

st.sidebar.header("Key Metrics")
selected_year = st.sidebar.slider("Select Year", min_value=int(gdp_data["Year"].min()), max_value=int(gdp_data["Year"].max()), value=2022)
global_gdp_year = gdp_data[gdp_data["Year"] == selected_year]["GDP"].sum()
top_country_data = gdp_data[gdp_data["Year"] == selected_year].sort_values(by="GDP", ascending=False).iloc[0]

# Apply custom CSS for smaller metrics in sidebar
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

    st.subheader("Statistical Metrics")
    mean_gdp = country_data["GDP"].mean()
    median_gdp = country_data["GDP"].median()
    std_gdp = country_data["GDP"].std()
    st.metric("Mean GDP", f"{mean_gdp:,.2f} USD")
    st.metric("Median GDP", f"{median_gdp:,.2f} USD")
    st.metric("Standard Deviation", f"{std_gdp:,.2f} USD")

    st.write("""
    **Insights:**
    - GDP trends provide insights into the economic stability and growth of the country.
    - High variability in GDP might indicate fluctuating economic conditions.
    """)

elif menu == "Comparison":
    st.header("Multi-Country Comparison")
    selected_countries = st.multiselect("Select Countries for Comparison", options=gdp_data["Country"].unique(), default=gdp_data["Country"].unique()[:5])
    comparison_data = gdp_data[gdp_data["Country"].isin(selected_countries)]
    fig = px.line(comparison_data, x="Year", y="GDP", color="Country", title="GDP Comparison Across Selected Countries")
    st.plotly_chart(fig)

    st.header("Bar Chart Comparison")
    latest_comparison = comparison_data[comparison_data["Year"] == selected_year]
    fig = px.bar(latest_comparison, x="Country", y="GDP", color="Country", title=f"GDP in {selected_year}")
    st.plotly_chart(fig)

    st.write("""
    **Insights:**
    - Comparison highlights economic growth trajectories of selected countries.
    - Divergences in GDP trends may reflect differing industrialization and policy impacts.
    """)

elif menu == "Top/Bottom Performers":
    st.header("Top/Bottom Performers")
    year_data = gdp_data[gdp_data["Year"] == selected_year].sort_values(by="GDP", ascending=False)
    top_performers = year_data.head(10)
    bottom_performers = year_data.tail(10)

    st.subheader(f"Top 10 Performers in {selected_year}")
    fig = px.bar(top_performers, x="Country", y="GDP", title="Top 10 Performing Countries", text="GDP")
    st.plotly_chart(fig)
    st.write("""
    **Explanation:**
    - Top performers indicate the largest economies, reflecting industrial strength and policy effectiveness.
    """)

    st.subheader(f"Bottom 10 Performers in {selected_year}")
    fig = px.bar(bottom_performers, x="Country", y="GDP", title="Bottom 10 Performing Countries", text="GDP")
    st.plotly_chart(fig)
    st.write("""
    **Explanation:**
    - Bottom performers represent smaller or struggling economies with limited resources or challenges.
    """)

elif menu == "World Map":
    st.header("Interactive World Map")
    year_data = gdp_data[gdp_data["Year"] == selected_year]
    fig = px.choropleth(
        year_data,
        locations="Country Code",
        color="GDP",
        hover_name="Country",
        title=f"World GDP Distribution in {selected_year}",
        color_continuous_scale=px.colors.sequential.Plasma
    )
    st.plotly_chart(fig)
    st.subheader("Hover Insights")
    st.write("""
    Hover over a country to see detailed GDP insights. This map provides a global perspective of economic performance.
    """)
