import json
import requests
from fastapi import FastAPI
from pydantic import BaseModel, conlist, conint
from typing import List

import base64
from PIL import Image
import io
import numpy as np
from botocore.exceptions import NoCredentialsError
import boto3
import random
import string
import os
from io import BytesIO
import time
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import concurrent.futures
import json
from flask import Flask, request, jsonify

app = Flask(__name__)

def search_url(search_term, page_number):
    template = f'https://www.myntra.com/scrape?rawQuery={search_term}&p={page_number}&sort=popularity'
    return template

def scrape_data(search_term):
    # Set up headless Chrome browser (optional)
    # chrome_options = webdriver.ChromeOptions()
    # chrome_options.add_argument("--headless")  # Run headless
    # chrome_options.add_argument("--disable-gpu")
    # chrome_options.add_argument("--no-sandbox")
    # chrome_options.add_argument("--disable-dev-shm-usage")

    # driver = webdriver.Chrome(options=chrome_options)
    driver = webdriver.Chrome()

    try:
        brands, prices, original_prices, descriptions, product_urls = [], [], [], [], []

        # Scraping only 1 page
        driver.get(search_url(search_term, 1))
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "product-brand"))
        )
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        # Scrape brand names (limiting to 5 products)
        brand_elements = soup.find_all('h3', class_="product-brand")[:1]
        brands.extend([brand.text for brand in brand_elements])

        # Scrape prices (limiting to 5 products)
        price_elements = soup.find_all('span', class_="product-discountedPrice")[:1]
        prices.extend([int(price.text.strip('Rs. ')) for price in price_elements])

        original_price_elements = soup.find_all('span', class_='product-strike')[:1]
        original_prices.extend([int(price.text.strip('Rs. ')) if price else None for price in original_price_elements])

        description_elements = soup.find_all('h4', class_='product-product')[:1]
        descriptions.extend([desc.text for desc in description_elements])

        li_elements = soup.find_all('li', class_="product-base")[:1]
        for item in li_elements:
            link = item.find('a', {'data-refreshpage': 'true', 'target': '_blank'})
            if link:
                href = 'http://myntra.com/' + link['href']
                product_urls.append(href)
            else:
                product_urls.append(None)

        # Return a dictionary for the current search term
        return {
            'products': [{
                'brand_name': brands[i],
                'price': prices[i],
                'original_price': original_prices[i],
                'description': descriptions[i],
                'product_url': product_urls[i]
            } for i in range(len(brands))]
        }

    finally:
        driver.quit()

def searchSKU(search_terms):
    start_time = time.time()

    # Run multiple scraping processes in parallel using ThreadPoolExecutor
    with concurrent.futures.ThreadPoolExecutor() as executor:
        # Submit scrape_data tasks for all search terms
        futures = [executor.submit(scrape_data, term) for term in search_terms]

        # Collect results as they complete
        results = [future.result() for future in concurrent.futures.as_completed(futures)]

    total_time = time.time() - start_time

    # Convert results to JSON format
    json_results = json.dumps({
        'total_time': total_time,
        'results': results
    }, indent=4)

    # Save to a file
    with open('scraped_products.json', 'w') as f:
        f.write(json_results)

    # Return the results with the time taken
    return json_results

def start_scraping(search_terms):
    # Expecting JSON input with a list of search terms
    # data = request.get_json()

    if not search_terms:
        return jsonify({"error": "Please provide search terms"}), 400

    # Perform the scraping with the provided search terms
    result = searchSKU(search_terms)
    return result



def generate_random_key(length=6):
    characters = string.ascii_letters + string.digits  # All letters (uppercase and lowercase) and digits
    return ''.join(random.choice(characters) for _ in range(length))

def upload_to_s3(local_file):
    s3 = boto3.client('s3',
        aws_access_key_id='Place_Holder',
        aws_secret_access_key='Place_Holder'
    )

    try:
        imageSuffix = generate_random_key()
        s3.upload_fileobj(local_file, 'dressify', f"/dressify_{imageSuffix}.png")
        s3Url = f'https://dressify.s3.amazonaws.com//dressify_{imageSuffix}.png'
        return s3Url
    except FileNotFoundError:
        return "The file was not found"
    except NoCredentialsError:
        return "Credentials not available"


class InputData(BaseModel):
    prompt: str
    imageString: str
    # gender: str
    # location: str
    # dressing_preferences: str
    # season: str
    # occasion_purpose: str
    # body_type: str
    # wardrobe_items: str
    # color_preferences: str
    # budget: int

