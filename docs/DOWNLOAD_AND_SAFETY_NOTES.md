# Download and safety notes

This package contains the project source code, documentation, Power BI assets, and extracted CSV datasets.
For compatibility with antivirus scanners, it does not embed nested ZIP archives or a Windows batch launcher.
The original source data is retained as extracted CSV files in `data/raw/`; the processed analytical data is in `data/processed/`.

The project does not include executable binaries, installers, macros, or browser extensions.
Python source files are plain text. Review them before running, and install dependencies only from the official Python package index using `pip`.

Run from the extracted project folder:
```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python -m streamlit run app/app.py
```

Antivirus results depend on the user's device, security product, and its definitions. This package has been repackaged to remove nested archives and the batch launcher, but no claim of a third-party antivirus certification is made.
