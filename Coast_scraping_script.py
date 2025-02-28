import datetime
import logging
import pandas as pd
import ast
import time
from datetime import timedelta
from bs4 import BeautifulSoup
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