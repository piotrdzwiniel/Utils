import pandas as pd
import os
import shutil

# Show all columns and rows
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

# Optional: Expand the column width so it doesn't truncate text
pd.set_option('display.max_colwidth', None)  # for pandas < 1.0 use -1

# Optional: Do not wrap the frame across multiple lines
pd.set_option('display.width', None)

# File paths
input_csv = "3_FilenameAuthorYearTitleDOI.csv"
library_csv = "DigitalLibrary.csv"
good_folder = "articles_good"
bad_folder = "articles_bad"
dup_folder = "articles_duplicates"

# Ensure destination folders exist
os.makedirs(good_folder, exist_ok=True)
os.makedirs(bad_folder, exist_ok=True)
os.makedirs(dup_folder, exist_ok=True)

# Load data
new_df = pd.read_csv(input_csv)

# Normalize fields
new_df['doi'] = new_df['doi'].astype(str).str.strip().str.lower()
new_df['title'] = new_df['title'].astype(str).str.strip()
new_df['year'] = new_df['year'].astype(str).str.strip()
new_df['authors'] = new_df['authors'].astype(str).str.strip()

# Filter out unknown values
new_df = new_df[
    (new_df['doi'] != 'unknown') &
    (new_df['title'].str.lower() != 'unknown') &
    (new_df['year'].str.lower() != 'unknown') &
    (new_df['authors'].str.lower() != 'unknown')
].copy()

# new_df = new_df[new_df['doi'].str.lower() != 'unknown'].copy()
# new_df['doi'] = new_df['doi'].str.strip().str.lower()  # normalize DOI

print(new_df)

if os.path.exists(library_csv):
    library_df = pd.read_csv(library_csv)
    library_df['doi'] = library_df['doi'].str.strip().str.lower()  # normalize DOI
else:
    library_df = pd.DataFrame(columns=['filename', 'authors', 'year', 'title', 'doi', 'apa_citation'])

# Identify new entries and duplicates
existing_dois = set(library_df['doi'].dropna())
new_entries = new_df[~new_df['doi'].isin(existing_dois)].copy()
duplicates = new_df[new_df['doi'].isin(existing_dois)].copy()

# Append new entries to library ===
if not new_entries.empty:
    updated_library = pd.concat([library_df, new_entries], ignore_index=True)
    updated_library.to_csv(library_csv, index=False, encoding='utf-8-sig')
    print(f"✅ Added {len(new_entries)} new entries to '{library_csv}'.")
else:
    print("ℹ️ No new entries to add.")

# Handle duplicates ===
if not duplicates.empty:
    print(f"\n⚠️ Found {len(duplicates)} duplicate DOI(s):")

    for _, row in duplicates.iterrows():
        filename = row['filename']
        doi = row['doi']
        print(f" - {filename} (DOI: {doi})")

        source_path = os.path.join(good_folder, filename)
        dup_path = os.path.join(dup_folder, filename)

        if os.path.exists(source_path):
            try:
                shutil.move(source_path, dup_path)
                print(f"   🔁 Moved '{filename}' from '{good_folder}' → '{dup_folder}'")
            except Exception as e:
                print(f"   ❌ Failed to move file '{filename}': {e}")
        else:
            print(f"   ⚠️ File not found in '{good_folder}': {filename}'")

print("\n✅ Script finished.")
