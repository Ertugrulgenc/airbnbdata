import streamlit as st
import pandas as pd
import altair as alt
import requests

st.title("Airbnb Listings Dashboard")

# Load data from Google Drive
file_id = "1lBYjeUP4yzAhEed0efY2I50KFnpkRkiR"
url = f"https://drive.google.com/uc?export=download&id={file_id}"

# Try reading the CSV with error handling
try:
    df = pd.read_csv(url, encoding='utf-8', on_bad_lines='skip')
except Exception as e:
    st.error(f"Failed to load data: {e}")
    st.stop()

# Optional: Clean column names to lowercase and underscores
df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

# Check if 'price' column exists
if 'price' not in df.columns:
    st.error("❌ 'price' column not found in the dataset. Please check the column names above.")
    st.stop()

# Clean price column
df['price_clean'] = df['price'].str.replace("[$,]", "", regex=True).astype(float)

# Sidebar filters
neighborhoods = df['neighbourhood_cleansed'].dropna().unique()
room_types = df['room_type'].dropna().unique()

neighborhood = st.sidebar.selectbox("Select Neighborhood", neighborhoods)
room_type = st.sidebar.selectbox("Select Room Type", room_types)
price_range = st.sidebar.slider(
    "Price Range",
    0,
    int(df['price_clean'].max()),
    (50, 300)
)

# Filtered data
filtered = df[
    (df['neighbourhood_cleansed'] == neighborhood) &
    (df['room_type'] == room_type) &
    (df['price_clean'].between(price_range[0], price_range[1]))
]

# Chart 1: Price Distribution
price_chart = alt.Chart(filtered).mark_bar().encode(
    x=alt.X('price_clean', bin=alt.Bin(maxbins=30), title='Price ($)'),
    y='count()',
    tooltip=['price_clean']
).properties(title="Price Distribution")

# Chart 2: Availability vs Revenue
scatter = alt.Chart(filtered).mark_circle(size=60).encode(
    x='availability_365',
    y='estimated_revenue_l365d',
    color='room_type',
    tooltip=['name', 'price_clean', 'availability_365', 'estimated_revenue_l365d']
).interactive().properties(title="Availability vs Estimated Revenue")

# Chart 3: Review Scores Over Time
filtered = filtered.copy()
filtered['first_review'] = pd.to_datetime(filtered['first_review'], errors='coerce')
line = alt.Chart(filtered.dropna(subset=['first_review'])).mark_line().encode(
    x='first_review:T',
    y='review_scores_rating',
    color='room_type'
).properties(title="Review Scores Over Time")

# Layout
st.altair_chart(price_chart, use_container_width=True)
st.altair_chart(scatter, use_container_width=True)
st.altair_chart(line, use_container_width=True)