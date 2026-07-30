# Python OCR Doctor Receipt Extractor

## Overview

The Python OCR Doctor Receipt Extractor is a Python-based application that automatically extracts structured information from doctor receipt PDF files.

The system reads PDF receipts, converts each page into an image, performs Optical Character Recognition (OCR) using PaddleOCR, extracts important receipt information using regular expressions, and exports the extracted data into an Excel spreadsheet.

The project demonstrates an end-to-end OCR document processing workflow for structured data extraction from medical receipts.

---

# Objectives

The objectives of this project are to:

* Read doctor receipt PDF files.
* Convert PDF pages into images.
* Prepare images for OCR by converting them to RGB format.
* Extract text using PaddleOCR.
* Parse important information from the OCR output.
* Export the extracted information into an Excel file.

---

# Features

* Batch processing of multiple PDF receipts
* PDF to image conversion
* RGB image conversion for OCR compatibility
* Text extraction using PaddleOCR
* Receipt information parsing using Regular Expressions
* Excel export
* Basic error handling

---

# Technologies Used

| Technology               | Purpose                       |
| ------------------------ | ----------------------------- |
| Python 3                 | Programming Language          |
| PaddleOCR                | Optical Character Recognition |
| PyMuPDF                  | PDF Reader                    |
| Pillow                   | Image Processing              |
| OpenCV                   | Image Format Conversion       |
| OpenPyXL                 | Excel Export                  |
| Regular Expressions (re) | Data Extraction               |

---

# Project Structure

```
Python-OCR-invoice-extractor/

│
├── data/
│   ├── doctor_receipts_1.pdf
│   ├── doctor_receipts_2.pdf
│   ├── doctor_receipts_3.pdf
│   ├── doctor_receipts_4.pdf
│   └── doctor_receipts_5.pdf
│
├── output/
│   └── extracted_receipts.xlsx
│
├── src/
│   ├── main.py
│   ├── pdf_reader.py
│   ├── image_processor.py
│   ├── ocr_engine.py
│   ├── receipt_parser.py
│   └── excel_writer.py
│
├── requirements.txt
└── README.md
```

---

# System Workflow

```
PDF Receipt
      │
      ▼
PDF Reader
      │
      ▼
Convert PDF Page to Image
      │
      ▼
Convert Image to RGB
      │
      ▼
PaddleOCR
      │
      ▼
OCR Text
      │
      ▼
Receipt Parser
      │
      ▼
Structured Data
      │
      ▼
Excel Writer
      │
      ▼
Excel Spreadsheet
```

---

# Module Description

## 1. PDF Reader

**File**

```
pdf_reader.py
```

### Responsibilities

* Opens PDF documents.
* Converts each PDF page into a PIL image.
* Supports multiple-page PDFs.
* Closes PDF documents after processing.

Main functions:

* `load_pdf()`
* `convert_pages_to_images()`
* `close_pdf()`

---

## 2. Image Processor

**File**

```
image_processor.py
```

### Responsibilities

The Image Processor prepares images for OCR by ensuring that every image is converted into RGB format before being passed to PaddleOCR.

This guarantees compatibility between the generated images and the OCR engine.

Main function:

```
preprocess()
```

---

## 3. OCR Engine

**File**

```
ocr_engine.py
```

### Responsibilities

* Loads PaddleOCR.
* Extracts text from receipt images.
* Returns OCR text.
* Handles OCR exceptions.

Main function:

```
extract_text()
```

---

## 4. Receipt Parser

**File**

```
receipt_parser.py
```

### Responsibilities

The Receipt Parser uses Regular Expressions (Regex) to identify and extract structured information from the OCR output.

Extracted fields include:

* Receipt Number
* Doctor Name
* PRC License Number
* Hospital Name
* Receipt Date
* Patient Name
* Total Amount
* Signature Indicator

Main function:

```
parse()
```

---

## 5. Excel Writer

**File**

```
excel_writer.py
```

### Responsibilities

Exports all extracted receipt information into an Excel spreadsheet.

Main function:

```
export()
```

---

## 6. Main Program

**File**

```
main.py
```

### Responsibilities

The main program coordinates the entire extraction process.

Workflow:

```
Read PDF

↓

Convert PDF to Image

↓

Convert Image to RGB

↓

OCR using PaddleOCR

↓

Parse Receipt Information

↓

Export to Excel
```

---

# Extracted Fields

The system extracts the following information from each receipt.

| Field              | Description                                                    |
| ------------------ | -------------------------------------------------------------- |
| Page               | PDF page number                                                |
| Receipt No.        | Official receipt number                                        |
| Doctor Name        | Doctor's full name                                             |
| PRC License        | PRC license number                                             |
| Hospital           | Hospital or medical center                                     |
| Date               | Receipt date                                                   |
| Patient Name       | Patient's name                                                 |
| Total Amount (PHP) | Total amount due                                               |
| Signature          | Indicates whether an authorized signature section was detected |

---

# Installation

Clone the repository.

```bash
git clone https://github.com/clydefestin/Python-OCR-invoice-extractor.git
```

Navigate to the project directory.

```bash
cd Python-OCR-invoice-extractor
```

Create a virtual environment.

```bash
python -m venv .venv
```

Activate the environment.

Windows

```bash
.venv\Scripts\activate
```

Install the required packages.

```bash
pip install -r requirements.txt
```

---

# Running the Project

Place all receipt PDFs inside the `data` folder.

Run:

```bash
python src/main.py
```

The extracted data will be saved in:

```
output/extracted_receipts.xlsx
```

---

# Current Limitations

* OCR accuracy depends on the quality of the scanned receipts.
* Handwritten text is not supported.
* The parser uses regular expressions and is designed for doctor receipt formats used in this project.
* Different receipt layouts may require parser modifications.
* Signature detection is based on textual labels (e.g., "Authorized Physician" or "Authorized Signature") rather than detecting handwritten signatures.

---

# Future Improvements

Future versions of the project may include:

* Image denoising
* Adaptive thresholding
* Contrast enhancement
* Automatic deskewing
* OCR confidence scoring
* Handwritten text recognition
* Machine learning–based field extraction
* CSV and JSON export
* GUI interface
* REST API integration
* Support for additional receipt layouts

---
