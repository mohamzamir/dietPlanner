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

    # Make an HTTP GET request to the provided URL
    # This sends a request to the server to fetch the menu data
    response = requests.get(url)

    # Check if the request was successful by verifying the status code
    # A status code of 200 means the request was successful
    if response.status_code == 200:
        # Parse the response content as JSON
        # This converts the response into a Python dictionary for easy access
        data = response.json()

        # Initialize an empty dictionary to store today's menu items
        # This will hold the food items and their corresponding calorie counts
        menu_items = {}

        # Get today's date in the format used by the API (YYYY-MM-DD)
        # This ensures we only process menu items for the current day
        today_str = datetime.now().strftime("%Y-%m-%d")

        # Iterate through the 'days' key in the JSON data
        # Each 'day' represents a day's menu in the API response
        for day in data.get('days', []):
            # Check if the current day's date matches today's date
            if day.get('date') == today_str:
                # Iterate through the 'menu_items' key in the current day's data
                # Each 'item' represents a food item or a section header
                for item in day.get('menu_items', []):
                    # Skip items that are section headers or don't have food data
                    # Section headers are not actual food items and should be ignored
                    if not item.get('is_section_title') and item.get('food'):
                        # Extract the 'food' object from the item
                        # This contains details like the food name and nutrition info
                        food = item['food']

                        # Extract and clean the food name
                        # The 'name' key holds the food item's name, and we strip any extra spaces
                        name = food.get('name', '').strip()

                        # Extract the calorie count from the nutrition info
                        # The 'rounded_nutrition_info' key contains calorie data
                        calories = food.get('rounded_nutrition_info', {}).get('calories')

                        # Only add the item to the menu if it has a valid name and calorie count
                        # This ensures we don't include incomplete or invalid entries
                        if name and calories is not None:
                            # Add the food item to the menu_items dictionary
                            # The key is the food name, and the value is the rounded calorie count
                            menu_items[name] = int(round(calories))

                # Exit the loop after processing today's menu
                # No need to check other days since we've found today's data
                break

        # Return the dictionary of today's menu items with their calorie counts
        return menu_items

    # If the request was not successful (status code is not 200), return None
    # This indicates that the menu data could not be fetched
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
