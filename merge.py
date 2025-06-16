import os
import glob
import pandas as pd

OUTPUT_DIR = "Output"  # Folder containing thread output files
OUTPUT_FILE = "Loan Rules.xlsx"

def merge_excel_files(output_dir, output_file):
    """Merge all Excel files in the output directory into a single file."""
    all_data = []

    # Get all .xlsx files in the directory
    file_paths = glob.glob(os.path.join(output_dir, "*.xlsx"))

    if not file_paths:
        print("❌ No Excel files found to merge.")
        return

    for file_path in file_paths:
        try:
            print(f"✅ Including: {file_path}")
            df = pd.read_excel(file_path, engine="openpyxl")
            print(df)

           
            #df = df.sort_values(by=['Fulfillment Unit Number', 'Rule Number'])
            all_data.append(df)
        except Exception as e:
            print(f"⚠️ Failed to read {file_path}: {e}")

    if all_data:
        final_df = pd.concat(all_data, ignore_index=True)

        if os.path.exists(output_file):
            os.remove(output_file)

        final_df.to_excel(output_file, index=False)
        print(f"📁 Merged {len(file_paths)} files. Final output: {output_file} ({os.path.getsize(output_file)/1024:.2f} KB)")
    else:
        print("❌ No valid data found to merge.")

merge_excel_files(OUTPUT_DIR, OUTPUT_FILE)