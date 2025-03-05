import datetime
import logging
import pandas as pd
import ast
import time
from datetime import timedelta
from bs4 import BeautifulSoup
import numpy as np
import spacy
import string
from datetime import datetime, timedelta
from collections import Counter
import re
import datetime
from rapidfuzz import process, fuzz
import logging
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

# Get today's date and format it
today = datetime.date.today()
formatted_today = today.strftime("%Y%m%d")  # Format as YYYYMMDD

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Variables for timing and scrolling
SCROLL_COUNT = 3
SCROLL_PAUSE = 5
PAGE_LOAD_WAIT = 5
CLICK_WAIT = 5
SORT_WAIT = 5
REVIEW_EXPAND_WAIT = 5

# Function to set up the WebDriver
def setup_driver():
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    service = ChromeService(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=options)

# Function to open URL and load the page
def open_url(driver, url):
    driver.get(url)
    time.sleep(PAGE_LOAD_WAIT)

# Function to click the 'Reviews' button if present
def click_reviews_button(driver):
    try:
        more_button = WebDriverWait(driver, CLICK_WAIT).until(
            EC.element_to_be_clickable((By.XPATH, '//button[contains(@aria-label, "Reviews")]'))
        )
        more_button.click()
        time.sleep(CLICK_WAIT)
        logging.info("Clicked 'Reviews' button.")
    except Exception as e:
        logging.warning(f"Error clicking 'Reviews' button: {e}")

# Function to locate the reviews container
def locate_reviews_container(driver):
    try:
        return WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="QA0Szd"]/div/div/div[1]/div[2]/div/div[1]/div/div/div[2]'))
        )
    except Exception as e:
        logging.error(f"Error locating reviews container: {e}")
        driver.quit()
        exit()

# Function to sort reviews by 'Newest'
def sort_reviews_by_newest(driver):
    try:
        sort_button = WebDriverWait(driver, CLICK_WAIT).until(
            EC.element_to_be_clickable((By.XPATH, '//button[@aria-label="Sort reviews"]'))
        )
        sort_button.click()
        time.sleep(SORT_WAIT)
        newest_option = WebDriverWait(driver, CLICK_WAIT).until(
            EC.element_to_be_clickable((By.XPATH, '//div[@role="menuitemradio" and @data-index="1"]'))
        )
        newest_option.click()
        time.sleep(CLICK_WAIT)
        logging.info("Sorted reviews by 'Newest'.")
    except Exception as e:
        logging.warning(f"Error sorting reviews: {e}")

# Function to scroll within the reviews container
def scroll_reviews_container(driver, container):
    for _ in range(SCROLL_COUNT):
        driver.execute_script("arguments[0].scrollBy(0, 4000);", container)
        time.sleep(SCROLL_PAUSE)
    logging.info("Finished scrolling reviews container.")

# Function to expand all reviews
def expand_all_reviews(driver):
    while True:
        try:
            more_buttons = driver.find_elements(By.XPATH, '//button[contains(@aria-label, "See more")]')
            if not more_buttons:
                break
            for button in more_buttons:
                button.click()
                time.sleep(REVIEW_EXPAND_WAIT)
        except Exception as e:
            logging.warning(f"Error clicking 'More' button: {e}")
            break

# Function to extract reviews and additional elements
def extract_reviews_and_additional_elements(soup):
    reviews = []
    review_elements = soup.find_all('div', {'class': 'GHT2ce'})

    for review_element in review_elements:
        try:
            star_rating_span = review_element.find('span', {'class': 'kvMYJc'})
            star_rating = star_rating_span.get('aria-label') if star_rating_span else 'No rating'
        except Exception as e:
            logging.warning(f"Error extracting star rating: {e}")
            star_rating = 'No rating'

        try:
            review_text_div = review_element.find('div', {'class': 'MyEned'})
            review_text_span = review_text_div.find('span', {'class': 'wiI7pd'}) if review_text_div else None
            review_text = review_text_span.get_text(strip=True) if review_text_span else 'No review text'
        except Exception as e:
            logging.warning(f"Error extracting review text: {e}")
            review_text = 'No review text'

        try:
            time_since_review_span = review_element.find('span', {'class': 'rsqaWe'})
            time_since_review = time_since_review_span.get_text(strip=True) if time_since_review_span else 'No time info'
        except Exception as e:
            logging.warning(f"Error extracting time since review: {e}")
            time_since_review = 'No time info'

        try:
            additional_info_spans = review_element.find_all('span', {'class': 'RfDO5c'})
            additional_info = [span.get_text(strip=True) for span in additional_info_spans] if additional_info_spans else 'No additional info'
        except Exception as e:
            logging.warning(f"Error extracting additional info: {e}")
            additional_info = 'No additional info'

        reviews.append({
            'Star Rating': star_rating,
            'Review Text': review_text,
            'Time Since Review': time_since_review,
            'Additional Info': additional_info
        })

    return reviews

