import fitz  # PyMuPDF
import re
from pathlib import Path
import pandas as pd

# Path to folder with PDFs
pdf_folder = Path("articles")

# Regex pattern for DOI
# doi_pattern = re.compile(r'\b10\.\d{4,9}/\S+\b', re.IGNORECASE)
doi_pattern = re.compile(r'10\.\d{4,9}/[^\s"<>]+', re.IGNORECASE)

# Store results
results = []

# Loop through PDFs
for pdf_file in pdf_folder.glob("*.pdf"):
    try:
        with fitz.open(pdf_file) as doc:
            text = ""
            for page in doc:
                text += page.get_text()
                if len(text) > 10000:  # limit text length for performance
                    break

            # Search for DOI
            match = doi_pattern.search(text)
            doi = match.group(0).rstrip(').') if match else "Unknown"

            results.append({
                "filename": pdf_file.name,
                "doi": doi
            })

    except Exception as e:
        print(f"❌ Error processing {pdf_file.name}: {e}")
        results.append({
            "filename": pdf_file.name,
            "doi": "Unknown"
        })

# Convert to DataFrame
df = pd.DataFrame(results)

# Show results
print(df)

# Optional: Save to CSV
df.to_csv("1_DOIs.csv", index=False)
