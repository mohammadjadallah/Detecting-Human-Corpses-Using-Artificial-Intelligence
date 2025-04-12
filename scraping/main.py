#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
FILE: main.py
DESCRIPTION: Extracts and processes images from web pages using BeautifulSoup
AUTHOR: Ahmad Deeb
CREATED: 11/04/2025
LAST MODIFIED: 11/04/2025
VERSION: 0.1.0
PYTHON VERSION: 3.10+

Copyright (c) 2025 Ahmad Deeb. All rights reserved.

Licensed under the MIT License (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    https://opensource.org/licenses/MIT

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

Dependencies:
- beautifulsoup4==4.13.3
- certifi==2025.1.31
- charset-normalizer==3.4.1
- idna==3.10
- requests==2.32.3
- soupsieve==2.6
- typing_extensions==4.13.2
- urllib3==2.4.0

Maintainer: Nabegh Sayegh (Na-sayegh@hotmail.com)
Status: Development
"""
"""
IMAGE SCRAPER FOR DOCUMENTATION WEBSITE

This script systematically scrapes images from a specific documentation website
by iterating through paginated content. It handles page scraping, image extraction,
and downloading with error handling.

Main Components:
- Page scraping with BeautifulSoup
- Image URL extraction
- Batch downloading with pagination
- Error handling and logging

Note: Ensure compliance with website terms of service before use.
"""

from core import *
import logging

# Base URL for the documentation website
base_url = "https://safmcd.com/martyr/index.php?id=2"

'''
https://safmcd.com/martyr/category.php
'''
def scrape_images(url: str) -> None:
    """
    Scrapes all images from a given URL and downloads them locally.
    
    The function:
    1. Fetches and parses the webpage
    2. Extracts all image URLs
    3. Downloads each image to local storage
    
    Args:
        url (str): Complete URL of the page to scrape images from
        
    Returns:
        None: Downloads images as side effect
        
    Raises:
        Silently handles and logs errors without raising exceptions
        
    Example:
        >>> scrape_images("https://leaks.zamanalwsl.net/tortures.php?id=&start=1")
        [Downloads all images from page 1]
    """
    try:
        # Scrape and parse the webpage
        soup = scrape_page(url)
        
        if soup:
            # Extract all image URLs from parsed HTML
            imgs_urls = extract_images_urls(url, soup)
            
            # Download each image found
            for image in imgs_urls:
                if image['url']:
                    download_image(image['url'])
    except Exception as e:
        logging.error(f"Error scraping {url}: {str(e)}")

if __name__ == "__main__":
    """
    Main execution block that runs the scraper across multiple pages.
    
    Iterates through paginated content,
    scraping images from each page sequentially.
    """
    # Configure basic logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('scraper.log'),
            logging.StreamHandler()
        ]
    )
    
    logging.info("Starting image scraping process")
    
    # Iterate through 54 pages of content
    for i in range(2, 55):
        try:
            # Construct paginated URL
            url = f'{base_url}?id=&start={i}'
            logging.info(f"Processing page {i}: {url}")
            
            # Scrape images from current page
            scrape_images(url)
            
        except Exception as e:
            logging.error(f"Error processing page {i}: {str(e)}")
            continue
    
    logging.info("Scraping process completed")