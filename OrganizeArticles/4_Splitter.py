import os
import shutil
import pandas as pd

# Configuration
input_csv = "3_FilenameAuthorYearTitleDOI.csv"
source_folder = "temp"
good_folder = "articles_good"
bad_folder = "articles_bad"

# Create destination folders if they do not exist
os.makedirs(good_folder, exist_ok=True)
os.makedirs(bad_folder, exist_ok=True)

# Load metadata
df = pd.read_csv(input_csv)

total_files = len(df)
processed_files = 0
moved_to_good = 0
moved_to_bad = 0

print(f"📥 Processing {total_files} articles from folder: {source_folder}")

# Move articles based on DOI availability
for idx, row in df.iterrows():
    filename = row["filename"]
    doi = str(row["doi"]).strip().lower()
    title = str(row["title"]).strip().lower()
    authors = str(row["authors"]).strip().lower()
    pub_year = str(row["year"]).split(".")[0].lower()
    source_path = os.path.join(source_folder, filename)

    if not os.path.exists(source_path):
        print(f"⚠️  File not found: {filename}")
        continue

    # Choose destination folder based on DOI
    if doi != "unknown" and title != "unknown" and authors != "unknown" and pub_year != "unknown":
        print(doi, title, authors, pub_year)
        destination_path = os.path.join(good_folder, filename)
        moved_to_good += 1
    else:
        destination_path = os.path.join(bad_folder, filename)
        moved_to_bad += 1

    try:
        shutil.move(source_path, destination_path)
        processed_files += 1
        progress_percent = processed_files / total_files * 100
        print(f"✅ Processed {processed_files} / {total_files} ({progress_percent:.1f}%) — {filename}")
    except Exception as e:
        print(f"❌ Error moving file {filename}: {e}")

# Summary
print("\n✅ Operation complete.")
print(f"📦 Successfully moved: {processed_files} of {total_files} articles.")

good_pct = (moved_to_good / total_files * 100) if total_files else 0
bad_pct = (moved_to_bad / total_files * 100) if total_files else 0

print(f"📂 → Moved to '{good_folder}': {moved_to_good} ({good_pct:.1f}%)")
print(f"📂 → Moved to '{bad_folder}': {moved_to_bad} ({bad_pct:.1f}%)")

remaining = len(os.listdir(source_folder))
print(f"📁 Remaining files in temp folder: {remaining}")