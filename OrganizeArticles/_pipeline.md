### Processing Scientific Articles Workflow

**Directory Structure (at start):**

```
project_directory/
│
├── temp/                   ← Place articles (PDFs) to be processed here
├── articles_good/          ← Automatically filled with valid articles (with DOI)
├── articles_bad/           ← Automatically filled with articles without DOI
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

#### **Step 1: Extract DOIs**

Run:

```bash
python 1_ExtractDOIs.py
```

* Reads PDF files from `temp/`
* Extracts DOI from first page(s)
* Saves results to `1_DOIs.csv`

---

#### **Step 2: Fetch Metadata from CrossRef API and DOI**

Run:

```bash
python 2_FetchMetadataFromCrossRefAPI.py
```

* Reads `1_DOIs.csv`
* Fetches metadata from CrossRef (title, authors, year, APA citation)
* Saves metadata to `2_CrossRefMetadata.csv`

---

#### **Step 3: Generate Clean Filenames and Final Metadata**

Run:

```bash
python 3_ChangeFilenamesAndCreateSummary.py
```

* Reads `2_CrossRefMetadata.csv`
* Generates safe filenames (based on Author, Year, Title)
* Renames PDFs in `temp/`
* Saves summary to `3_FilenameAuthorYearTitleDOI.csv`

---

#### **Step 4: Split Articles Based on DOI**

Run:

```bash
python 4_Splitter.py
```

* Reads `3_FilenameAuthorYearTitleDOI.csv`
* Moves:

  * Articles **with DOI** → `articles_good/`
  * Articles **without DOI** → `articles_bad/` - handle them manually
* Clears `temp/` folder

If there are remaining files in `temp/`, check them manually and most likely move to `articles_bad/`

---

#### **Step 5: Update Digital Library**

Run:

```bash
python 5_AddRecordsToDigitalLibrary.py
```

* Reads `3_FilenameAuthorYearTitleDOI.csv`
* Appends **new records** (based on DOI) to `DigitalLibrary.csv`
* Moves **duplicates** from `articles_good/` → `articles_duplicates/`
* Skips already existing entries (based on DOI)
