# Log Compare

A Python tool for analyzing and comparing log files, generating comparative tables and exporting results to CSV/Excel.

## Features

- Parse log files and extract step durations
- Compare reference log to other logs in a folder
- Export comparison table to CSV/Excel
- Optional GUI for visualization

## Installation

```bash
pip install -r requirements.txt
```

## Usage

Run the GUI:

```bash
python -m log_compare.main
```

## Structure

- `log_compare/` - main package
- `GUI.py` - GUI application
- `parsing.py` - log parsing logic
- `pivot.py` - table construction and exporting
- `models.py` - data models
- `prefs.py` - user preferences

## License

MIT License