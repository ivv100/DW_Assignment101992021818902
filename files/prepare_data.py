"""
Parses the raw university grade-sheet .txt files (one per subject) and
produces ONE clean, tab-separated dataset:

    SUBJECT_CODE <TAB> REGNO <TAB> GRADE

This combined file is the "sample data" that the MapReduce job (mapper.py /
reducer.py) will actually consume -- exactly like raw result sheets would
first be loaded into HDFS before a real Hadoop job processes them.
"""

import os
import re
import glob

RAW_DIR = "raw"
OUTPUT_FILE = "all_subjects_grades.txt"

ROW_PATTERN = re.compile(r"^\d{6,}\s")          # a data row starts with a REGNO
CODE_PATTERN = re.compile(r"Subject Code\s*:\s*(\S+)")
TITLE_PATTERN = re.compile(r"Subject Title\s*:\s*(.+)")
STAT_PATTERNS = {
    "absentees": re.compile(r"No\. of Absentees\s*=\s*(\d+)"),
    "malpractices": re.compile(r"No\. of Malpractices\s*=\s*(\d+)"),
    "detentions": re.compile(r"No\. of Detentions\s*=\s*(\d+)"),
    "appeared": re.compile(r"No\. of students appeared\s*=\s*(\d+)"),
}


def parse_grade_sheet(filepath):
    """Extract (subject_code, subject_title, [(regno, grade), ...], footer_stats)."""
    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        text = f.read()

    code_match = CODE_PATTERN.search(text)
    subject_code = code_match.group(1).strip() if code_match else \
        os.path.splitext(os.path.basename(filepath))[0]

    title_match = TITLE_PATTERN.search(text)
    subject_title = title_match.group(1).strip() if title_match else subject_code

    records = []
    for line in text.splitlines():
        line = line.strip()
        if ROW_PATTERN.match(line):
            parts = line.split()
            regno, grade = parts[0], parts[-1].upper()
            records.append((regno, grade))

    footer_stats = {}
    for key, pattern in STAT_PATTERNS.items():
        m = pattern.search(text)
        footer_stats[key] = int(m.group(1)) if m else None

    return subject_code, subject_title, records, footer_stats


def main():
    files = sorted(glob.glob(os.path.join(RAW_DIR, "*.txt")))
    if not files:
        raise SystemExit(f"No .txt files found in {RAW_DIR}/")

    subject_titles = {}
    footer_by_subject = {}

    with open(OUTPUT_FILE, "w", encoding="utf-8") as out:
        for path in files:
            subject_code, subject_title, records, footer = parse_grade_sheet(path)
            subject_titles[subject_code] = subject_title
            footer_by_subject[subject_code] = footer
            for regno, grade in records:
                out.write(f"{subject_code}\t{regno}\t{grade}\n")
            print(f"{subject_code:10s} {subject_title[:45]:45s} -> {len(records):4d} rows")

    print(f"\nCombined dataset written to: {OUTPUT_FILE}")
    return subject_titles, footer_by_subject


if __name__ == "__main__":
    main()
