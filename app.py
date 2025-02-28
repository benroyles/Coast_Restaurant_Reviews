import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go 
from datetime import datetime
import re

# Set the page configuration to wide layout
st.set_page_config(
    page_title="Coast Reviews Dashboard",  # Custom page title
    page_icon=":bar_chart:",  # Custom favicon (optional)
    layout="wide",  # Set layout to 'wide' for a larger display
    initial_sidebar_state="expanded"  # Optional, to expand the sidebar by default
)

# Load Data
@st.cache_data
def load_data():
    df = pd.read_csv("Review_dashboard_export.csv")  # Updated file name
    return df

df = load_data()

# Sidebar Filters
st.sidebar.header("Filters")
menu = st.sidebar.multiselect("Select Menu", sorted(df['Menu Mentions'].dropna().unique()))
tags = st.sidebar.multiselect("Select Tags", sorted(df['Tags'].dropna().unique()))
staff = st.sidebar.multiselect("Select Staff", sorted(df['Names Mentioned'].dropna().unique()))
theme = st.sidebar.multiselect("Select Theme", sorted(df['Theme'].dropna().unique()))
rating = st.sidebar.multiselect("Select Rating", sorted(df['Star Rating'].dropna().unique()))


# Apply filters based on sidebar inputs
df_filtered = df.copy()

# Filter by Menu Items, Tags, and Staff from the sidebar multiselects
if tags:
    df_filtered = df_filtered[df_filtered['Tags'].isin(tags)]
if staff:
    df_filtered = df_filtered[df_filtered['Names Mentioned'].isin(staff)]
if theme:
    df_filtered = df_filtered[df_filtered['Theme'].isin(theme)]
if menu:
    df_filtered = df_filtered[df_filtered['Menu Mentions'].isin(menu)]
if rating:
    df_filtered = df_filtered[df_filtered['Star Rating'].isin(rating)]

# Dashboard Layout
st.title("Coast Review Dashboard")

# Calculate the average scores for Food, Service, Atmosphere, and Star Ratings
st.subheader("Average Scores")

# Group by the 'Reversed Index' to avoid duplication, and calculate the mean for each column
df_avg_scores = df_filtered.groupby('Reversed Index')[['Food', 'Service', 'Atmosphere', 'Star Rating']].mean().reset_index()

# Get the averages for display (for the first review after grouping)
avg_food = df_avg_scores['Food'].mean()
avg_service = df_avg_scores['Service'].mean()
avg_atmosphere = df_avg_scores['Atmosphere'].mean()
avg_star_rating = df_avg_scores['Star Rating'].mean()

# Count the unique reviews by the 'Reversed Index'
review_count = df_filtered['Reversed Index'].nunique()

# Display the averages and count in a single row using st.columns
col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Average Food Rating", f"{avg_food:.2f}")
col2.metric("Average Service Rating", f"{avg_service:.2f}")
col3.metric("Average Atmosphere Rating", f"{avg_atmosphere:.2f}")
col4.metric("Average Star Rating", f"{avg_star_rating:.2f}")
col5.metric("Review Count", f"{review_count}")

# Count unique reversed indexes for each star rating
unique_reversed_count = df_filtered.drop_duplicates(subset='Reversed Index').groupby('Star Rating')['Reversed Index'].count().reset_index()

# Create the horizontal bar chart
fig_bar = px.bar(unique_reversed_count, 
                 x='Reversed Index', 
                 y='Star Rating', 
                 orientation='h', 
                 labels={'Reversed Index': 'Number of Reviews', 'Star Rating': 'Star Rating'},
                 title='Number of Reviews by Star Rating')

# Display the chart
st.plotly_chart(fig_bar)

# Bar Chart: Most Mentioned Tags
st.subheader("Top Mentioned Tags")

# Instead of just exploding and counting, we need to count unique mentions of tags per review
# We'll use 'drop_duplicates' to ensure a review only counts once per tag.
tag_counts = df_filtered.drop_duplicates(subset=['Reversed Index', 'Tags'])  # Ensure each review counts once per tag
tag_counts = tag_counts.explode('Tags')['Tags'].value_counts().reset_index()
tag_counts.columns = ['Tag', 'Mentions']  # Rename columns to 'Tag' and 'Mentions'

# Get top 15 most mentioned tags and sort in descending order of mentions
tag_counts = tag_counts.head(15).sort_values(by='Mentions', ascending=True)

# Create the horizontal bar chart
fig_bar_tags = px.bar(tag_counts, x='Mentions', y='Tag', orientation='h', labels={'Tag': 'Tag', 'Mentions': 'Mentions'})

