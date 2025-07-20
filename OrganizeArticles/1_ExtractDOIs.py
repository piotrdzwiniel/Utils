import fitz  # pip install pymupdf
import re
from pathlib import Path
import pandas as pd

# Path to folder with PDFs
pdf_folder = Path("temp")

# Rename all PDFs to sequential numbers
pdf_files = list(pdf_folder.glob("*.pdf"))
pdf_files.sort()  # ensure consistent order

print(f"🔁 Renaming {len(pdf_files)} files to sequential numbers...\n")

for i, file in enumerate(pdf_files, 1):
    new_name = f"{i}.pdf"
    new_path = pdf_folder / new_name
    try:
        file.rename(new_path)
        print(f"✅ Renamed: {file.name} → {new_name}")
    except Exception as e:
        print(f"❌ Failed to rename {file.name}: {e}")

# Refresh file list after renaming
pdf_files = list(pdf_folder.glob("*.pdf"))
pdf_files.sort()  # sort numerically if needed
total_files = len(pdf_files)

# Regex pattern for DOI
doi_pattern = re.compile(r'10\.\d{4,9}/[^\s"<>]+', re.IGNORECASE)

# Store results
results = []

# Get list of PDF files
# pdf_files = list(pdf_folder.glob("*.pdf"))
# total_files = len(pdf_files)

print(f"\n📁 Found {total_files} PDF files to process.\n")

# Loop through PDFs with progress display
for idx, pdf_file in enumerate(pdf_files, 1):
    try:
        with fitz.open(pdf_file) as doc:
            text = ""
            for page in doc:
                text += page.get_text()
                if len(text) > 5000:  # limit text length for performance
                    break

            # Search for DOI
            match = doi_pattern.search(text)
            doi = match.group(0).rstrip(').,') if match else "Unknown"

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

    # Progress display
    progress = (idx / total_files) * 100
    print(f"✅ Processed {idx} / {total_files} ({progress:.1f}%) — {pdf_file.name}")

# Convert to DataFrame
df = pd.DataFrame(results)

# Optional: Save to CSV
df.to_csv("1_DOIs.csv", index=False)
print("\n✅ Finished processing. Results saved to 1_DOIs.csv.")
