import os
import time
import requests
from datetime import datetime
import yaml
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime

# Load config from YAML
with open("config.yaml", "r") as config_file:
    config = yaml.safe_load(config_file)

GOOGLE_NEWS_URL = config["google_news_url"]
TOP_STORIES_ID = config["top_stories_id"]

def get_top_stories():
    """Scrape top stories from Google News."""
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    driver = webdriver.Chrome(options=options)

    driver.get(GOOGLE_NEWS_URL)
    driver.find_element(By.ID,TOP_STORIES_ID ).click()
    time.sleep(2)
    
    storyTags = driver.find_elements(By.TAG_NAME, "c-wiz")

    data = []
    storyCount = 0
    image_folder = "news_Thumbnails"
    os.makedirs(image_folder, exist_ok=True)
    for storytag in storyTags:
        if storytag.get_attribute("class") == "PO9Zff Ccj79 kUVvS":
            storyCount += 1
            imageFile = None
            imagesInside = storytag.find_elements(By.TAG_NAME, "img")
            for imageInside in imagesInside:
                if imageInside.get_attribute("class") == "Quavad vwBmvb":
                    img_url = imageInside.get_attribute("src")
                    if img_url:
                            try:
                                # Download and save the image
                                response = requests.get(img_url, stream=True)
                                if response.status_code == 200:
                                    image_filename = os.path.join(image_folder, f"news_{storyCount}.jpg")
                                    with open(image_filename, "wb") as img_file:
                                        img_file.write(response.content)
                                    imageFile = image_filename  # Store file path
                            except Exception as e:
                                print(f"Error downloading image: {e}")
            headlineText = None
            try:
                headlineText = WebDriverWait(storytag, 5).until(EC.presence_of_element_located((By.CLASS_NAME, "gPFEn"))).text
            except Exception as e:
                print("")
            try:
                # Extract article URL
                article_url = storytag.find_element(By.TAG_NAME, "a").get_attribute("href")
            except Exception as e:
                print("Error retrieving article URL.")

            try:
                # Extract article date (assuming it's available in a 'time' tag or similar)
                article_date = storytag.find_element(By.TAG_NAME, "time").get_attribute("datetime")
            except Exception as e:
                print("Error retrieving article date.")
                

            metadata = {
                "headline": headlineText,
                "image": imageFile,
                "url": article_url,
                "scrape_time": datetime.now().strftime("%H:%M:%S  %Y-%m-%d"),
                "article_date": article_date,
                "story_count": storyCount
            }

            # Append metadata to data list
            
            data.append(metadata)
            #lazyloading 
            driver.execute_script("window.scrollBy(0, 1000);")
            time.sleep(2)  
    return data