# Display the chart
st.plotly_chart(fig_bar_tags)

from datetime import datetime

# Staff mentions over time
st.subheader("Staff Mentions Over Time")

# Ensure 'Names Mentioned' is properly formatted
df_filtered['Names Mentioned'].fillna('No Name Mentioned', inplace=True)

# Get all unique staff names from the filtered DataFrame
staff_names = sorted(df_filtered['Names Mentioned'].unique())

# Initialize dictionary to store counts
counts_dict = {name: {} for name in staff_names}

# Track seen reversed indexes to avoid duplicate counts
seen_indexes = set()

# Count occurrences of each staff name in each time period, ensuring unique reversed index
for _, row in df_filtered.iterrows():
    name = row['Names Mentioned']
    time_period = row['Time Period']
    reversed_index = row['Reversed Index']
    
    if reversed_index in seen_indexes:
        continue  # Skip duplicate entries based on reversed index
    seen_indexes.add(reversed_index)  # Mark this reversed index as counted
    
    if time_period not in counts_dict[name]:
        counts_dict[name][time_period] = 0
    counts_dict[name][time_period] += 1

# Convert counts_dict into a DataFrame
counts_df = pd.DataFrame(counts_dict).fillna(0).astype(int).T

# Add a total column
counts_df['Total'] = counts_df.sum(axis=1)

# Extract columns and identify date ranges and month names
date_range_columns = []
month_columns = []
for col in counts_df.columns:
    if 'to' in col:  # Simple check for date ranges
        date_range_columns.append(col)
    else:
        try:
            # Try parsing as a month name, e.g., 'January'
            datetime.strptime(f'01-{col}-2024', '%d-%B-%Y')
            month_columns.append(col)
        except ValueError:
            pass  # Ignore columns that don't match

# Convert date range columns to datetime for sorting
def extract_date(date_range):
    try:
        return datetime.strptime(date_range.split(' to ')[-1], '%d-%b-%Y')
    except ValueError:
        return datetime.min

sorted_date_range_columns = sorted(date_range_columns, key=lambda x: extract_date(x), reverse=False)
sorted_month_columns = sorted(month_columns, key=lambda x: datetime.strptime(f'01-{x}-2024', '%d-%B-%Y'), reverse=False)

# Combine sorted columns with 'Total' at the end
sorted_columns = sorted_month_columns + sorted_date_range_columns + ['Total']
counts_df = counts_df[sorted_columns]

# Sort by total mentions
counts_df = counts_df.sort_values('Total', ascending=False)

# Display the sorted table in Streamlit
st.dataframe(counts_df.head(20))  # Show top 20 staff mentions


# Pie Chart: Sentiment Distribution
st.subheader("Sentiment Distribution")
fig_pie = px.pie(df_filtered, names='Theme', title="Review Sentiments")
st.plotly_chart(fig_pie)

import plotly.graph_objects as go
import pandas as pd
from datetime import datetime
import streamlit as st

# Assuming you already have your dataframe 'df_filtered' ready...

# Average Star Rating and Review Count Over Time Period
st.subheader("Average Star Rating and Review Count Over Time Period")

# Track seen reversed indexes to avoid duplicate counts
seen_indexes = set()

# Initialize dictionaries to store average star ratings and review counts for each time period
avg_star_dict = {}
review_count_dict = {}

# Count occurrences of each time period with a unique reversed index
for _, row in df_filtered.iterrows():
    reversed_index = row['Reversed Index']
    time_period = row['Time Period']
    
    if reversed_index in seen_indexes:
        continue  # Skip duplicate entries based on reversed index
    seen_indexes.add(reversed_index)  # Mark this reversed index as counted
    
    # Get the star rating for this review
    star_rating = row['Star Rating']
    
    # Update average star rating calculation
    if time_period not in avg_star_dict:
        avg_star_dict[time_period] = {'total_rating': 0, 'count': 0}
    avg_star_dict[time_period]['total_rating'] += star_rating
    avg_star_dict[time_period]['count'] += 1

    # Update review count calculation
    if time_period not in review_count_dict:
        review_count_dict[time_period] = 0
    review_count_dict[time_period] += 1

# Convert the avg_star_dict into a DataFrame
avg_star_df = pd.DataFrame.from_dict(avg_star_dict, orient='index').reset_index()
avg_star_df.columns = ['Time Period', 'Total Rating', 'Review Count']

# Calculate the average star rating for each time period
avg_star_df['Avg Star Rating'] = avg_star_df['Total Rating'] / avg_star_df['Review Count']

# Add the review count for each time period
avg_star_df['Review Count'] = avg_star_df['Time Period'].map(review_count_dict)