stream = False
app = FastAPI()
url = "https://proxy.tune.app/chat/completions"
headers = {
    "Authorization": "Place_Holder",
    "Content-Type": "application/json",
}

def decode_base64_image(base64_str):
    image_data = base64.b64decode(base64_str)
    file_obj = BytesIO(image_data)
    return file_obj


@app.post("/outfit/")
def suggest_outfit(requestBody: InputData):
  # print(requestBody.prompt)
  if (requestBody.imageString is not None):
    imageFile = decode_base64_image(requestBody.imageString)
    imageFinalURL = upload_to_s3(imageFile)
    #TODO: hit RAG to get data
    # if rag.data is not null do this else continue with below
  data = {
    "temperature": 0.8,
    "messages":  [
  {
    "role": "user",
    "content": [
      {
        "type": "text",
        "text": f"""
        1. You are Dressify, an AI dressing assistant for the Indian audience. Your task is to provide personalized dressing suggestions based on the user's preferences, body type, location, season, occasion, and wardrobe.
        2. Consider user input given below.
        3. Request: "{requestBody.prompt}"
        4. If image is not null extract out outfit of the given image.
        5. Note detailed granular details data of clothes and accessories that is available in the image.
        6. Consider details extracted to give suggestion.
        7. Either way, balance the attire to create a full and polished ensemble.
        8. If shoes or any other accessory can be recommended do that.
        9. In the output share only complete look details in granular manner.
        10. Return output in below format strictly. Do not send anything apart from below points in output value.
        10.1 Top Apparel
        10.2 Bottom Apparel
        10.3 Accessories, it's Color & Description
        10.4 Head Gear, it's Color & Description
        10.5 Footwear, it's Color & Description
        11. Do not return anything in output apart from search terms and recommendations.
        12. Enforce below sample to generate response:
        {{
           'recommendations': {{
            'top apparel': 'You already have a white shirt, so no additional suggestion is needed.',
            'bottom apparel': 'Navy Blue Formal Trousers',
            'accessories': 'Black Leather Blazer with a fitted silhouette, Simple Silver Watch with a leather strap',
            'head_gear': 'None',
            'footwear': 'Black Leather Dress Shoes with a sleek design and polished finish',
          }},
          'search_terms': []
          }}
        13. Replace all ' with " in response.
        14. Remove everything after the response object.
        15. Enforce sending only recommendation and search_terms and both keys are at same level in the json output.
        16. Generate search_terms according to suggesstions.
        IMPORTANT : Return response as JSON which should have above requested response, under no condition should the output format change
        """
      }
      # {
      #   "type": "image_url",
      #   "image_url": {
      #     "url": imageFinalURL
      #   }
      # }
    
    ]
  },
],
    "model": "meta/llama-3.2-90b-vision",
    "stream": stream,
    "frequency_penalty":  0,
    "max_tokens": 3000
  }
  response = requests.post(url, headers=headers, json=data)
  if stream:
      for line in response.iter_lines():
          if line:
              l = line[6:]
              if l != b'[DONE]':
                hash_map = {}
                hash_map["response"] = response.json(l)
                hash_map["metaData"] = extract_search_terms(json.loads(l))
                print(hash_map)
                return(hash_map)
  else:
    hash_map = {}
    hash_map["response"] = response.json()
    hash_map["metaData"] = extract_search_terms(response.json())
    print(hash_map)
    return hash_map


def extract_search_terms(response):
  print(response)
  content = response['choices'][0]['message']['content']

  start = content.index('{')
  end = content.rindex('}') + 1
  print(content)
  json_str = content[start:end]
  print(json_str)
  data = json.loads(json_str)
  print(data)

  search_terms = data['search_terms']
  print(f'search:{search_terms}')
  skuResult = start_scraping(search_terms)
  return skuResult



            #    "Gender: {data.gender}"
            #    "Location: {data.location}"
            #    "Dressing Preferences: {data.dressing_preferences}"
            #    "Season: {data.season} (e.g., spring, summer, monsoon, autumn, winter)"
            #    "Occasion/Purpose: {data.occasion_purpose} (e.g., casual wear, office, wedding, party, business meeting, sports)"
            #    "Body Type: {data.body_type} (e.g., slim, athletic, curvy, average)"
            #    "Wardrobe Items: {data.wardrobe_items} (List of user's clothing items that they want to style with, or specify new suggestions)"
            #    "Color Preferences: {data.color_preferences} (List any color or pattern preferences, or no preference)"
            #    "Budget: {data.budget} (If applicable: budget-friendly, mid-range, luxury)"
            #    """


