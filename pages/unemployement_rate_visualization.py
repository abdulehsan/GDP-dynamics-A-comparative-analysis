import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Title of the Streamlit App
st.title("Unemployment Dataset Explorer")
st.markdown("Analyze and visualize unemployment trends interactively!")

# File Uploader
uploaded_file = r'Datasets\New folder\unemployment-rate-imf.csv'

if uploaded_file:
    # Load the dataset
    df = pd.read_csv(uploaded_file)
    st.write("### Dataset Preview")
    st.dataframe(df.head())import logging

# Create a logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Create a file handler and a stream handler
file_handler = logging.FileHandler('app.log')
stream_handler = logging.StreamHandler()

# Create a formatter and set it for the handlers
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
stream_handler.setFormatter(formatter)

# Add the handlers to the logger
logger.addHandler(file_handler)
logger.addHandler(stream_handler)

# ... (rest of the code remains the same)

# File Uploader
uploaded_file = r'Datasets\New folder\unemployment-rate-imf.csv'

if uploaded_file:
    logger.info('File uploaded successfully')
    # ... (rest of the code remains the same)

    # Load the dataset
    try:
        df = pd.read_csv(uploaded_file)
        logger.info('Dataset loaded successfully')
    except Exception as e:
        logger.error(f'Failed to load dataset: {str(e)}')
        st.write("Failed to load dataset. Please check the file and try again.")
        st.stop()

    # ... (rest of the code remains the same)

    # Basic Information
    st.write("### Dataset Information")
    st.write("#### Column Data Types:")
    st.write(df.dtypes)
    st.write("### Summary Statistics")
    st.write(df.describe())

    # ... (rest of the code remains the same)

    # Data Cleaning: Convert columns to numeric where applicable
    numeric_cols = [
        "Unemployment rate - Percent of total labor force - Observations", 
        "Unemployment rate - Percent of total labor force - Forecasts"
    ]
    for col in numeric_cols:
        if col in df.columns:
            try:
                # Convert column to numeric, forcing errors to NaN
                df[col] = pd.to_numeric(df[col], errors="coerce")
                logger.info(f'Converted column {col} to numeric successfully')
            except Exception as e:
                logger.error(f'Failed to convert column {col} to numeric: {str(e)}')

    # ... (rest of the code remains the same)

    # Drop rows with missing or invalid data in numeric columns
    try:
        df_cleaned = df.dropna(subset=numeric_cols)
        logger.info('Dropped rows with invalid numeric data successfully')
    except Exception as e:
        logger.error(f'Failed to drop rows with invalid numeric data: {str(e)}')
        st.write("Failed to clean dataset. Please check the data and try again.")
        st.stop()

    # ... (rest of the code remains the same)

    # --- Visualization 1: Distribution of Unemployment Rate ---
    st.write("## Distribution of Unemployment Rate (Observations)")
    if "Unemployment rate - Percent of total labor force - Observations" in df_cleaned.columns:
        try:
            fig1 = px.histogram(df_cleaned, 
                                x="Unemployment rate - Percent of total labor force - Observations", 
                                nbins=30, marginal="box",
                                title="Distribution of Unemployment Rate", opacity=0.8)
            fig1.update_layout(xaxis_title="Unemployment Rate (Observations)", yaxis_title="Frequency")
            logger.info('Created histogram successfully')
        except Exception as e:
            logger.error(f'Failed to create histogram: {str(e)}')
            st.write("Failed to create histogram. Please check the data and try again.")
            st.stop()

    # ... (rest of the code remains the same)
    # Basic Information
    st.write("### Dataset Information")
    st.write("#### Column Data Types:")
    st.write(df.dtypes)
    st.write("### Summary Statistics")
    st.write(df.describe())
    
    # Data Cleaning: Convert columns to numeric where applicable
    numeric_cols = [
        "Unemployment rate - Percent of total labor force - Observations", 
        "Unemployment rate - Percent of total labor force - Forecasts"
    ]
    for col in numeric_cols:
        if col in df.columns:
            # Convert column to numeric, forcing errors to NaN
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Drop rows with missing or invalid data in numeric columns
    df_cleaned = df.dropna(subset=numeric_cols)
    st.write(f"### Cleaned Dataset (Dropped Rows with Invalid Numeric Data)")
    st.dataframe(df_cleaned.head())

    # --- Visualization 1: Distribution of Unemployment Rate ---
    st.write("## Distribution of Unemployment Rate (Observations)")
    if "Unemployment rate - Percent of total labor force - Observations" in df_cleaned.columns:
        fig1 = px.histogram(df_cleaned, 
                            x="Unemployment rate - Percent of total labor force - Observations", 
                            nbins=30, marginal="box",
                            title="Distribution of Unemployment Rate", opacity=0.8)
        fig1.update_layout(xaxis_title="Unemployment Rate (Observations)", yaxis_title="Frequency")
        st.plotly_chart(fig1)

    # --- Visualization 2: Unemployment Rate Over Time ---
    if "Year" in df_cleaned.columns:
        st.write("## Unemployment Rate Over Time")
        fig2 = px.line(df_cleaned, 
                       x="Year", 
                       y="Unemployment rate - Percent of total labor force - Observations", 
                       title="Unemployment Rate Over Time")
        fig2.update_layout(xaxis_title="Year", yaxis_title="Unemployment Rate (Observations)")
        st.plotly_chart(fig2)

    # --- Visualization 3: Unemployment Rate Forecasts Over Time ---
    if "Unemployment rate - Percent of total labor force - Forecasts" in df_cleaned.columns:
        st.write("## Forecasted Unemployment Rate Over Time")
        fig3 = px.line(df_cleaned, 
                       x="Year", 
                       y="Unemployment rate - Percent of total labor force - Forecasts", 
                       title="Forecasted Unemployment Rate Over Time")
        fig3.update_layout(xaxis_title="Year", yaxis_title="Forecasted Unemployment Rate")
        st.plotly_chart(fig3)

    # --- Visualization 4: Correlation Heatmap ---
    st.write("## Correlation Heatmap")

    # Select only numeric columns
    numeric_cols = df_cleaned.select_dtypes(include=["float64", "int64"]).columns

    # Ensure there are numeric columns to process
    if len(numeric_cols) > 1:
        corr_matrix = df_cleaned[numeric_cols].corr()
        fig4 = go.Figure(data=go.Heatmap(
            z=corr_matrix.values,
            x=corr_matrix.columns,
            y=corr_matrix.columns,
            colorscale="Viridis",
            zmin=-1, zmax=1))
        fig4.update_layout(title="Correlation Heatmap")
        st.plotly_chart(fig4)
    else:
        st.write("Not enough numeric data to compute correlations.")

else:
    st.write("Please upload a CSV file to begin the analysis.")
