import requests
from datetime import datetime

# API URL
url = "https://stonybrook.api.nutrislice.com/menu/api/weeks/school/sac/menu-type/noodles/2025/02/10/"
# Perform GET request to fetch the JSON data
response = requests.get(url)

# Get today's date in the format as in the JSON response (e.g., "2025-02-10")
today_date = datetime.now().strftime("%Y-%m-%d")

# Parse the response if the request was successful
if response.status_code == 200:
    menu_data = response.json()

    # Collect food items only for today's date
    food_items = []
    for day in menu_data.get("days", []):
        if day.get("date") == today_date:  # Check for today's date
            for item in day.get("menu_items", []):
                food = item.get("food")
                if food and "name" in food:
                    food_items.append(food["name"])

    # Print the food items for today
    if food_items:
        print("Today's Food Items:")
        for food_item in food_items:
            print(f"- {food_item}")
    else:
        print("No food items found for today.")
else:
    print(f"Failed to fetch data. HTTP Status Code: {response.status_code}")