# Main scraping function
def scrape_reviews(url, output_csv):
    driver = setup_driver()
    open_url(driver, url)
    click_reviews_button(driver)
    reviews_container = locate_reviews_container(driver)
    sort_reviews_by_newest(driver)
    scroll_reviews_container(driver, reviews_container)
    expand_all_reviews(driver)

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    reviews = extract_reviews_and_additional_elements(soup)

    df_reviews = pd.DataFrame(reviews)
    df_reviews.to_csv(output_csv, index=False, encoding='utf-8')

    logging.info(f"Scraped {len(df_reviews)} reviews and saved to {output_csv}")

    driver.quit()

# URL of the Google Maps place
url = 'https://www.google.com/maps/place/Coast/@49.2847519,-123.1230777,17z/data=!3m1!5s0x5486718052622a71:0x8e5068a555707078!4m8!3m7!1s0x5486718052c4c0fd:0x403b5fb55a4b8508!8m2!3d49.2847519!4d-123.1230777!9m1!1b1!16s%2Fm%2F04_j3cp?entry=ttu'

# Create the filename using the formatted date
output_csv = f'coast_restaurant_reviews_{formatted_today}.csv'

# Run the scraping function
scrape_reviews(url, output_csv)

df = pd.read_csv(f'coast_restaurant_reviews_{formatted_today}.csv')

df = df[
    (df['Star Rating'] != 'No rating')
]

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Function to calculate the exact date of the review
def calculate_review_date(time_since, today):
    if 'minute' in time_since:
        minutes_ago = int(time_since.split()[0]) if time_since[0].isdigit() else 1
        return (today - timedelta(minutes=minutes_ago)).strftime('%Y-%m-%d')
    elif 'hour' in time_since:
        hours_ago = int(time_since.split()[0]) if time_since[0].isdigit() else 1
        return (today - timedelta(hours=hours_ago)).strftime('%Y-%m-%d')
    elif 'day' in time_since:
        days_ago = int(time_since.split()[0]) if time_since[0].isdigit() else 1
        return (today - timedelta(days=days_ago)).strftime('%Y-%m-%d')
    elif 'week' in time_since or 'month' in time_since or 'year' in time_since:
        return float('nan')
    else:
        return float('nan')

# Load the scraped data
df = pd.read_csv(f'coast_restaurant_reviews_{formatted_today}.csv')
df = df[(df['Star Rating'] != 'No rating')]

df['Date Of Review'] = df['Time Since Review'].apply(lambda x: calculate_review_date(x, today))

# Function to calculate the start of the week (Sunday) for a given date
def get_week_start(date):
    return date - timedelta(days=date.weekday() + 1) if date.weekday() != 6 else date

# Define the date range calculation function that returns the week range or month name
def calculate_time_period(time_since, today):
    if 'minute' in time_since:
        minutes_ago = int(time_since.split()[0]) if time_since[0].isdigit() else 1
        review_date = today - timedelta(minutes=minutes_ago)
    elif 'hour' in time_since:
        hours_ago = int(time_since.split()[0]) if time_since[0].isdigit() else 1
        review_date = today - timedelta(hours=hours_ago)
    elif 'day' in time_since:
        days_ago = int(time_since.split()[0]) if time_since[0].isdigit() else 1
        review_date = today - timedelta(days=days_ago)
    elif 'week' in time_since:
        weeks_ago = int(time_since.split()[0]) if time_since[0].isdigit() else 1
        review_date = today - timedelta(weeks=weeks_ago)
    elif 'month' in time_since:
        months_ago = int(time_since.split()[0]) if time_since[0].isdigit() else 1
        review_date = today.replace(day=1) - timedelta(days=30 * months_ago)
        return review_date.strftime('%B')
    elif 'year' in time_since:
        years_ago = int(time_since.split()[0]) if time_since[0].isdigit() else 1
        review_date = today.replace(month=1, day=1) - timedelta(days=365 * years_ago)
        return review_date.strftime('%Y')
    else:
        return "Unknown"
    
    # Get the start of the week (Sunday)
    week_start = get_week_start(review_date)
    week_end = week_start + timedelta(days=6)
    return f"{week_start.strftime('%d-%b-%Y')} to {week_end.strftime('%d-%b-%Y')}"

