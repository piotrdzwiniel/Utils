### 🧠 Processing Scientific Articles Workflow

**Directory Structure (at start):**

```
project_directory/
│
├── temp/                   ← Place articles (PDFs) to be processed here
├── articles_good/          ← Automatically filled with valid articles (with DOI, title, authors, and year)
├── articles_bad/           ← Automatically filled with articles without valid metadata
├── articles_duplicates/    ← Automatically filled with duplicate DOI articles
│
├── 1_ExtractDOIs.py
├── 2_FetchMetadataFromCrossRefAPI.py
├── 3_ChangeFilenamesAndCreateSummary.py
├── 4_Splitter.py
├── 5_AddRecordsToDigitalLibrary.py
├── DigitalLibrary.csv      ← Persistent master file (created/updated automatically)
└── _pipeline.md            ← This file
```

---

### 🔄 Processing Pipeline

#### **Step 0:**

Move all new articles (PDF files) into the `temp/` folder.

---

#### **Step 1: Extract DOIs & Normalize Filenames**

Run:

```bash
python 1_ExtractDOIs.py
```

* Iterates through PDFs in `temp/`
* Renames all files to numeric format (`1.pdf`, `2.pdf`, ...)
* Extracts DOI from the first page(s)
* Saves results to `1_DOIs.csv`

---

#### **Step 2: Fetch Metadata from CrossRef API and DOI**

Run:

```bash
python 2_FetchMetadataFromCrossRefAPI.py
```

* Reads `1_DOIs.csv`
* Fetches metadata from CrossRef:

  * Title
  * Authors
  * Year
  * APA-style citation
* Saves metadata to `2_CrossRefMetadata.csv`

---

#### **Step 3: Generate Clean Filenames & Handle Duplicates**

Run:

```bash
python 3_ChangeFilenamesAndCreateSummary.py
```

* Reads `2_CrossRefMetadata.csv`
* Checks for duplicate DOIs (excluding `"unknown"`) and:

  * Keeps **only one** article with each duplicate DOI in the working set
  * Moves the **redundant files** to `articles_duplicates/`
* Then, for remaining entries:

  * Generates safe filenames (`Author (Year) Title.pdf`)
  * Renames PDF files in `temp/` accordingly
* Saves cleaned metadata to `3_FilenameAuthorYearTitleDOI.csv`

---

#### **Step 4: Split Articles Based on Valid Metadata**

Run:

```bash
python 4_Splitter.py
```

* Reads `3_FilenameAuthorYearTitleDOI.csv`
* Moves:

  * Articles **with valid DOI, title, authors, and year** → `articles_good/`
  * Articles **with missing or "unknown" DOI/title/authors/year** → `articles_bad/`
  * Articles in `temp/` with duplicate DOI already moved to `articles_good/` → `articles_duplicates/`
* Clears the `temp/` folder

⚠️ If any files remain in `temp/`, inspect manually — they likely belong in `articles_bad/` or are malformed.

---

#### **Step 5: Update Digital Library**

Run:

```bash
python 5_AddRecordsToDigitalLibrary.py
```

* Reads `3_FilenameAuthorYearTitleDOI.csv`
* Appends **new records** (based on unique DOI and valid title, authors, and year) to `DigitalLibrary.csv`
* Moves DOI **duplicates** from `articles_good/` → `articles_duplicates/`
* Skips already existing or incomplete entries
