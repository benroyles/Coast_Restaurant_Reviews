import pandas as pd
import numpy as np
import spacy
import string
from datetime import datetime, timedelta
from collections import Counter
import re
import datetime
from rapidfuzz import process, fuzz

import logging

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