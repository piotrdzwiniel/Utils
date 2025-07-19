import pandas as pd
import requests
import time

# Load CSV with DOIs
df = pd.read_csv("1_DOIs.csv")

# Prepare output list
records = []

# Set user-agent for polite API usage
headers = {
    "User-Agent": "DOI-MetadataFetcher/1.0 (mailto:piotr.dzwiniel@gmail.com)"
}

# Total number of entries
total = len(df)

# Loop through DOIs with progress
for index, row in df.iterrows():
    doi = str(row['doi']).strip()
    filename = row['filename']
    current = index + 1

    print(f"\n🔄 Processing {current}/{total} ({(current / total * 100):.1f}%) — {filename}, DOI: {doi}")

    if doi and doi.lower() != 'Unknown' and doi != '':
        url = f"https://api.crossref.org/works/{doi}"
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()['message']

            # Extract metadata
            title = data.get("title", [""])[0]
            year = str(data.get("issued", {}).get("date-parts", [[None]])[0][0])
            authors = data.get("author", [])
            author_list = [f"{a.get('family', '')} {a.get('given', '')}".strip() for a in authors]

            # Remove empty strings
            author_list = [a for a in author_list if a]

            print(f"✅ Retrieved metadata for DOI: {doi}")

            print("Authors:", author_list)
            print("Title:", title)
            print("Year:", year)

            records.append({
                "filename": filename,
                "doi": doi,
                "title": title,
                "year": year,
                "authors": "; ".join(author_list)
            })

        except Exception as e:
            print(f"❌ Failed for DOI {doi}: {e}")
            records.append({
                "filename": filename,
                "doi": doi,
                "title": "Unknown",
                "year": "Unknown",
                "authors": "Unknown"
            })

        time.sleep(0.5)  # Be polite to the API
    else:
        print("⚠️ No valid DOI provided.")
        records.append({
            "filename": filename,
            "doi": "Unknown",
            "title": "Unknown",
            "year": "Unknown",
            "authors": "Unknown"
        })

# Convert to DataFrame
metadata_df = pd.DataFrame(records)

# Show summary and save results
print("\n✅ Done. Saving results to CrossRefMetadata.csv")
metadata_df.to_csv("2_CrossRefMetadata.csv", index=False)
