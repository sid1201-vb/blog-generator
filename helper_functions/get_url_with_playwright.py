from playwright.sync_api import sync_playwright


def web_search_topic(text: str):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        # Go to Google
        page.goto("https://www.bing.com")

        # Accept cookies if prompted
        try:
            page.click('button[jsname="V67aGc"]', timeout=2000)
        except:
            pass

        # Enter search query in the text area and press Enter
        keyword = text
        page.fill('textarea[name="q"]', keyword)
        page.press('textarea[name="q"]', "Enter")

        # Wait for results to load
        page.wait_for_selector('h2 > a')

        # Collect top 5 search result URLs
        urls = []
        results = page.query_selector_all('h2 > a')

        for result in results[:2]:  # Limit to top 5 results
            urls.append(result.get_attribute('href'))

        browser.close()


        # Print results
        print("Top 5 Search Results:")
        for url in urls:
            print(url)
        return urls



def get_url_list(search_phrases:list[str])->list[str]:
    all_urls = []
    for phrase in search_phrases:
        urls = web_search_topic(phrase)
        all_urls = all_urls + urls

    return all_urls
