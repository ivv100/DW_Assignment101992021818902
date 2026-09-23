# Assignment 2 — MapReduce: Student Count per Grade (S,A,B,C,D,E,F)

**Goal:** Apply the MapReduce framework to calculate the number of students
in each grade category (S, A, B, C, D, E, F) using previous-semester final
exam results, for all subjects.

**Sample data:** 9 previous-semester subject grade sheets (Sikkim Manipal
University, May/June 2026 exams), each containing REGNO and final GRADE per
student — 1,235 student records across 9 subjects in total.

## Files
| File | Role |
|---|---|
| `raw/*.txt` | Original grade sheets, one per subject (input) |
| `prepare_data.py` | Parses the raw sheets -> `all_subjects_grades.txt` (`SUBJECT<TAB>REGNO<TAB>GRADE`) |
| `mapper.py` | **Map** step — emits `SUBJECT_GRADE <TAB> 1` for every student row |
| `reducer.py` | **Reduce** step — sums identical keys after the shuffle/sort |
| `run_mapreduce.py` | Driver: runs prepare -> map -> sort -> reduce -> builds the final report + chart |
| `grade_distribution_by_subject.csv` | Output: students per grade, per subject (+ grand total row) |
| `grade_distribution_chart.png` | Stacked bar chart of the same result |

## How the MapReduce logic works
1. **Map**: each line `SUBJECT<TAB>REGNO<TAB>GRADE` -> key `SUBJECT_GRADE`, value `1`
   (grades outside S–F, i.e. `I`=absent, `DT`=detention, `MP`=malpractice, are
   bucketed as `OTHER` so no row is silently dropped).
2. **Shuffle/Sort**: identical keys are grouped together (plain Unix `sort`).
3. **Reduce**: sums the `1`s for each key -> total students with that grade in that subject.
4. A final aggregation step sums every subject's row to also give the combined
   total across **all** subjects (bottom "ALL SUBJECTS" row).

Every subject's computed total was cross-checked against that file's own
footer ("No. of students appeared", "No. of Absentees", etc.) — all 9 matched.

## Results summary
Combined across all 9 subjects (1,235 student-subject records):

| S | A | B | C | D | E | F | Others (absent/detained/malpractice) | Total |
|---|---|---|---|---|---|---|---|---|
| 43 | 153 | 263 | 278 | 214 | 91 | 104 | 89 | 1,235 |

- **GN201B1** (Universal Human Values II) is the largest class — 449 students,
  mostly B/C grades, only 14 F's.
- **MA206B1** (Probability, Statistics & Stochastic Processes) was the
  toughest paper — 84 F's out of 367 students.
- **IT220A2** (Intro to Cyber Security) had the strongest results — 0 F's.

## Run it locally
```bash
pip install pandas matplotlib
python3 run_mapreduce.py
```

You can also run just the Map/Reduce steps as a raw Unix pipeline (this is
exactly what Hadoop Streaming does under the hood):
```bash
cat all_subjects_grades.txt | python3 mapper.py | sort | python3 reducer.py
```

## Running it on a real Hadoop cluster
`mapper.py` / `reducer.py` are Hadoop-Streaming compatible as-is:
```bash
hadoop jar $HADOOP_HOME/share/hadoop/tools/lib/hadoop-streaming-*.jar \
  -input   /user/you/all_subjects_grades.txt \
  -output  /user/you/grade_counts \
  -mapper  mapper.py \
  -reducer reducer.py \
  -file    mapper.py \
  -file    reducer.py
```
