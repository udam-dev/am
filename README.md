# Attendance Report App

A simple Flask application for importing student names from an Excel file, marking attendance, and exporting a Khmer-language PDF attendance report.

## Features

- Upload an Excel file containing student names
- Display imported students on the web page
- Mark students as present, absent, or leave
- Generate a downloadable PDF attendance report with Khmer date formatting

## Requirements

- Python 3.9+
- Flask
- pandas
- openpyxl
- playwright

## Setup

1. Create and activate a virtual environment:

```bash
python -m venv venv
venv\Scripts\activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Install Playwright browsers:

```bash
playwright install chromium
```

## Run the app

```bash
python app.py
```

Then open `http://127.0.0.1:5000/` in your browser.

## Usage

1. Prepare an Excel file with a column named **ឈ្មោះសិស្ស** (student name).
2. Upload the file on the main page.
3. Mark attendance and submit to download the PDF report.

## Notes

- The app uses `pandas.read_excel`, so Excel files should be in `.xlsx` format or another supported format.
- The generated PDF uses Playwright with Chromium.