# Apply the time period calculation to the 'Time Since Review' column to create the 'Time Period' column
df['Time Period'] = df['Time Since Review'].apply(lambda x: calculate_time_period(x, today))


# Check if an entry is a valid list representation
def is_list_representation(s):
    try:
        return isinstance(ast.literal_eval(s), list)
    except (ValueError, SyntaxError):
        return False

# Convert valid string representations to lists
df['Additional Info'] = df['Additional Info'].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) and is_list_representation(x) else x)

# Define columns
columns = [
    'Service type',
    'Meal type',
    'Price per person',
    'Food',
    'Service', 
    'Atmosphere',
    'Recommended dishes',
    'Parking space',
    'Parking options',
    'Kid-friendliness'
]

# Initialize the columns in the DataFrame
# Initialize the columns in the DataFrame with None (empty)
for col in columns:
    df[col] = None  

# Function to parse additional info
def parse_additional_info(row):
    if isinstance(row['Additional Info'], list):
        info_list = row['Additional Info']
        idx = 0
        while idx < len(info_list):
            if info_list[idx] == 'Service' and (idx + 1 < len(info_list) and not info_list[idx + 1].startswith('Service:')):
                row['Service type'] = info_list[idx + 1] if idx + 1 < len(info_list) else None
                idx += 2
            elif info_list[idx] == 'Meal type':
                row['Meal type'] = info_list[idx + 1] if idx + 1 < len(info_list) else None
                idx += 2
            elif info_list[idx] == 'Price per person':
                row['Price per person'] = info_list[idx + 1] if idx + 1 < len(info_list) else None
                idx += 2
            elif 'Food:' in info_list[idx]:
                row['Food'] = info_list[idx].split(':')[1] if ':' in info_list[idx] else None
                idx += 1
            elif 'Service:' in info_list[idx]:
                row['Service'] = info_list[idx].split(':')[1] if ':' in info_list[idx] else None
                idx += 1
            elif 'Atmosphere:' in info_list[idx]:
                row['Atmosphere'] = info_list[idx].split(':')[1] if ':' in info_list[idx] else None
                idx += 1
            elif info_list[idx] == 'Recommended dishes':
                row['Recommended dishes'] = info_list[idx + 1] if idx + 1 < len(info_list) else None
                idx += 2
            elif info_list[idx] == 'Parking space':
                row['Parking space'] = info_list[idx + 1] if idx + 1 < len(info_list) else None
                idx += 2
            elif info_list[idx] == 'Parking options':
                row['Parking options'] = info_list[idx + 1] if idx + 1 < len(info_list) else None
                idx += 2
            elif info_list[idx] == 'Kid-friendliness':
                row['Kid-friendliness'] = info_list[idx + 1] if idx + 1 < len(info_list) else None
                idx += 2
            else:
                idx += 1
    return row

# Apply the parsing function to the DataFrame
df = df.apply(parse_additional_info, axis=1)

df.drop('Additional Info', axis=1, inplace=True)

df.to_csv(f'coast_restaurant_reviews_{formatted_today}.csv', index=False, encoding='utf-8')

# Log the completion of the process with review count and column names
logging.info(f"Process completed. The CSV file '{output_csv}' contains {len(df)} reviews.")
logging.info(f"Columns in the CSV file: {', '.join(df.columns)}")

##### Preprocessing #######

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

logging.info("Starting preprocessing step...")


# Get today's date and format it
today = datetime.date.today()
formatted_today = today.strftime("%Y%m%d")  # Format as YYYYMMDD

