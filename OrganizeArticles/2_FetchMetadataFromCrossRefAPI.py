import pandas as pd
import requests
import time

# Load CSV with DOIs
df = pd.read_csv("1_DOIs.csv").dropna()

# Prepare output list
records = []

# Set user-agent for polite API usage
headers = {
    "User-Agent": "DOI-MetadataFetcher/1.0 (mailto:piotr.dzwiniel@gmail.com)"
}
headers_apa = {
    "User-Agent": "DOI-MetadataFetcher/1.0 (mailto:piotr.dzwiniel@gmail.com)",
    "Accept": "text/x-bibliography; style=apa"
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
        citation_url = f"https://doi.org/{doi}"

        try:
            # Get metadata
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()['message']

            # Extract metadata
            title = data.get("title", [""])[0]
            year = str(data.get("issued", {}).get("date-parts", [[None]])[0][0])
            authors = data.get("author", [])
            author_list = [f"{a.get('family', '')} {a.get('given', '')}".strip() for a in authors]
            author_list = [a for a in author_list if a]  # Remove empty strings

            # Fallback to "Unknown" if any field is empty or None
            title = title if title else "Unknown"
            year = year if year and year != 'None' else "Unknown"
            author_list = author_list if author_list else "Unknown"

            print(f"✅ Retrieved metadata for DOI: {doi}")
            print("Authors:", author_list)
            print("Title:", title)
            print("Year:", year)

            # Get APA citation
            try:
                citation_response = requests.get(citation_url, headers=headers_apa, timeout=10)
                citation_response.raise_for_status()

                # Force decoding with UTF-8-Sig (sig helps read the CSV files in Excel)
                citation_response.encoding = 'utf-8-sig'
                apa_citation = citation_response.text.strip()

                print("📖 APA Citation:", apa_citation)
            except Exception as e:
                print(f"⚠️ Could not retrieve APA citation: {e}")
                apa_citation = "Unavailable"

            records.append({
                "filename": filename,
                "doi": doi,
                "title": title,
                "year": year,
                "authors": author_list if author_list == "Unknown" else ", ".join(author_list),
                "apa_citation": apa_citation
            })

        except Exception as e:
            print(f"❌ Failed for DOI {doi}: {e}")
            records.append({
                "filename": filename,
                "doi": doi,
                "title": "Unknown",
                "year": "Unknown",
                "authors": "Unknown",
                "apa_citation": "Unavailable"
            })

        time.sleep(0.5)  # Be polite to the API; one call per 0.5 s
    else:
        print("⚠️ No valid DOI provided.")
        records.append({
            "filename": filename,
            "doi": "Unknown",
            "title": "Unknown",
            "year": "Unknown",
            "authors": "Unknown",
            "apa_citation": "Unavailable"
        })

# Convert to DataFrame
metadata_df = pd.DataFrame(records)

# Show summary and save results
metadata_df.to_csv("2_CrossRefMetadata.csv", index=False, encoding='utf-8-sig')

print("\n✅ Done. Saving results to CrossRefMetadata.csv")
