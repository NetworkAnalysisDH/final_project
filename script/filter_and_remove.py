import os
import json

# Load the JSON file
base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../data"))
file_path = os.path.join(base_path, "publications_filtered_fixed1.json")
output_file_path = os.path.join(base_path, "publications.json")

def load_publications(file_path):
    # Load the JSON file
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    # Access the list of publications
    if "publications" in data:
        data = data["publications"]
    else:
        raise ValueError("The JSON file does not contain the 'publications' key.")
    
    # Ensure it is a list
    if not isinstance(data, list):
        raise ValueError("The 'publications' key must contain a list of articles.")
    
    return data

def get_article_id(entry):
    # Return the first available identifier for the article
    return entry.get("id") or entry.get("doi") or entry.get("url") or entry.get("isbn") or entry.get("title")

def filter_duplicates(publications):
    # Dictionary to store the most complete version of each article by article_id
    unique_publications = {}
    
    for entry in publications:
        article_id = get_article_id(entry)
        
        if article_id:
            # If article_id is already present, compare completeness
            if article_id in unique_publications:
                current_entry = unique_publications[article_id]
                # Replace with the more complete entry (based on the number of keys)
                if len(entry.keys()) > len(current_entry.keys()):
                    unique_publications[article_id] = entry
            else:
                # Add the current entry
                unique_publications[article_id] = entry
    
    # Return only the unique entries
    return list(unique_publications.values())

def save_filtered_publications(filtered_publications, output_file_path):
    # Create a dictionary with the "publications" key and save as JSON
    with open(output_file_path, "w", encoding="utf-8") as f:
        json.dump({"publications": filtered_publications}, f, indent=4, ensure_ascii=False)

def main():
    # Load the publications
    publications = load_publications(file_path)
    
    # Filter duplicates
    filtered_publications = filter_duplicates(publications)
    
    # Save the filtered publications to a new JSON file
    save_filtered_publications(filtered_publications, output_file_path)
    
    # Print comparison of total entries
    print(f"Original file contains {len(publications)} entries.")
    print(f"Filtered file contains {len(filtered_publications)} entries.")
    print(f"Filtering complete. File saved at: {output_file_path}")

if __name__ == "__main__":
    main()
