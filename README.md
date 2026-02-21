# Photo Organizer

## What it does
Organizes photos into folders based on date taken/created.

## How to run
### Dry run (default)
photo-organizer SRC OUT

### Execute (makes changes)
photo-organizer --do-it SRC OUT

### Output format
OUT/YYYY/YYYY-MM/filename
## Setup
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e requirements.txt

## Notes
- CLI entry point is stable; run `photo-organizer --help` for options.
- Local-only
- No data leaves the machine
