# LOGCOMPARE

A desktop tool for analysing and comparing structured `.log` files step by step.

Built with Python and Tkinter. Parses timestamped log files, compares step durations across multiple runs against a reference, and exports colour-coded results to CSV and Excel.

---

## Features

- Compare any number of `.log` files against a reference log in one click
- Automatically isolates the first `DEBUT DE TEST … FIN DE TEST` block
- Optional delta columns showing the millisecond difference vs. the reference
- Colour-coded table (green / yellow / red) based on configurable thresholds
- Live step filter — type to filter rows instantly
- Show or hide any column; mandatory columns are protected
- Excel export with colours, bold headers, freeze panes, and an embedded scatter chart
- CSV auto-saved on every table build
- Matplotlib window for visualising test duration distribution across all files
- Last-used paths and settings remembered between sessions
- Midnight timestamp rollovers handled transparently

---

## Installation

Requirements: Python 3.10 or higher.

```bash
git clone https://github.com/your-username/LOGCOMPARE.git
cd LOGCOMPARE

python3 -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate

pip install -r requirements.txt
```

---

## Usage

```bash
python3 main.py
```

1. Select a reference `.log` file using the *Parcourir* button.
2. Select the folder containing all `.log` files to compare.
3. Optionally choose an output folder for CSV and Excel exports.
4. Click **Construire tableau** to build the comparison table and auto-save the CSV.
5. Adjust the *Seuil proche %* and *Seuil jaune %* thresholds, then click **Recolorer**.
6. Click **Extraire Excel** to export a fully formatted `.xlsx` workbook.
7. Click **Courbe durée test** to view the duration distribution plot.

---

## Log Format

Each step line must follow this structure:

```
[HH:MM:SS:mmm] ==> STEP NAME <optional rest of line
```

Example:

```
[08:12:34:001] ==> DEBUT DE TEST <
[08:12:34:456] ==> INIT SYSTEME < version 2.1
[08:12:37:890] ==> CHARGEMENT CONFIG <
[08:15:20:123] ==> FIN DE TEST <
DUREE DU TEST : 346 secondes
```

- `[HH:MM:SS:mmm]` — timestamp (hours, minutes, seconds, milliseconds)
- `==>` — step marker (one or more `=` followed by `>`)
- `STEP NAME` — label, normalised to upper case for matching
- `<` — end-of-name delimiter

Lines not matching the pattern are ignored. A *test block* is the sequence between `DEBUT DE TEST` and `FIN DE TEST`; only the first block is used by default.

---

## Colour Legend

| Colour | Meaning |
|--------|---------|
| Dark green | Duration exactly matches the reference |
| Light green | Deviation within the "Near" threshold (default 5 %) |
| Yellow | Deviation within the "Yellow" threshold (default 20 %) |
| Red | Deviation exceeds the yellow threshold |
| Grey | Step not found in this log file |
| Blue | TOTAL row |
| Light green background | Reference column |

---

## Configuration

All defaults are in [`constants.py`](constants.py):

| Constant | Default | Description |
|----------|---------|-------------|
| `DEFAULT_THRESH_NEAR` | `5.0` | "Close" threshold in percent |
| `DEFAULT_THRESH_YELLOW` | `20.0` | "Warning" threshold in percent |
| `INCLURE_INDEX_DEFAULT` | `True` | Show sequential index column by default |
| `AFFICHER_DELTAS_DEFAULT` | `False` | Show delta columns by default |
| `LIMITER_PREMIER_BLOC` | `True` | Use only the first test block |
| `NOM_DEBUT` | `"DEBUT DE TEST"` | Opening block step name |
| `NOM_FIN` | `"FIN DE TEST"` | Closing block step name |
| `SIGNATURE_ENABLED` | `False` | Enable optional branding |
| `SIGNATURE_TEXT` | `""` | Signature text shown in the UI and Excel metadata |

User preferences (last-used paths, threshold values) are saved to `~/.log_compare_prefs.json`.

---

## Project Structure

```
LOGCOMPARE/
├── main.py          # Entry point — launches the GUI
├── GUI.py           # Tkinter application (LogCompareApp)
├── parsing.py       # Log parsing, block detection, occurrence indexing
├── pivot.py         # Pivot table construction and CSV export
├── models.py        # Etape dataclass (one timestamped step)
├── constants.py     # Configurable constants and colour codes
├── prefs.py         # JSON preferences helpers
├── requirements.txt # Python dependencies
└── .gitignore
```

---

## Dependencies

| Package | Purpose | Min version |
|---------|---------|-------------|
| [openpyxl](https://openpyxl.readthedocs.io/) | Excel generation and chart embedding | 3.1.0 |
| [matplotlib](https://matplotlib.org/) | Duration distribution plot | 3.7.0 |
| [tksheet](https://github.com/ragardner/tksheet) | Spreadsheet widget inside Tkinter | 7.0.0 |

Tkinter ships with the Python standard library.

---

## License

MIT License