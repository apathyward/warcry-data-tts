import requests
import json
from collections import defaultdict

# URL to download the JSON data
url = "https://krisling049.github.io/warcry_data/fighters_tts.json"

# Download and parse the JSON data
response = requests.get(url)
data = response.json()

# Dictionary to track entries by name
name_groups = defaultdict(list)

# Group entries by name
for fighter in data:
    name = fighter.get("name")
    if name:
        name_groups[name].append(fighter)

# Write duplicates to a text file
with open("duplicates.txt", "w") as output:
    for name, fighters in name_groups.items():
        if len(fighters) > 1:  # Only output names with duplicates
            output.write(f"Name: {name}\n")
            for fighter in fighters:
                output.write(f"  Warband: {fighter.get('warband')}, _id: {fighter.get('_id')}\n")
            output.write("\n")

print("All shared name values with IDs have been saved to duplicates.txt")
