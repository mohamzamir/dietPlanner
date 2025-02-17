from playwright.sync_api import sync_playwright
import re
import json

# Load JSON data from a file
with open('fetched_data_with_date.json', 'r') as file:
    json_data = json.load(file)

# List to store URLs from the JSON
all_menu_links = []

# Mapping of original menu links to API links or None if not found
link_replacements = {}

# Pattern for the required API URLs
url_pattern = re.compile(r"https://stonybrook\.api\.nutrislice\.com/menu/api/weeks/school/.*/2025/02/10/")

# Extract menu page links
def extract_links(data):
    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, dict):
                extract_links(value)
            elif key == "url" and isinstance(value, str):
                all_menu_links.append((key, value))

# Update JSON with new links
def update_json(data, replacements):
    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, dict):
                update_json(value, replacements)
            elif key == "url" and value in replacements:
                data[key] = replacements[value]  # Replace old link with new API link or None

# Extract initial menu links
extract_links(json_data)

# Visit menu links and find API links
with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)  # Show the browser window
    page = browser.new_page()

    def handle_request(request):
        if url_pattern.match(request.url):
            # Capture the first matching API link per page visit
            if link_replacements[current_link] is None:
                link_replacements[current_link] = request.url

    # Attach request handler
    page.on("request", handle_request)

    # Visit each menu link and search for the API link
    for key, menu_link in all_menu_links:
        current_link = menu_link
        link_replacements[menu_link] = None  # Default to None in case no link is found
        try:
            page.goto(menu_link, wait_until='networkidle')
        except Exception as e:
            print(f"Error visiting {menu_link}: {e}")

    browser.close()

# Update the JSON structure with new or None API links
update_json(json_data, link_replacements)

# Save the updated JSON to a new file
with open('updated_menu_links.json', 'w') as file:
    json.dump(json_data, file, indent=2)

# Output the mapping of old links to new API links or None
link_replacements