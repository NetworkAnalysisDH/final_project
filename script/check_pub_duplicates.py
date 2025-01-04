import os
import json
from collections import defaultdict

# Loading logic for publications
base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../data"))
file_path = os.path.join(base_path, "publications_filtered_fixed1.json")

def load_publications(file_path):
    # Load the JSON file
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    # Access the list of publications
    if "publications" in data:
        data = data["publications"]
    else:
        raise ValueError("The JSON file does not contain the 'publications' key.")

    # Check that it is a list
    if not isinstance(data, list):
        raise ValueError("The 'publications' key must contain a list of articles.")
    
    return data

def get_article_id(entry):
    # Return the first available value for article_id
    return entry.get("id") or entry.get("doi") or entry.get("url") or entry.get("isbn") or entry.get("title")

def find_duplicates(publications):
    # Dictionary to store occurrences of article_ids
    seen = defaultdict(list)
    duplicates = []

    # Loop through publications and check for duplicates
    for index, entry in enumerate(publications):
        article_id = get_article_id(entry)
        
        if article_id:
            # If article_id is already seen, add the current index to the duplicates list
            if article_id in seen:
                duplicates.append((seen[article_id], index))
            # Store the index of the current article_id
            seen[article_id].append(index)
    
    return duplicates

def main():
    # Load the publications data
    publications = load_publications(file_path)
    
    # Find duplicates
    duplicates = find_duplicates(publications)
    
    if duplicates:
        print("Found duplicates:")
        for dup in duplicates:
            print(f"Duplicate entries found at indices: {dup[0]} and {dup[1]}")
            # Loop through the list of indices to print each duplicate entry
            for idx in dup[0]:
                print(f"Entry {idx}: {publications[idx]}")
            print(f"Entry {dup[1]}: {publications[dup[1]]}")
            print("-" * 80)
    else:
        print("No duplicates found.")

if __name__ == "__main__":
    main()
