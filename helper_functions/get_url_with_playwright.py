import requests
import json
import dotenv
dotenv.load_dotenv()
import os 

api_key = os.getenv("SERPER_API_KEY")
def web_search_topic(text: str):
    """
    Search for a topic using Serper Dev API and return top search result URLs
    
    Args:
        text (str): Search query text
        api_key (str): Your Serper API key
    
    Returns:
        list: List of URLs from top search results
    """
    
    # Serper API endpoint
    url = "https://google.serper.dev/search"
    
    # Request payload
    payload = json.dumps({
        "q": text,
        "num": 5  # Number of results to return (can be up to 100)
    })
    
    # Request headers
    headers = {
        'X-API-KEY': api_key,
        'Content-Type': 'application/json'
    }
    
    try:
        # Make the API request
        response = requests.post(url, headers=headers, data=payload)
        response.raise_for_status()  # Raise an exception for bad status codes
        
        # Parse the response
        data = response.json()
        
        # Extract URLs from organic results
        urls = []
        if 'organic' in data:
            for result in data['organic'][:5]:  # Limit to top 5 results
                if 'link' in result:
                    urls.append(result['link'])
        
        # Print results
        print(f"Top {len(urls)} Search Results for: '{text}'")
        for i, url in enumerate(urls, 1):
            print(f"{i}. {url}")
        
        return urls
        
    except requests.exceptions.RequestException as e:
        print(f"Error making API request: {e}")
        return []
    except json.JSONDecodeError as e:
        print(f"Error parsing API response: {e}")
        return []
    except Exception as e:
        print(f"Unexpected error: {e}")
        return []


def get_url_list(search_phrases:list[str])->list[str]:
    all_urls = []
    for phrase in search_phrases:
        urls = web_search_topic(phrase)
        all_urls = all_urls + urls

    return all_urls
