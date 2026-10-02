# Final QA and data-source notes
**Build date:** 30 September 2026

## Corrections
1. Removed the small header kicker that appeared clipped above the dashboard title and increased safe top spacing.
2. Changed the date-picker key to reset stale saved date selections from earlier app versions.
3. Separated vaccination data from the case/death table. The Vaccination Analysis page reads the dedicated vaccination API directly, so the older original JHU-style data does not suppress vaccination charts.
4. Overview now displays the global fully vaccinated count, with population coverage when available.
5. Reworked the UI into a restrained light analytics layout with readable chart labels, white panels and subtle depth. The interactive 3D country comparison remains available.
6. Preserved original raw CSV data and Power BI project assets.

## Data caveat
The OWID COVID catalog provides the current cases/deaths feed. The dedicated vaccination Grapher APIs provide historical vaccination observations; OWID's published series currently ends on 12 August 2024. The API URL is online, but this does not mean vaccination observations are current through today. Missing values are not imputed or fabricated.

## QA performed
- Python AST syntax parse.
- Static checks for the header, date widget reset, dedicated vaccination APIs, independent vaccination page, 3D comparison, branding, and navigation.
- ZIP integrity test and archive-content checks performed when packaging.
- No claim of third-party antivirus certification is made.
