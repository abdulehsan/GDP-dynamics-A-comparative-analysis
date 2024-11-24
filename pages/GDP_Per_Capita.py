import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

# Load the dataset
@st.cache_data(ttl=60)  # Updated caching method
def load_raw_data():
    file_path = Path(__file__).parent.parent / 'Datasets' / 'New_folder' / 'GDP_Per_Capita_Individual_Countries.csv'

    try:
        if not file_path.exists():
            raise FileNotFoundError(f"Dataset file not found at: {file_path}")
        raw_data = pd.read_csv(file_path)
        return raw_data
    except Exception as e:
        st.error(f"Error loading data: {e}")
        st.stop()

@st.cache_data(ttl=60)  # Updated caching method
def load_cleaned_data():
    raw_data = load_raw_data()

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

    # Step 7: Drop rows where critical fields like 'Country' or 'ISO_Code' are missing
    cleaned_data = cleaned_data.dropna(subset=['Country', 'ISO_Code'])

    return cleaned_data

# Load data
raw_data = load_raw_data()
cleaned_data = load_cleaned_data()

# Streamlit app title
st.title("Global GDP per Capita Dashboard")
st.markdown("Analyze and visualize GDP per capita data with interactive features.")

# Sidebar for filters and dataset views
st.sidebar.header("Filter Options")

# Use session state for button persistence
if "show_cleaned" not in st.session_state:
    st.session_state["show_cleaned"] = False
if "show_raw" not in st.session_state:
    st.session_state["show_raw"] = False

# Buttons to view datasets
if st.sidebar.button("View Raw Data"):
    st.session_state["show_raw"] = True
    st.session_state["show_cleaned"] = False

if st.sidebar.button("View Cleaned Data"):
    st.session_state["show_cleaned"] = True
    st.session_state["show_raw"] = False

# Display the datasets based on button state
if st.session_state["show_raw"]:
    st.subheader("Raw Dataset")
    st.dataframe(raw_data)

if st.session_state["show_cleaned"]:
    st.subheader("Cleaned Dataset")
    st.dataframe(cleaned_data)

    # Step-by-step explanation of data cleaning
    st.write("### Data Cleaning Process")
    st.markdown("""
    The following steps were taken to clean the raw dataset:
    1. **Remove Columns with All Missing Values**: Columns with no data for any year were dropped.
    2. **Retain Relevant Columns**: Only columns for `Country Name`, `Country Code`, `Indicator Name`, `Indicator Code`, and years `1990-2023` were kept.
    3. **Strip Whitespace**: Leading and trailing spaces were removed from column names and text fields.
    4. **Interpolate Missing Values**: Missing values in year columns were filled using **linear interpolation**.
    5. **Fill Remaining Gaps**: Any remaining missing values in numeric fields were replaced with `0`.
    6. **Rename Columns**: Columns were renamed to more descriptive names.
    7. **Drop Empty Rows**: Rows missing critical fields like `Country` or `ISO_Code` were removed.
    """)

    # Display null counts and other diagnostics
    st.write("### Data Diagnostics")
    st.write("#### Null Counts per Column:")
    st.write(cleaned_data.isnull().sum())
    st.write("#### Number of Rows and Columns:")
    st.write(cleaned_data.shape)

# Filter Options
years = [int(year) for year in cleaned_data.columns[4:]]
selected_year = st.sidebar.slider("Select Year", int(min(years)), int(max(years)), int(max(years)))

# Country Filter
available_countries = sorted(cleaned_data['Country'].dropna().unique())
selected_countries = st.sidebar.multiselect("Select Countries", options=["All"] + available_countries, default="All")

# Filter data
filtered_data = cleaned_data.copy()
if "All" not in selected_countries:
    filtered_data = filtered_data[filtered_data['Country'].isin(selected_countries)]

# Visualization: Choropleth Map
st.subheader(f"GDP per Capita in {selected_year}")
year_filtered_data = (
    filtered_data[['Country', 'ISO_Code', str(selected_year)]]
    .rename(columns={str(selected_year): 'GDP per Capita'})
    .dropna(subset=['ISO_Code', 'GDP per Capita'])
)
fig_map = px.choropleth(
    year_filtered_data,
    locations="ISO_Code",
    color="GDP per Capita",
    hover_name="Country",
    title=f"Global GDP per Capita in {selected_year}",
    color_continuous_scale=px.colors.sequential.Plasma,
    labels={"GDP per Capita": "GDP per Capita (USD)"}
)
st.plotly_chart(fig_map)

# Footer
st.markdown("**Data Source:** Provided CSV File")