# Calculate the cumulative average of the star ratings (current week + all previous weeks)
avg_star_df['Cumulative Avg Star Rating'] = avg_star_df['Total Rating'].cumsum() / avg_star_df['Review Count'].cumsum()

# Extract columns and identify date ranges and month names
date_range_columns = []
month_columns = []
for time_period in avg_star_df['Time Period']:
    if 'to' in time_period:  # Date range, e.g., "26 Jan - 01 Feb"
        date_range_columns.append(time_period)
    else:
        try:
            # Try parsing as a month name, e.g., 'January'
            datetime.strptime(f'01-{time_period}-2024', '%d-%B-%Y')
            month_columns.append(time_period)
        except ValueError:
            pass  # Ignore columns that don't match

# Convert date range columns to datetime for sorting
def extract_date(date_range):
    try:
        return datetime.strptime(date_range.split(' to ')[-1], '%d-%b-%Y')
    except ValueError:
        return datetime.min

sorted_date_range_columns = sorted(date_range_columns, key=lambda x: extract_date(x), reverse=False)
sorted_month_columns = sorted(month_columns, key=lambda x: datetime.strptime(f'01-{x}-2024', '%d-%B-%Y'), reverse=False)

# Combine sorted columns
sorted_time_periods = sorted_month_columns + sorted_date_range_columns

# Reorder the DataFrame based on the sorted time periods
avg_star_df['Time Period'] = pd.Categorical(avg_star_df['Time Period'], categories=sorted_time_periods, ordered=True)
avg_star_df = avg_star_df.sort_values('Time Period')

# Create a subplot with three charts
fig = go.Figure()

# Add the first chart (Average Star Rating)
fig.add_trace(
    go.Scatter(
        x=avg_star_df['Time Period'],
        y=avg_star_df['Avg Star Rating'],
        mode='lines+markers',
        name='Average Star Rating',
        line=dict(color='blue')
    )
)

# Add the second chart (Review Count)
fig.add_trace(
    go.Scatter(
        x=avg_star_df['Time Period'],
        y=avg_star_df['Review Count'],
        mode='lines+markers',
        name='Review Count',
        line=dict(color='red'),
        yaxis='y2'  # Use a secondary y-axis for the review count
    )
)

# Add the third chart (Cumulative Average Star Rating)
fig.add_trace(
    go.Scatter(
        x=avg_star_df['Time Period'],
        y=avg_star_df['Cumulative Avg Star Rating'],
        mode='lines+markers',
        name='Cumulative Average Star Rating',
        line=dict(color='green', dash='dot')
    )
)

# Create layout with secondary y-axis
fig.update_layout(
    title="Average Star Rating, Review Count, and Cumulative Average Over Time Period",
    xaxis=dict(title="Time Period"),
    yaxis=dict(title="Average Star Rating"),
    yaxis2=dict(
        title="Review Count",
        overlaying="y",
        side="right"
    ),
    template="plotly_white"  # Optional: to improve the visual style
)

# Display the chart
st.plotly_chart(fig)


# Time Series: Review Trends
st.subheader("Number of Reviews per Day")

# Ensure the 'Date Of Review' column is in datetime format
df_filtered['Date Of Review'] = pd.to_datetime(df_filtered['Date Of Review'])

# Group by 'Date Of Review' and count unique values in 'Reversed Index'
df_time = df_filtered.groupby('Date Of Review')['Reversed Index'].nunique().reset_index(name='count')

# Create the line chart
fig_line = px.line(df_time, x='Date Of Review', y='count', labels={'count': 'Review Count'})
st.plotly_chart(fig_line)

# Display Filtered Reviews
st.subheader("Filtered Reviews")

# To prevent duplication, we drop duplicates based on 'Reversed Index' and other relevant columns
df_display = df_filtered.drop_duplicates(subset=['Reversed Index'])

# Create a scrollable container for reviews
reviews_container = st.empty()

# Add scrollable HTML/CSS directly to the container
reviews_container.markdown(
    """
    <div style="max-height: 400px; overflow-y: auto; padding-right: 10px;">
    """, 
    unsafe_allow_html=True
)

# Loop through the filtered reviews and display each one with star rating
for _, row in df_display.iterrows():
    st.write(f"**Date Of Review**: {row['Date Of Review']}")
    st.write(f"**Star Rating**: {row['Star Rating']} ⭐")  # Show the star rating as a number with stars
    st.markdown(f"<div style='white-space: pre-wrap;'>{row['Review Text']}</div>", unsafe_allow_html=True)
    st.markdown("---")

# End the scrollable container
reviews_container.markdown("</div>", unsafe_allow_html=True)