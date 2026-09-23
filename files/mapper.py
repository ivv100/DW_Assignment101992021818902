#!/usr/bin/env python3
"""
MAPPER  --  MapReduce framework (Hadoop-Streaming compatible)
---------------------------------------------------------------
Reads lines of:      SUBJECT_CODE <TAB> REGNO <TAB> GRADE
Emits key-value pairs:  SUBJECT_CODE_GRADE <TAB> 1

This can run:
  (a) locally, piped like a normal Unix filter:
        cat all_subjects_grades.txt | python3 mapper.py
  (b) on a real Hadoop cluster via Hadoop Streaming:
        hadoop jar hadoop-streaming.jar -mapper mapper.py ...
"""
import sys

VALID_GRADES = {"S", "A", "B", "C", "D", "E", "F"}

for line in sys.stdin:
    line = line.strip()
    if not line:
        continue

    parts = line.split("\t")
    if len(parts) != 3:
        continue

    subject, regno, grade = parts
    grade = grade.strip().upper()

    # Group anything outside S-F (I=absent, DT=detained, MP=malpractice)
    # into "OTHER" so every input row is still accounted for.
    bucket = grade if grade in VALID_GRADES else "OTHER"

    key = f"{subject}_{bucket}"
    print(f"{key}\t1")
