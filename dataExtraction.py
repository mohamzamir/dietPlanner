# Import required libraries
import json  # For working with JSON data
import requests  # For making HTTP requests to fetch menu data
from datetime import datetime  # For handling dates

# Load the raw JSON data from file
# This contains menu links organized by location and meal categories
with open('updated_menu_links.json', 'r') as file:
    menu_data = json.load(file)

# Define allowed locations using a set for fast lookups
# These are the dining locations we want to include in our final output
allowed_locations = {
    "West Side Dining",
    "East Side Dining",
    "Jasmine",
    "Roth",
    "Student Activities Center"
}

# Filter the data to keep only specified locations
# Dictionary comprehension filters out unwanted locations
filtered_data = {k: v for k, v in menu_data.items() if k in allowed_locations}

# Get today's date in the format used by the menu URLs (YYYY/MM/DD)
today_date = datetime.now().strftime("%Y/%m/%d")


def update_date_in_url(url):
    """Replace the placeholder date in URLs with today's date.

    Args:
        url: Original URL string containing a placeholder date

    Returns:
        Updated URL string with current date
    """
    # The original URLs contain a static date that needs daily updating
    return url.replace("2025/02/10", today_date)


def fetch_and_process_menu(url):
    """Fetch and process menu data from a given URL.

    1. Makes HTTP GET request to menu API
    2. Extracts today's menu items
    3. Cleans and formats food items with calorie information

    Args:
        url: API endpoint URL to fetch menu data from

    Returns:
        Dictionary of {item_name: calories} or None if request fails
    """
    try:
        # Make HTTP GET request with timeout safety
        response = requests.get(url)

        # Check for successful response before processing
        if response.status_code == 200:
            data = response.json()
            menu_items = {}

            # Get today's date in the format used by the API (YYYY-MM-DD)
            today_str = datetime.now().strftime("%Y-%m-%d")

            # Search through days to find today's menu
            for day in data.get('days', []):
                if day.get('date') == today_str:
                    # Process each menu item in today's menu
                    for item in day.get('menu_items', []):
                        # Skip section headers and invalid entries
                        if not item.get('is_section_title') and item.get('food'):
                            food = item['food']

                            # Extract and clean food name
                            name = food.get('name', '').strip()

                            # Extract and round calorie count
                            calories = food.get('rounded_nutrition_info', {}).get('calories')

                            # Only add entries with valid names and calorie counts
                            if name and calories is not None:
                                menu_items[name] = int(round(calories))
                    break  # Exit loop after processing today's menu
            return menu_items
        return None
    except Exception as e:
        # Print error but continue processing other URLs
        print(f"Error processing {url}: {str(e)}")
        return None


def process_node(node):
    """Recursively process menu nodes to:
    1. Update URLs with current date
    2. Fetch and add calorie information

    Handles nested menu structure through recursion
    """
    if isinstance(node, dict):
        if 'url' in node:
            # Update the URL with current date
            node['url'] = update_date_in_url(node['url'])

            # Fetch and add menu items with calories
            # This is where we connect to external API
            menu_items = fetch_and_process_menu(node['url'])
            if menu_items:
                node['menu_items'] = menu_items
        else:
            # Recursively process nested dictionaries
            for key in node:
                process_node(node[key])


# Main processing pipeline
# Iterate through filtered locations and process their menu structures
for location in filtered_data.values():
    process_node(location)

# Save the enhanced data to new file
# Now contains both updated URLs and calorie information
with open('filtered_menu_with_calories.json', 'w') as file:
    json.dump(filtered_data, file, indent=4)

print("Filtered menu data updated successfully!")