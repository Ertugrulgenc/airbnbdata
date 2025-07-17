import streamlit as st
import pandas as pd
import altair as alt

# Load data
df = pd.read_csv("cleaned_file.csv")

# Sidebar filters
neighborhood = st.sidebar.selectbox("Select Neighborhood", df['neighbourhood_cleansed'].dropna().unique())
room_type = st.sidebar.selectbox("Select Room Type", df['room_type'].dropna().unique())
price_range = st.sidebar.slider("Price Range", 0, int(df['price'].str.replace("[$,]", "", regex=True).astype(float).max()), (50, 300))

# Clean price column
df['price_clean'] = df['price'].str.replace("[$,]", "", regex=True).astype(float)

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
filtered['first_review'] = pd.to_datetime(filtered['first_review'])
line = alt.Chart(filtered).mark_line().encode(
    x='first_review:T',
    y='review_scores_rating',
    color='room_type'
).properties(title="Review Scores Over Time")

# Layout
st.altair_chart(price_chart, use_container_width=True)
st.altair_chart(scatter, use_container_width=True)
st.altair_chart(line, use_container_width=True)