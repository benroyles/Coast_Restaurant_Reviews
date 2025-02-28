# Coast Reviews Dashboard

This repository contains the code and resources for the Coast Reviews Dashboard, a data analysis project for processing and visualizing customer feedback from restaurant reviews. The dashboard is built using Python, Streamlit, and various data analysis libraries.

## Project Overview

The Coast Reviews Dashboard is designed to help analyze customer reviews by extracting key insights such as:

- Review sentiments and ratings.
- Frequently mentioned staff members, food items, and menu items.
- Time-based trends, including review frequency over specific periods.
- The ability to filter and display reviews based on various attributes such as staff members, meal types, etc.

### Web Scraping and Data Preprocessing

To provide the dataset for the dashboard, web scraping techniques are used to collect customer reviews from restaurant review platforms. The scraping process targets specific elements such as:

- **Review Text**: Captures the content of customer feedback.
- **Review Rating**: Extracts the star ratings associated with each review.
- **Review Time**: Records when the review was written, enabling time-based analysis.

Once the reviews are scraped, the data is preprocessed using several steps to prepare it for analysis and visualization:

- **Text Normalization**: The review text is cleaned by converting it to lowercase, removing possessive forms (e.g., “Ben's” → “Ben”), and eliminating unnecessary characters.
- **Tagging Mentions**: Names of staff, food items, and menu mentions are tagged and identified within the reviews.
- **Exploding Data**: The data is exploded so that each tag or name mentioned in a review gets its own row, allowing for more granular analysis.

The preprocessing pipeline ensures that the dataset is consistent, structured, and ready for filtering and analysis within the dashboard.

The dashboard provides an interactive user interface to allow non-technical users to view and filter review data easily.

## Features

- **Staff Mention Analysis**: Identifies and visualizes which staff members are mentioned in customer reviews.
- **Review Filtering**: Allows filtering reviews based on various attributes such as meal type, staff names, and ratings.
- **Data Visualization**: Displays key metrics about the reviews using interactive charts and tables.
- **Time-based Analysis**: Visualizes reviews and mentions over specific time periods.

## Technologies Used

- **Python**: Core programming language for data processing and analysis.
- **Streamlit**: Framework for building interactive dashboards and web applications.
- **Pandas**: Library for data manipulation and analysis.
- **Matplotlib**: For creating basic plots and visualizations.
- **Scikit-learn**: For any machine learning models if used.
- **Regex (re module)**: For text processing and cleaning, especially for extracting mentions of staff names.

## Acknowledgements

- **Streamlit**: For making it easy to create interactive dashboards.
- **Pandas**: For efficient data manipulation.
- **Matplotlib**: For creating visualizations.
