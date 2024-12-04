import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st
from pathlib import Path

file_path = Path(__file__).parent.parent / 'Datasets' / 'New_folder' / 'Cleaned_GDP_Growth.csv'
gdp_data = pd.read_csv(file_path)

st.title("Interactive GDP Growth Dashboard")
st.title("Navigation")
page = st.selectbox("Go to", ["Country Analysis", "Comparison", "Global Insights", "Top/Bottom Performers"])

if page == "Global Insights":
    selected_year = st.slider(
        "Select Year", min_value=1960, max_value=2022, value=2022
    )
    total_gdp_growth = gdp_data[str(selected_year)].sum()
    top_country = gdp_data.loc[gdp_data[str(selected_year)].idxmax(), "Country Name"]
    top_country_gdp = gdp_data[str(selected_year)].max()

    st.subheader("Global GDP Growth Insights")
    st.write(f"**Total Global GDP Growth in {selected_year}:** {total_gdp_growth}%")
    st.write(f"**Top Country:** {top_country} with {top_country_gdp}% growth")

    # Create a world map
    fig_map = px.choropleth(
        gdp_data,
        locations="Country Code",
        color=str(selected_year),
        hover_name="Country Name",
        color_continuous_scale="Viridis",
        title=f"GDP Growth Distribution in {selected_year}",
    )
    st.plotly_chart(fig_map)

    world_data = gdp_data[gdp_data['Country Name'] == 'World']
    world_growth = world_data.iloc[0, 3:].values  # Get GDP growth values for years

    # Bar Chart for Average Global GDP Growth by Year
    st.subheader("Average Global GDP Growth Over Time")
    fig_avg_growth = px.bar(
        x=gdp_data.columns[3:],  # Years
        y=world_growth,  # World GDP growth values
        labels={'x': 'Year', 'y': 'GDP Growth (%)'},
        title="Average Global GDP Growth (World)"
    )
    st.plotly_chart(fig_avg_growth)

# Country Analysis
elif page == "Country Analysis":
    st.subheader("Analyze GDP Growth for a Country")
    country = st.selectbox("Select Country", gdp_data["Country Name"].unique())

    # Filter data for the selected country
    country_data = gdp_data[gdp_data["Country Name"] == country]
    years = gdp_data.columns[3:]  # Skip metadata columns
    gdp_growth = country_data.iloc[0, 3:].values

    # Line chart for GDP growth over time
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=years,
        y=gdp_growth,
        mode='lines+markers',
        name='GDP Growth',
        line=dict(color='blue'),
        marker=dict(symbol='circle', size=6, color='red')
    ))

    # Adding labels and title
    fig.update_layout(
        title=f"GDP Growth Over Time ({country})",
        xaxis_title="Year",
        yaxis_title="GDP Growth (%)",
        template="plotly_dark"
    )
    st.plotly_chart(fig)

# Comparison
elif page == "Comparison":
    st.subheader("Compare GDP Growth Between Countries")
    
    # Step 1: Select multiple countries for comparison
    countries = st.multiselect(
        "Select Countries for Comparison:", gdp_data["Country Name"].unique()
    )

    if countries:
        # Filter data for selected countries
        comparison_data = gdp_data[gdp_data["Country Name"].isin(countries)]
        years = gdp_data.columns[3:]

        # Step 2: Line Chart to visualize GDP growth trends
        st.subheader("Line Chart: GDP Growth Trends Over the Years")
        fig_line = go.Figure()
        for country in countries:
            country_data = comparison_data[comparison_data["Country Name"] == country]
            gdp_growth = country_data.iloc[0, 3:].values
            fig_line.add_trace(
                go.Scatter(
                    x=years,
                    y=gdp_growth,
                    mode="lines+markers",
                    name=country,
                )
            )
        fig_line.update_layout(
            title="GDP Growth Comparison (Line Chart)",
            xaxis_title="Year",
            yaxis_title="GDP Growth (%)",
            template="plotly_dark",
        )
        st.plotly_chart(fig_line)

        # Step 3: Bar Chart with a year slider
        st.subheader("Bar Chart: GDP Growth for a Selected Year")
        selected_year = st.slider(
            "Select Year for Bar Chart:", 
            min_value=int(years[0]), 
            max_value=int(years[-1]), 
            value=int(years[-1])
        )
        bar_data = gdp_data[gdp_data["Country Name"].isin(countries)][
            ["Country Name", str(selected_year)]
        ]
        fig_bar = px.bar(
            bar_data,
            x="Country Name",
            y=str(selected_year),
            color="Country Name",
            title=f"GDP Growth in {selected_year} (Bar Chart)",
            labels={str(selected_year): "GDP Growth (%)"},
        )
        st.plotly_chart(fig_bar)

        # Step 4: Scatter Plot with a single year slider
        st.subheader("Scatter Plot: GDP Growth Comparison for a Selected Year")
        scatter_year = st.slider(
            "Select Year for Scatter Plot:", 
            min_value=int(years[0]), 
            max_value=int(years[-1]), 
            value=int(years[-1])
        )

        scatter_data = gdp_data[gdp_data["Country Name"].isin(countries)][
            ["Country Name", str(scatter_year)]
        ]

        fig_scatter = px.scatter(
            scatter_data,
            x="Country Name",
            y=str(scatter_year),
            color="Country Name",
            text="Country Name",
            title=f"Scatter Plot: GDP Growth in {scatter_year}",
            labels={str(scatter_year): f"GDP Growth in {scatter_year} (%)"},
        )
        fig_scatter.update_traces(textposition="top center")
        st.plotly_chart(fig_scatter)

# Top/Bottom Performers
elif page == "Top/Bottom Performers":
    st.subheader("Top and Bottom 10 GDP Growth Performers")

    # Year slider to select the year for top/bottom performers
    selected_year = st.slider(
        "Select Year for Top/Bottom Performers:",
        min_value=1960,
        max_value=2022,
        value=2022
    )

    # Sort countries based on the selected year's GDP growth
    top_performers = gdp_data.sort_values(str(selected_year), ascending=False).head(10)
    bottom_performers = gdp_data.sort_values(str(selected_year)).head(10)

    # Display the Top 10 Performers
    st.write(f"**Top 10 Countries with Highest GDP Growth in {selected_year}:**")
    st.dataframe(top_performers[['Country Name', str(selected_year)]])

    # Display the Bottom 10 Performers
    st.write(f"**Bottom 10 Countries with Lowest GDP Growth in {selected_year}:**")
    st.dataframe(bottom_performers[['Country Name', str(selected_year)]])

    # Optional: Display Top/Bottom Performers as a bar chart
    fig_top_bottom = go.Figure()

    # Bar chart for Top Performers
    fig_top_bottom.add_trace(go.Bar(
        x=top_performers['Country Name'],
        y=top_performers[str(selected_year)],
        name='Top Performers',
        marker=dict(color='green')
    ))

    # Bar chart for Bottom Performers
    fig_top_bottom.add_trace(go.Bar(
        x=bottom_performers['Country Name'],
        y=bottom_performers[str(selected_year)],
        name='Bottom Performers',
        marker=dict(color='red')
    ))

    fig_top_bottom.update_layout(
        title=f"Top and Bottom 10 GDP Performers in {selected_year}",
        xaxis_title="Country",
        yaxis_title="GDP Growth (%)",
        barmode='group',
        template="plotly_dark"
    )

    st.plotly_chart(fig_top_bottom)