df_1 = pd.read_csv('detailed_scrape_master.csv')
df_2 = pd.read_csv(f'coast_restaurant_reviews_{formatted_today}.csv')

df = pd.concat([df_2, df_1], ignore_index=True)

df_cleaned = df.drop_duplicates('Review Text', keep='first')

# Reset the index if needed
df_cleaned.reset_index(drop=True, inplace=True)

df_cleaned.to_csv(f'detailed_scrape_master.csv', index=False, encoding='utf-8')

df = pd.read_csv('detailed_scrape_master.csv')

# Convert score columns to numeric
df['Food'] = pd.to_numeric(df['Food'], errors='coerce')
df['Service'] = pd.to_numeric(df['Service'], errors='coerce')
df['Atmosphere'] = pd.to_numeric(df['Atmosphere'], errors='coerce')

df.drop(columns=['Kid-friendliness'], inplace=True)


# Define your staff lists and misspelling map
servers = ['andrea', 'andrew', 'ben', 'ben r', 'ben w',
           'betty', 'blaine', 'brad', 'brooke', 'caili',
           'carmen', 'chris', 'gloria', 'isabel',
           'isabella', 'jacob', 'jesse', 'jess', 'josh', 'khalil',
           'laura', 'michael', 'peter',
           'rhonda', 'sallie', 'sam', 'stephen', 'vinny']

bar = ['chrissy', 'chung', 'oscar', 'pavlo', 'rafael', 'ryan', 'aimée', 'jayson']

managers = ['abhi', 'franklin', 'katya', 'mohit', 'murat', 'natasha', 'lindsay']

host = ['anna', 'caren', 'lotty', 'megan', 'nicole', 'sharen']

events = ['emma jo', 'selina']

all_staff = servers + bar + managers + host + events

misspelling_map = {
    'abby': 'abhi',
    'abbi': 'abhi',
    'abi': 'abhi',
    'aby': 'abhi',
    'aimee': 'aimée',
    'ami': 'aimée',
    'ben royals': 'ben r',
    'ben royles': 'ben r',
    'ben ward': 'ben w',
    'benw' : 'ben w',
    'blain': 'blaine',
    'blonde ben': 'ben w',
    'blond ben': 'ben w',
    'bradley': 'brad',
    'brook': 'brooke',
    'cali': 'caili',
    'chris': 'chris',
    'chrissy': 'chrissy',
    'emma-jo': 'emma jo',
    'isobel': 'isabel',
    'isabelle': 'isabel',
    'jessica': 'jess',
    'joshua': 'josh',
    'katja' : 'katya',
    'katia' : 'katya',
    'halil': 'khalil',
    'khalel': 'khalil',
    'khalil': 'khalil',
    'launa': 'laura',
    'lindsey': 'lindsay',
    'michael m': 'michael',
    'michele': 'michael',
    'paulo': 'pavlo',
    'pablo': 'pavlo',
    'raf': 'rafael',
    'sally': 'sallie',
    'stefan': 'stephen',
    'stephan': 'stephen',
    'stephans': 'stephen',
    'tash': 'natasha',
}

# Apply normalize_text function to normalize the 'Review Text' column
def normalize_text(text):
    # Convert text to lowercase
    text = text.lower()

    # Remove possessive 's (e.g., "Gloria's" → "Gloria", "Ben's" → "Ben")
    text = re.sub(r"\b(\w+)'s\b", r'\1', text)
    # This will also remove cases like: "dog's" → "dog"

    # Remove all non-word characters except spaces (to keep names with dots, e.g., ben.w)
    text = re.sub(r'[^\w\s.]', '', text)
    
    return text

df['Normalized Reviews'] = df['Review Text'].apply(normalize_text)

def map_misspellings(text):
    for misspelling, correct_name in misspelling_map.items():
        pattern = r'\b' + re.escape(misspelling) + r'\b'
        text = re.sub(pattern, correct_name, text)
    return text

import re

