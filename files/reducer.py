#!/usr/bin/env python3
"""
REDUCER  --  MapReduce framework (Hadoop-Streaming compatible)
---------------------------------------------------------------
Reads SORTED key-value pairs:   SUBJECT_CODE_GRADE <TAB> 1
Sums consecutive identical keys (the standard streaming-reducer pattern,
relying on the shuffle/sort step to group identical keys together) and
emits:                          SUBJECT_CODE_GRADE <TAB> total_count
"""
import sys

current_key = None
current_count = 0

for line in sys.stdin:
    line = line.strip()
    if not line:
        continue

    key, value = line.split("\t", 1)
    value = int(value)

    if key == current_key:
        current_count += value
    else:
        if current_key is not None:
            print(f"{current_key}\t{current_count}")
        current_key = key
        current_count = value

# flush the last key
if current_key is not None:
    print(f"{current_key}\t{current_count}")
