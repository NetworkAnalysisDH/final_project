import os
import json

# Relative path to the JSON file
base_path = os.path.dirname(os.path.abspath(__file__)) 
file_path = os.path.join(base_path, "..", "data", "publications.json")

# Load the data from the JSON file
with open(file_path, 'r') as f:
    data = json.load(f)

# Assuming you want to print the attributes for the first publication in the list
publication = data['publications'][0]

# Loop through the attributes and print them
for key, value in publication.items():
    print(f"{key}: {value}")