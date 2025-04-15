import json
import re
from datetime import datetime
from collections import OrderedDict

# Function to normalize dates and insert them inline
def normalize_date(date_str):
    try:
        clean_date = re.search(r"(\d{1,2}/\d{1,2}/\d{2,4})", date_str)
        if clean_date:
            clean_date = clean_date.group(1)
            parsed_date = datetime.strptime(clean_date, "%m/%d/%y").strftime("%Y-%m-%d")
            return parsed_date
        elif re.match(r"\d{1,2}/\d{2,4}", date_str):
            parsed_date = datetime.strptime(date_str, "%m/%y").strftime("%Y-%m-01")
            return parsed_date
        elif re.match(r"\d{4}", date_str):  
            return f"{date_str}-01-01"
    except ValueError:
        pass  
    return None  

# Function to normalize and extract dollar figures, inserting them inline
def normalize_currency(value):
    if not value:
        return None  # Handle missing or "undisclosed" values
    
    value = str(value).replace(",", "").replace("$", "").strip().lower()
    
    # Convert shorthand (e.g., "1.2m" -> "1200000")
    match = re.match(r"([\d\.]+)([mk]?)", value)
    if match:
        num, suffix = match.groups()
        try:
            num = float(num)
            if suffix == "m":  
                num *= 1_000_000
            elif suffix == "k":  
                num *= 1_000
            return int(num)  
        except ValueError:
            return None  
    return None  

# Function to extract and insert normalized currency values inline within text
def insert_normalized_currency(text):
    if not text:
        return text, None
    
    matches = re.findall(r"\$?([\d,]+(?:\.\d{1,2})?)", text)  # Extract currency values
    extracted_values = []
    
    for match in matches:
        normalized_value = normalize_currency(match)
        if normalized_value is not None:
            extracted_values.append(normalized_value)
            text = text.replace(f"${match}", f"${match} ({normalized_value})", 1)
    
    return text, extracted_values if extracted_values else None

# Function to normalize the "facts" section by inserting normalized dates inline
def normalize_facts(facts_str):
    match = re.match(r"(\d{1,2}/\d{1,2}/\d{2,4})", facts_str)
    if match:
        original_date = match.group(1)
        normalized = normalize_date(original_date)
        if normalized:
            return facts_str.replace(original_date, f"{original_date} ({normalized})", 1)
    return facts_str  

# File names
input_file = "parsed_cases.json"
output_file = "parsed_cases_normalized.json"

# Load JSON data
with open(input_file, "r", encoding="utf-8-sig") as f:
    data = json.load(f)

# Process each case
normalized_data = []
for case in data:
    new_case = OrderedDict()
    for key, value in case.items():
        new_case[key] = value

        if key == "date":  
            normalized = normalize_date(value)
            if normalized:
                new_case["normalized_date"] = normalized  

        if key == "facts":  
            new_case[key] = normalize_facts(value)  

        # Normalize and insert monetary values inline
        if key in ["specials", "result", "settlement"]:  # FIX: Added "settlement"
            new_case[key], extracted_values = insert_normalized_currency(value)
            if extracted_values:
                new_case[key + "_values"] = extracted_values  # Store extracted numbers separately

    normalized_data.append(new_case)

# Save updated JSON data
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(normalized_data, f, indent=4, ensure_ascii=False)

print(f"Normalization complete! Saved to {output_file}")

