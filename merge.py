import os
import glob
import pandas as pd

OUTPUT_DIR = "Output"  # Folder containing thread output files
OUTPUT_FILE = "Loan Rules.xlsx"

def merge_excel_files():
    """Merge all Excel files in OUTPUT_DIR into a single Excel file."""
    all_data = []
    excel_files = glob.glob(os.path.join(OUTPUT_DIR, "*.xlsx"))

    if not excel_files:
        print("❌ No Excel files found to merge.")
        return

    for file_path in excel_files:
        try:
            print(f"✅ Including: {file_path}")
            df = pd.read_excel(file_path, engine="openpyxl")
            all_data.append(df)
        except Exception as e:
            print(f"⚠️ Failed to read {file_path}: {e}")

    final_df = pd.concat(all_data, ignore_index=True)

    # Remove old output file if it exists
    if os.path.exists(OUTPUT_FILE):
        os.remove(OUTPUT_FILE)

    final_df.to_excel(OUTPUT_FILE, index=False)
    print(f"📁 Merged {len(excel_files)} files. Final output: {OUTPUT_FILE} ({os.path.getsize(OUTPUT_FILE)/1024:.2f} KB)")


merge_excel_files()