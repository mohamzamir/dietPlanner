import json
import asyncio
import time
from datetime import datetime
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

# Define the latest date to append to URLs
LATEST_DATE = datetime.now().strftime("%Y-%m-%d")


def append_date_to_url(url):
    if not url.endswith("/"):
        url += "/"
    return f"{url}{LATEST_DATE}"


async def fetch_content_with_playwright(url):
    """Fetch dynamically loaded content using playwright."""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        try:
            await page.goto(url, timeout=60000)  # Wait up to 60 seconds if needed
            # Wait for the target element to be available on the page
            await page.wait_for_selector("ul.menu-day.show-description.show-calories.show-icons", timeout=30000)

            # Get the page content after JavaScript has run
            content = await page.content()
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            content = None
        finally:
            await browser.close()

    return content


def parse_html(html_content):
    """Parse the HTML content to extract menu information."""
    if not html_content:
        return "No content available"

    soup = BeautifulSoup(html_content, "html.parser")
    menu_day_ul = soup.find("ul", class_="menu-day show-description show-calories show-icons")

    if not menu_day_ul:
        return "No menu found"

    menu_data = {}
    for li in menu_day_ul.find_all("li"):
        h3_tag = li.find("h3")
        if not h3_tag:
            continue

        key = h3_tag.get_text(strip=True)
        food_names = [
            span.get_text(strip=True)
            for span in li.find_all("span", class_="food-name")
        ]

        if key:
            menu_data[key] = food_names

    return menu_data


async def process_links(json_data):
    """Recursively process the JSON structure to fetch and parse content for each URL."""

    async def process_item(item):
        # If the item is a string that looks like a URL, fetch its content.
        if isinstance(item, str) and item.startswith("http"):
            url_with_date = append_date_to_url(item)
            html_content = await fetch_content_with_playwright(url_with_date)
            menu = parse_html(html_content)
            return {"url": url_with_date, "menu": menu}
        # Process dictionaries concurrently
        elif isinstance(item, dict):
            tasks = {key: asyncio.create_task(process_item(value)) for key, value in item.items()}
            results = {}
            for key, task in tasks.items():
                results[key] = await task
            return results
        # Process lists concurrently
        elif isinstance(item, list):
            tasks = [asyncio.create_task(process_item(value)) for value in item]
            return await asyncio.gather(*tasks)
        return item

    return await process_item(json_data)


def save_cleaned_json(json_data, filename):
    """Save the JSON with fetched content to a file."""
    with open(filename, "w", encoding="utf-8") as file:
        json.dump(json_data, file, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    start_time = time.time()
    input_file = "result.json"
    output_file = "fetched_data_with_date.json"

    with open(input_file, "r", encoding="utf-8") as file:
        json_data = json.load(file)

    # Run the asynchronous processing and save the fetched content
    fetched_data = asyncio.run(process_links(json_data))
    save_cleaned_json(fetched_data, output_file)
    print(f"Fetched data saved to {output_file}")

    end_time = time.time()
    execution_time = end_time - start_time
    print(f"Execution time: {execution_time:.6f} seconds")