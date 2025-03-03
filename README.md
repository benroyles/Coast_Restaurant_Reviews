# Coast Reviews Dashboard

This repository contains the code and resources for the **Coast Reviews Dashboard**, a data analysis project designed to process and visualize customer feedback from restaurant reviews. The dashboard is built using **Python, Streamlit**, and various data analysis libraries, providing an interactive way to explore and filter review data.

## Project Overview

The **Coast Reviews Dashboard** is designed to extract key insights from restaurant customer reviews, including:

- **Review Sentiments and Ratings**: Understanding overall customer satisfaction.
- **Frequently Mentioned Staff Members, Food Items, and Menu Items**: Identifying key themes in feedback.
- **Time-Based Trends**: Analyzing review frequency and sentiment trends over time.
- **Custom Filtering**: Allowing users to filter reviews based on attributes such as staff members, meal types, and time periods.

## Web Scraping and Automated Data Extraction

To collect customer reviews, an automated **web scraping pipeline** was built using:

- **Selenium**: For automating browser interactions, navigating through dynamic restaurant review pages, handling pagination, and loading content dynamically.
- **BeautifulSoup**: For parsing the HTML structure and extracting relevant information such as review text, ratings, timestamps, and reviewer details.

### Web Scraping Workflow:

1. **Automated Navigation**: Selenium simulates user interactions to load full review pages, including handling infinite scrolling and clicking "Load More" buttons when necessary.
2. **HTML Parsing**: BeautifulSoup extracts structured data from each review, identifying key elements like review text, ratings, and review dates.
3. **Data Storage**: Scraped reviews are saved as structured **CSV** files for further processing.
4. **Scheduled Scraping**: A **script is scheduled to run at regular intervals**, ensuring the dataset stays updated with new reviews.

## Data Preprocessing & Cleaning

Once the reviews are collected, a **data preprocessing pipeline** ensures the data is structured and ready for analysis. This includes:

- **Text Normalization**: Converting text to lowercase, removing unnecessary characters, and standardizing formatting.
- **Tagging Mentions**: Extracting and tagging references to staff members, food items, and menu mentions using **regular expressions (Regex)** and **NLP techniques**.
- **Data Explosion**: To facilitate granular analysis, each identified tag (staff name, food item, etc.) is assigned its own row in the dataset.
- **Handling Duplicates**: Implementing a reversed index system to prevent multiple versions of the same review from appearing in the final dataset.

## Dashboard Features

The **Coast Reviews Dashboard** provides an intuitive interface for exploring the processed review data. Key features include:

- **Staff Mention Analysis**: Identifies which staff members are frequently mentioned in customer reviews.
- **Review Filtering**: Users can filter reviews based on multiple attributes, such as meal type, staff names, and star ratings.
- **Interactive Data Visualization**: Displays key review metrics using dynamic charts and tables.
- **Time-Based Analysis**: Visualizes trends in customer sentiment and review frequency over time.

## Technologies Used

- **Python**: Primary language for data scraping, processing, and dashboard development.
- **Streamlit**: Framework for building interactive dashboards.
- **Pandas**: For data manipulation and analysis.
- **Matplotlib & Seaborn**: For generating visual insights from the data.
- **Selenium & BeautifulSoup**: For web scraping and data extraction.
- **Scikit-learn**: For potential sentiment analysis or machine learning enhancements.
- **Regex (re module)**: For extracting and tagging mentions of staff names, food items, and menu references.

## Acknowledgements

- **Streamlit**: For providing an easy way to build interactive dashboards.
- **Pandas & Matplotlib**: For data manipulation and visualization.
- **Selenium & BeautifulSoup**: For automating and streamlining data collection.

---

This project provides a comprehensive look at customer feedback trends, helping restaurants gain valuable insights from their reviews. Contributions and feedback are welcome!

