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

Maintainer: Ahmad Deeb (ahmaddeebdev@gmail.com)
Status: Development
"""

import os
import re
import time
import logging
import requests
from bs4 import BeautifulSoup
from typing import Optional, List, Dict
from urllib.parse import urljoin, unquote, urlparse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scraper.log'),
        logging.StreamHandler()
    ]
)

# Standard headers for web requests
DEFAULT_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
    'Accept-Language': 'en-US,en;q=0.9',
}

def scrape_page(
    url: str,
    headers: dict = DEFAULT_HEADERS,
    timeout: int = 10,
    parser: str = 'html.parser'
) -> Optional[BeautifulSoup]:
    """
    Fetches and parses a web page into a BeautifulSoup object with robust logging.

    Args:
        url: Complete URL to scrape (must include scheme)
        headers: Dictionary of HTTP headers (default: browser-like headers)
        timeout: Request timeout in seconds (default: 10)
        parser: BeautifulSoup parser to use (default: 'html.parser')

    Returns:
        BeautifulSoup object if successful, None if failed

    Examples:
        >>> soup = scrape_page("https://example.com")
        >>> if soup:
        ...     print(soup.title.text)
    """
    try:
        logging.info(f"Requesting URL: {url}")
        response = requests.get(
            url,
            headers=headers,
            timeout=timeout
        )
        response.raise_for_status()

        logging.debug(f"Response received: {response.status_code}")
        soup = BeautifulSoup(response.text, parser)
        logging.info("Page successfully parsed")
        return soup

    except requests.exceptions.Timeout:
        logging.error(f"Request timed out after {timeout} seconds: {url}")
    except requests.exceptions.HTTPError as e:
        logging.error(f"HTTP {e.response.status_code} error: {url}")
    except requests.exceptions.ConnectionError:
        logging.error(f"Connection failed: {url}")
    except requests.exceptions.RequestException as e:
        logging.error(f"Request failed: {e}")
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}", exc_info=True)

    return None

def extract_images_urls(url: str, soup: BeautifulSoup) -> List[Dict[str, str]]:
    """
    Extracts all image information from a BeautifulSoup parsed page and returns structured data.
    
    Processes both absolute and relative image URLs, handles multiple source attributes (src/data-src),
    and provides comprehensive logging. Automatically resolves relative URLs to absolute paths.

    Args:
        url: The base URL of the page being scraped (used to resolve relative URLs)
        soup: Parsed BeautifulSoup object containing the HTML content

    Returns:
        List of dictionaries containing image details with keys:
        - 'url': Absolute image URL
        - 'alt': Alt text (empty string if not present)
        - 'page_url': Source page URL
        - 'position': Index position on page

    Raises:
        TypeError: If input arguments are invalid
        ValueError: If URL resolution fails

    Examples:
        >>> soup = BeautifulSoup(html_content, 'html.parser')
        >>> images = extract_images("https://example.com", soup)
        >>> for img in images:
        ...     print(f"Found image: {img['url']}")
    """
    # Input validation
    if not isinstance(url, str):
        logging.error("URL must be a string")
        raise TypeError("URL must be a string")
    if not isinstance(soup, BeautifulSoup):
        logging.error("soup must be a BeautifulSoup object")
        raise TypeError("soup must be a BeautifulSoup object")

    images = soup.find_all('img')
    if not images:
        logging.info(f"No images found on page {url}")
        return []

    logging.info(f"Found {len(images)} images on page {url}")
    image_data = []

    for i, img in enumerate(images, 1):
        try:
            img_url = img.get('src') or img.get('data-src') or img.get('data-lazy-src')
            alt_text = img.get('alt', '').strip()
            
            if not img_url:
                logging.debug(f"Image {i} has no source URL")
                image_data.append({
                    'position': i,
                    'url': None,
                    'alt': alt_text,
                    'page_url': url
                })
                continue

            # Resolve relative URLs
            if not img_url.startswith(('http', 'https')):
                img_url = urljoin(url, img_url)

            logging.debug(f"Processed image {i}: {img_url}")
            
            image_data.append({
                'position': i,
                'url': img_url,
                'alt': alt_text,
                'page_url': url
            })

        except Exception as e:
            logging.error(f"Error processing image {i}: {str(e)}")
            continue

    return image_data

def download_image(
    url: str,
    headers: dict = DEFAULT_HEADERS,
    save_dir: str = "downloads",
    timeout: int = 30,
    chunk_size: int = 1024,
    retries: int = 2,
    custom_filename: str = None
) -> str:
    """
    Downloads an image from a URL and saves it with its original filename or custom name.
    Automatically extracts filename from URL if not specified.

    Args:
        url: Complete URL of the image to download
        headers: Dictionary of HTTP headers (default: browser-like headers)
        save_dir: Directory to save images (default: 'downloads')
        timeout: Request timeout in seconds (default: 30)
        chunk_size: Chunk size for streaming download in bytes (default: 1024)
        retries: Number of retry attempts for failed downloads (default: 2)
        custom_filename: Optional custom filename without extension (default: None)

    Returns:
        str: Full path to downloaded image if successful, None if failed

    Raises:
        ValueError: If URL is invalid or filename contains illegal characters
        OSError: If directory creation or file writing fails

    Examples:
        >>> # Automatic filename extraction
        >>> path = download_image("https://example.com/images/photo.jpg")
        
        >>> # With custom filename
        >>> path = download_image(url, custom_filename="vacation")
    """
    # Input validation
    if not url.startswith(('http://', 'https://')):
        logging.error(f"Invalid URL protocol: {url}")
        raise ValueError("URL must start with http:// or https://")

    # Create save directory if needed
    os.makedirs(save_dir, exist_ok=True)

    # Extract filename from URL if not provided
    if custom_filename:
        filename = custom_filename
    else:
        # Decode URL-encoded characters and extract filename
        parsed = urlparse(unquote(url))
        filename = os.path.basename(parsed.path)
        
        # Remove query parameters if present
        filename = filename.split('?')[0]
        
        # Generate default name if URL doesn't contain one
        if not filename or '.' not in filename:
            filename = f"image_{int(time.time())}"

    # Clean filename
    filename = re.sub(r'[\\/*?:"<>|]', "_", filename)
    
    # Determine file extension
    file_ext = os.path.splitext(filename)[1].lower()
    if not file_ext:
        # Try to get extension from content type if missing
        try:
            with requests.head(url, timeout=5, headers=headers) as response:
                content_type = response.headers.get('content-type', '')
                if content_type.startswith('image/'):
                    file_ext = f".{content_type.split('/')[1].split(';')[0]}"
        except:
            file_ext = '.jpg'  # Default fallback

    # Ensure filename has extension
    if not file_ext:
        file_ext = '.jpg'
    elif file_ext not in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
        file_ext = '.jpg'  # Force valid image extension

    base_name = os.path.splitext(filename)[0]
    full_filename = f"{base_name}{file_ext}"
    full_path = os.path.join(save_dir, full_filename)

    # Download with retry logic
    for attempt in range(retries + 1):
        try:
            logging.info(f"Download attempt {attempt + 1} for {url}")
            with requests.get(
                url,
                headers=headers,
                timeout=timeout,
                stream=True
            ) as response:
                response.raise_for_status()

                # Verify content is actually an image
                content_type = response.headers.get('content-type', '')
                if not content_type.startswith('image/'):
                    logging.error(f"URL does not point to an image: {url}")
                    return None

                # Stream download to file
                with open(full_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=chunk_size):
                        if chunk:
                            f.write(chunk)

                logging.info(f"Successfully downloaded: {full_path}")
                return full_path

        except requests.exceptions.RequestException as e:
            logging.warning(f"Attempt {attempt + 1} failed: {str(e)}")
            if attempt == retries:
                logging.error(f"All download attempts failed for {url}")
                return None
            time.sleep(2 ** attempt)  # Exponential backoff

    return None