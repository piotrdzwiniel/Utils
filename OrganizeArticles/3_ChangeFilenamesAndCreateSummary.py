import pandas as pd
import re
import os

# Load metadata
df = pd.read_csv("2_CrossRefMetadata.csv")


# Function to generate new filename based on metadata
def format_filename(authors, year, title):
    first_author = authors.split(";")[0].strip()
    author_last = first_author.split()[0]

    year_str = str(year).split(".")[0]
    title_words = re.findall(r'\w+', title)
    title_snippet = " ".join(title_words[:10])

    raw_filename = f"{author_last} ({year_str}) {title_snippet}.pdf"
    safe_filename = re.sub(r'[<>:"/\\|?*]', '', raw_filename)
    return safe_filename


# Generate new filenames only for known DOIs
df['new_filename'] = df.apply(
    lambda row: row['filename'] if str(row['doi']).strip().lower() == "unknown"
    else format_filename(row['authors'], row['year'], row['title']),
    axis=1
)

# Overwrite 'filename' column with new filenames (as per user request)
df['filename'] = df['new_filename']
df = df.drop(columns=['new_filename'])

# Reorder columns
df = df[['filename', 'authors', 'year', 'title', 'doi']]

# Save updated CSV
df.to_csv("3_FilenameAuthorYearTitleDOI.csv", index=False)

# Rename files on disk if enabled
change_file_names = True
folder_path = "articles"

if change_file_names:
    original_df = pd.read_csv("2_CrossRefMetadata.csv")  # use original to map old → new
    for _, row in df.iterrows():
        new_name = row['filename']
        doi = row['doi']

        # Get original filename from the initial CSV
        if str(doi).strip().lower() == "unknown":
            continue  # filename remains unchanged, nothing to rename

        old_name = original_df.loc[original_df['doi'] == doi, 'filename'].values
        if len(old_name) == 0:
            print(f"⚠️ Original filename not found for DOI: {doi}")
            continue

        old_name = old_name[0]
        old_path = os.path.join(folder_path, old_name)
        new_path = os.path.join(folder_path, new_name)

        if old_name == new_name:
            continue  # nothing to rename

        if os.path.exists(old_path):
            if os.path.exists(new_path):
                print(f"⚠️ Target file already exists: {new_name}")
                continue
            try:
                os.rename(old_path, new_path)
                print(f"✅ Renamed: {old_name} → {new_name}")
            except Exception as e:
                print(f"❌ Failed to rename {old_name}: {e}")
        else:
            print(f"🚫 File not found: {old_name}")
