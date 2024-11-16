import streamlit as st
import pandas as pd
import plotly.express as px

# Set the title of the Streamlit app
st.title("GDP Visualization")

# Load the dataset
df = pd.read_csv(r'Datasets/New folder/GDP_Growth_Individual_Countries.csv', encoding='ISO-8859-1')


# Clean column names and ensure they are treated as strings
df.columns = df.columns.str.strip().astype(str)

# Display the first few rows of the dataset for reference
st.write("Dataset Preview:", df.head())

# Ensure the 'Country Name' column exists
if 'Country Name' not in df.columns:
    st.error("The 'Country Name' column is missing in the dataset.")
else:
    # Convert all year columns to numeric, if possible
    df.columns = [col.strip() for col in df.columns]
    
    # Get a list of available years from the dataset (excluding non-year columns)
    available_years = [col for col in df.columns if col.isdigit()]

    # Add a slider to select the year
    selected_year = st.slider("Select Year", min_value=int(min(available_years)), 
                              max_value=int(max(available_years)), value=2023)

    # Ensure the selected year exists in the dataset
    if str(selected_year) in df.columns:
        # Convert the selected year column to numeric, if necessary
        df[str(selected_year)] = pd.to_numeric(df[str(selected_year)], errors='coerce')
        
        # Remove rows with missing or NaN values for the selected year
        df = df.dropna(subset=[str(selected_year)])
        
        # Display a message if the column has no data
        if df.empty:
            st.write(f"No data available for the year {selected_year}.")
        else:
            # Create a choropleth map using Plotly
            fig = px.choropleth(
                df,
                locations='Country Name',
                locationmode='country names',
                color=str(selected_year),
                hover_name='Country Name',
                color_continuous_scale='Viridis',
                title=f'GDP Growth by Country in {selected_year}'
            )
            
            # Display the choropleth map in Streamlit
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.write(f"Column '{selected_year}' not found in the dataset.")