def extract_names(mapped_text):
    if not isinstance(mapped_text, str):
        return []

    # Apply misspelling corrections (map any misspelled names to their correct form)
    mapped_text = map_misspellings(mapped_text)

    # Initialize a set to store unique staff names
    mentioned_names = set()

    # Check for exact matches in staff lists, allowing for optional possessive 's
    for name in all_staff:
        # Look for the name with or without an 's' at the end (e.g., "Gloria's" or "Gloria")
        pattern = r'\b' + re.escape(name) + r"'?s?\b"
        if re.search(pattern, mapped_text):
            mentioned_names.add(name)

    # Handle edge cases like "laura b" and "ben w" that should be treated specifically
    if 'ben w' in mapped_text:
        mentioned_names.add('ben w')

    # Ensure no duplicate generic names when specific ones are found (like "laura" should be removed if "laura b" is found)
    if 'ben w' in mentioned_names:
        mentioned_names.discard('ben')

    # Return the list of names mentioned or 'No Name Mentioned' if none were found
    return list(mentioned_names) if mentioned_names else ['No Name Mentioned']

df['Names Mentioned'] = df['Normalized Reviews'].apply(extract_names)

# Food items set
menu_items = [
    "Oysters", "Prawn Cocktail", "Seafood Tower", "Brioche", "Crab Cake", "Calamari", 
    "Mussels", "Carpaccio", "Pacific Octopus", "Salmon Flatbread", "Mushroom Flatbread", 
    "Chowder", "Velouté", "bisque", "Burrata Salad", "Caesar Salad", "Cobb Salad", "Beets Salad", 
    "Fish & Chip Cones","sushi", "California Roll", "King Salmon Roll", "Tuna Roll", "A5 Wagyu Roll", 
    "Sablefish Oshi", "Dynamite Roll", "Hamachi", "Masunosuke", "Amaebi", "A5 Wagyu", "Hotate", 
    "Shiro Maguro", "Tako", "Uni", "Hon Maguro", "Otoro", "Madai", "Nigiri Platter", "Sashimi Platter", 
    "King Salmon", "Sablefish", "Branzino", "Scallops", "Seafood Linguine", "Fish & Chips", 
    "Lobster Roll", "Steak", "Burger", "Roasted Chicken", "Poke Bowl", "Milanese", "Sole Piccata", 
    "Vongole", "Truffle Fries", "Grilled Broccolini", "Brussels Sprouts", "Banana Cake", 
    "Creme Brulee", "Chocolate Mint Cake", "Cheesecake", "Raspberry Cake", "Creme Puff", 
    "Crab Dip", "Hamachi Crudo", "Salmon Oshi", "Negitoro Hand Roll", "Lobster Roll"
]

# List of specific menus to check
menu_keywords = [
    "brunch", "lunch", "happy hour", "dinner", "valentines", "set menu", "lobster night", "buy up"
]

# Define abbreviations
menu_abbreviations = {
    "hh": "happy hour"
}

def extract_food_mentions_fuzzy(review_text, threshold=80):
    found_items = set()
    found_menus = set()

    # Normalize abbreviations (e.g., "hh" -> "happy hour")
    for abbreviation, full_menu in menu_abbreviations.items():
        review_text = review_text.lower().replace(abbreviation, full_menu)

    # Tokenize review into potential food words
    words = re.findall(r'\b\w+\b', review_text.lower())  # Extract words
    
    # Check for food items
    for word in words:
        match, score, _ = process.extractOne(word, menu_items, scorer=fuzz.ratio)  # Use fuzz.ratio for better matching
        if score >= threshold:  # Higher threshold means stricter matching
            found_items.add(match)
    
    # Check for specific menu mentions
    for menu in menu_keywords:
        if menu in review_text.lower():  # Check if the menu keyword is in the review
            found_menus.add(menu)
    
    return list(found_items), list(found_menus)

# Apply the function to the 'review_text' column and create new columns
df[['Food Mentions', 'Menu Mentions']] = df['Review Text'].apply(lambda x: pd.Series(extract_food_mentions_fuzzy(x)))

# Define standardization mapping
merge_dict = {
    "wagyu beef carpaccio": "carpaccio",
    "beef carpaccio": "carpaccio",
    "oysters on the half shell and lemon drop": "oysters",
    "new england clam chowder": "chowder",
    "mussels & clams": "mussels",
    "mussels and clams": "mussels",
    "coast tower": "seafood tower",
    "fish and chip cones" : "Fish & Chip Cones",
    "fish and chips" : "Fish & Chips",
    "warm banana & coconut butter cake & creme brulee" : "Butter Cake & Creme Brulee",
    "creme" : "Butter Cake & Creme Brulee"
}

