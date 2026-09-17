import os
import glob
import pandas as pd
import json
from datetime import datetime

EXCEL_FOLDER = "./daily_excel_files/"
OUTPUT_JSON = "./master_data.json"

def get_date_from_filename(filepath):
    # Extracts '16-09-26' from './daily_excel_files/16-09-26.xlsx'
    filename = os.path.basename(filepath)
    date_str = os.path.splitext(filename)[0]
    try:
        # Converts dd-mm-yy string into an actual date object for perfect chronological sorting
        return datetime.strptime(date_str, "%d-%m-%y")
    except ValueError:
        # Fallback if a file isn't named correctly
        print(f"Warning: File name '{filename}' does not match dd-mm-yy format.")
        return datetime.min

def combine_excel_files():
    # 1. Locate all Excel files in your folder
    excel_files = glob.glob(os.path.join(EXCEL_FOLDER, "*.xlsx")) + glob.glob(os.path.join(EXCEL_FOLDER, "*.xls"))
    
    # 2. Sort files properly using actual calendar dates instead of basic alphabet rules
    excel_files.sort(key=get_date_from_filename)
    
    if not excel_files:
        print("No files found! Make sure your Excel sheets are dropped inside the 'daily_excel_files' folder.")
        return

    all_data_frames = []

    # 3. Open and process each Excel file
    for file_path in excel_files:
        file_name = os.path.basename(file_path)
        date_label = os.path.splitext(file_name)[0] # e.g., "16-09-26"
        
        try:
            df = pd.read_excel(file_path)
            
            # Create a brand new column in the data stating which day this row belongs to
            df['Saved_Date'] = date_label
            
            all_data_frames.append(df)
            print(f"Successfully processed: {file_name}")
        except Exception as e:
            print(f"Skipped {file_name} due to an error: {e}")

    if not all_data_frames:
        return

    # 4. Stack all dates cleanly on top of each other into a single master table
    combined_df = pd.concat(all_data_frames, ignore_index=True)

    # Clean up any native Excel timestamps so your HTML can read them without breaking
    for col in combined_df.columns:
        if pd.api.types.is_datetime64_any_dtype(combined_df[col]):
            combined_df[col] = combined_df[col].dt.strftime('%d-%m-%y')

    # 5. Transform the final table into a web-ready format
    result_json = combined_df.to_dict(orient="records")

    # 6. Save your permanent historical file
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(result_json, f, indent=4, ensure_ascii=False)
        
    print(f"\nSuccess! All past and present history saved together in '{OUTPUT_JSON}'")

if __name__ == "__main__":
    combine_excel_files()