import requests
from bs4 import BeautifulSoup
import os
import shutil

import re

def clean_md(content):
    """
    Cleans a markdown file by removing image links, hyperlinks, and embedded links.
    It overwrites the file with the cleaned content.
    
    :param file_path: Path to the markdown file.
    """
    
    # Remove image links ![alt text](image_url)
    content = re.sub(r'!\[.*?\]\(.*?\)', '', content)
    
    # Remove hyperlinks [text](url)
    content = re.sub(r'\[([^\]]+)\]\((.*?)\)', r'\1', content)
    
    # Remove raw URLs
    content = re.sub(r'http[s]?://\S+', '', content)
    
    # Remove excessive empty lines
    content = re.sub(r'\n{2,}', '\n\n', content)
    
    return content


import requests
from bs4 import BeautifulSoup

def fetch_webpage(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Raise an error for bad responses (4xx and 5xx)
        
        soup = BeautifulSoup(response.text, 'html.parser')
        page_content = soup.prettify()  # Stores the entire parsed HTML content
        
        return page_content
    except requests.exceptions.RequestException as e:
        print(f"Error fetching the webpage: {e}")
        return None
    
def save_webpages(url_list: list[str], blog_id: str) -> bool:
    if os.path.exists(blog_id):
        shutil.rmtree(blog_id)
    for i,url in enumerate(url_list):
        try:
            webpage_content = fetch_webpage("https://r.jina.ai//"+url)
            if webpage_content:  # Proceed if content was successfully fetched
                webpage_content = clean_md(content=webpage_content)
                os.makedirs(blog_id, exist_ok=True)
                with open(f"{blog_id}/{i}.md", "w", encoding="utf-8") as f:  # Open file in append mode
                    f.write(webpage_content)
            else:
                print(f"Skipping URL {url} due to fetch failure.")
        except Exception as e:
            print(f"An error occurred while processing {url}: {e}")
            continue  # Continue with the next URL even if one fails
    return True