# Clean and prepare the recommended dishes list
df['Recommended dishes'] = df['Recommended dishes'].fillna('')  # Handle NaN values

# Apply merge_dict mapping to standardize dish names
df['Recommended dishes'] = df['Recommended dishes'].apply(lambda x: [
    merge_dict.get(dish.strip().lower(), dish.strip().lower()) for dish in x.split(',') if dish
])

topics = {
    'Service': [
        'server', 'service', 'fast', 'experience', 'friendly', 'attentive', 'helpful', 'waiter', 'waitress'
    ],
    'Food': [
        'delicious', 'tasty', 'food', 'tasted', 'order', 'ordered', 'flavor', 'pairing', 'sushi', 'meal'
    ],
    'Positive': [
        'great', 'good', 'amazing', 'superb', 'fantastic', 'excellent', 
        'wonderful', 'thank', 'highly', 'recommend', 'best', 'impeccable', 'awesome',
        'courteous', 'professional', 'phenomenal', 'outstanding'
    ],
    'Negative': [
        'poor', 'slow', 'terrible', 'awful', 'bad', 'disgusting', 'dissapointing', 'mediocre'
    ]
}

# Double negatives phrases
double_negatives = ['not bad', 'not good', 'not great']

# Function to categorize reviews based on topic keywords
def assign_themes(text, topics):
    themes = []
    
    # Convert the text to lowercase to make the search case-insensitive
    text_lower = text.lower()
    
    # Check for double negatives and adjust sentiment
    if any(neg_phrase in text_lower for neg_phrase in double_negatives):
        # If double negative, treat as positive
        themes.append('Positive')
    else:
        # Check for positive and negative keywords
        for theme, keywords in topics.items():
            if any(word in text_lower for word in keywords):
                if theme != 'Negative' or 'Positive' in themes:  # Ensure no double counting
                    themes.append(theme)
                
    return themes

# Apply the function to create the 'Theme' column
df['Theme'] = df['Normalized Reviews'].apply(lambda x: assign_themes(x, topics))

# Capitalize the first letter of each word in each dish in the 'Recommended dishes' list
df['Recommended dishes'] = df['Recommended dishes'].apply(lambda dishes: [dish.title() for dish in dishes])

# Capitalize the first letter of each word in each menu mention in the 'Menu Mentions' list
df['Menu Mentions'] = df['Menu Mentions'].apply(lambda mentions: [mention.title() for mention in mentions])

# Create a new column for tags by combining extracted food and menu mentions without duplicates
df['Tags'] = df.apply(lambda row: list(set(row['Food Mentions']) | set(row['Recommended dishes']) | set(row['Menu Mentions'])), axis=1)


# Adding a reversed index
df_exploded = df.copy()

# Reverse the DataFrame, create a new index, then reverse it back
df_exploded['Reversed Index'] = range(len(df_exploded), 0, -1)

# Explode the 'Tags' column so each name has its own row
df_exploded = df_exploded.explode('Tags')

# Explode the 'Names Mentioned' column so each name has its own row
df_exploded = df_exploded.explode('Names Mentioned')

# Explode the 'Theme' column so each name has its own row
df_exploded = df_exploded.explode('Theme')

# Explode the 'Menu Mentions' column so each name has its own row
df_exploded = df_exploded.explode('Menu Mentions')

# Create a dictionary to map text to numerical values
star_rating_map = {
    '5 stars': 5,
    '4 stars': 4,
    '3 stars': 3,
    '2 stars': 2,
    '1 star': 1
}

# Replace the values in the 'Star Rating' column with numerical values
df_exploded['Star Rating'] = df_exploded['Star Rating'].replace(star_rating_map)

# Convert the 'Date of Review' column to datetime format
df_exploded['Date Of Review'] = pd.to_datetime(df_exploded['Date Of Review'], errors='coerce')

# Save the resulting DataFrame to a CSV file
df_exploded.to_csv('Review_dashboard_export.csv')


logging.info("Preprocessing step completed.")

# Wait for 30 seconds before closing
time.sleep(15)