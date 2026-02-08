import requests
import json
import os
import re
import time
from duckduckgo_search import DDGS

# Function to extract data from data.js
def extract_data_from_js(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    # Find the JSON object inside the JS file
    match = re.search(r'const slideData = ({.*});', content, re.DOTALL)
    if match:
        json_str = match.group(1)
        # Javascript object keys might not be quoted, fix that for valid JSON
        # This is a simple regex fix, might need more robustness for complex JS
        # Assuming the structure is simple as per view_file output
        # Remove comments if any (simple line comments)
        json_str = re.sub(r'//.*', '', json_str)
        # Fix unquoted keys
        # json_str = re.sub(r'(\w+):', r'"\1":', json_str) 
        # Actually, let's just use Python's eval mostly safe here since we know content
        # creating a dummy variable for JS 'const'
        # But even better, let's just parse it manually or use a JS parser if available, 
        # but regex for this specific simple file is safer/easier than dependency.
        
        # Let's try to parse the structure directly from the file content we saw earlier
        # expected format: "Category": [ { "en": "Word", "ta": "Tamil" }, ... ]
        
        # simplified parsing logic:
        # Find all keys (Categories) and their arrays
        data = {}
        
        # Clean up newlines and extra spaces
        clean_content = re.sub(r'\s+', ' ', json_str)
        
        # Extract categories
        # Pattern: "CategoryName": [ ... ]
        # The keys in the file are quoted (e.g. "Animals":), so standard JSON might almost work if we clean trailing commas
        
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            print("Direct JSON parse failed, trying relaxed parsing...")
            # Fallback: simple evaluation since the file format is known and trusted
            # modifying the string to be valid python dictionary syntax
            # true/false/null -> True/False/None
            py_str = json_str.replace("true", "True").replace("false", "False").replace("null", "None")
            try:
                data = eval(py_str)
                return data
            except Exception as e:
                print(f"Eval parsing failed: {e}")
                return None
    return None

def download_image(keyword, filename):
    print(f"Searching for: {keyword}")
    try:
        with DDGS() as ddgs:
            results = list(ddgs.images(
                keywords=keyword,
                region="wt-wt",
                safesearch="on",
                max_results=1
            ))
            
            if results:
                image_url = results[0]['image']
                print(f"Downloading {image_url}...")
                try:
                    # Use requests with a timeout and user-agent
                    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
                    response = requests.get(image_url, headers=headers, timeout=10, verify=False) # verify=False effectively bypasses SSL verification issues for this script
                    if response.status_code == 200:
                        with open(filename, 'wb') as f:
                            f.write(response.content)
                        print(f"Saved to {filename}")
                        return True
                    else:
                        print(f"Failed to download {image_url}: Status {response.status_code}")
                except Exception as e:
                    print(f"Failed to download {image_url}: {e}")
            else:
                print(f"No results found for {keyword}")
    except Exception as e:
        print(f"Search failed for {keyword}: {e}")
    return False

def main():
    data_file = 'data.js'
    image_dir = 'images'
    
    if not os.path.exists(image_dir):
        os.makedirs(image_dir)
        
    data = extract_data_from_js(data_file)
    
    if not data:
        print("Failed to extract data from data.js")
        return

    for category, items in data.items():
        print(f"\nProcessing category: {category}")
        for item in items:
            word = item['en']
            # Search query: "Word Category" to be specific (e.g. "Orange Fruit" vs "Orange Color")
            # If category is "Family", maybe "Mother person" or just "Mother"
            # Adjusting query based on category for better results
            
            search_query = f"{word}"
            if category in ["Fruits", "Animals", "Colors"]:
                search_query = f"{word} {category[:-1]}" # Singularize category roughly
            elif category == "Family":
                search_query = f"{word} family cartoon" # Cartoon might be better for kids, or just "Mother"
                # Let's try realistic first as requested by "representative"
                search_query = f"{word} person" if word not in ["Baby"] else "Baby"

            # Filename: Category_Word.jpg to avoid collisions
            filename = os.path.join(image_dir, f"{category}_{word}.jpg")
            
            if os.path.exists(filename):
                print(f"Image already exists for {word}, skipping.")
                continue
                
            success = download_image(search_query, filename)
            if not success:
                print(f"Warning: Could not download image for {word}")
            
            # Sleep to be polite to the server and avoid rate limits
            time.sleep(3)

if __name__ == "__main__":
    main()
