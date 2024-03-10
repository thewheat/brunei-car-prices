# Brunei Car Prices

- Data extracted from DEPD (Department of Economic Planning and Statistics) https://deps.mofe.gov.bn
- Source files: https://deps.mofe.gov.bn/DEPD%20Documents%20Library/Forms/AllItems.aspx?RootFolder=%2FDEPD%20Documents%20Library%2FKH%2Fcars&FolderCTID=0x01200054D7905F1114F84892C81BDC2CC4C7CE&View={4DDE193B-C0DA-4E84-838E-C66D84EA697D}

## Data is extracted on a base effort basis but there are bound to be errors

## Usage

```
python 1scrape.py
python 2useSumFiles.py
python 3convertToText.py
python 4convertToCSV.py
```

## Overview

- Download PDFs
- Use only "sum" folders where they exist (as non "sum" folders list brands individually)
   - Later years only have "sum" folders
- PDFs are converted to text via `pdftotext` https://poppler.freedesktop.org/
   - This method is used as I tried several PDFs to spreadsheet/CSV/Excel converters but there was missing data so for now opted extraction of text for now
- Data is extracted from these text files
   - Several hacks needed to get the right data as a best effort
   - Examples are
      - Likely incorrect costs
      - Weird text preventing regular extraction
      - Oddities in PDF to text formatting
   - Due to this there can be possible incorrect extractions

