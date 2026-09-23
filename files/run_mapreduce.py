"""
======================================================================
 ASSIGNMENT 2 : MapReduce -- Student count per Grade (S,A,B,C,D,E,F)
======================================================================
 Sample data : Previous semester final exam grade-sheets (9 subjects,
               Sikkim Manipal University, May/June 2026 exams)
 Framework   : MapReduce (mapper.py -> shuffle/sort -> reducer.py),
               executed exactly as Hadoop Streaming would run it,
               just on a single machine instead of a cluster.
======================================================================
"""

import subprocess
import pandas as pd
import matplotlib.pyplot as plt

from prepare_data import main as prepare_main

GRADES = ["S", "A", "B", "C", "D", "E", "F"]

# ----------------------------------------------------------------
# STEP 1: Build the combined sample dataset from the raw grade sheets
# ----------------------------------------------------------------
print("=" * 70)
print("STEP 1: Preparing sample data from previous semester result sheets")
print("=" * 70)
subject_titles, footer_stats = prepare_main()

# ----------------------------------------------------------------
# STEP 2: Run the REAL MapReduce pipeline
#         mapper.py  ->  sort (shuffle)  ->  reducer.py
#         (identical to: cat data | python3 mapper.py | sort | python3 reducer.py)
# ----------------------------------------------------------------
print("\n" + "=" * 70)
print("STEP 2: Running Map -> Shuffle/Sort -> Reduce pipeline")
print("=" * 70)

with open("all_subjects_grades.txt", "rb") as infile:
    map_proc = subprocess.run(["python3", "mapper.py"], stdin=infile, capture_output=True)

sort_proc = subprocess.run(["sort"], input=map_proc.stdout, capture_output=True)

reduce_proc = subprocess.run(["python3", "reducer.py"], input=sort_proc.stdout, capture_output=True)

reducer_output = reduce_proc.stdout.decode().strip().splitlines()
print(f"Mapper emitted   : {len(map_proc.stdout.decode().strip().splitlines())} key-value pairs")
print(f"Reducer produced : {len(reducer_output)} aggregated (subject, grade) keys")

# ----------------------------------------------------------------
# STEP 3: Turn the reducer's flat "SUBJECT_GRADE <TAB> count" output
#         into a Subject x Grade pivot table
# ----------------------------------------------------------------
counts = {}
for line in reducer_output:
    key, value = line.split("\t")
    subject, bucket = key.rsplit("_", 1)
    counts.setdefault(subject, {}).setdefault(bucket, 0)
    counts[subject][bucket] += int(value)

rows = []
for subject in sorted(counts):
    row = {"Subject": subject, "Title": subject_titles.get(subject, "")}
    for g in GRADES:
        row[g] = counts[subject].get(g, 0)
    row["Others (I/DT/MP)"] = counts[subject].get("OTHER", 0)
    row["Total"] = sum(row[g] for g in GRADES) + row["Others (I/DT/MP)"]
    rows.append(row)

report = pd.DataFrame(rows)

# Grand total row (2nd-level reduce: aggregate across ALL subjects)
grand_total = {"Subject": "ALL SUBJECTS", "Title": "-"}
for g in GRADES:
    grand_total[g] = report[g].sum()
grand_total["Others (I/DT/MP)"] = report["Others (I/DT/MP)"].sum()
grand_total["Total"] = report["Total"].sum()
report_with_total = pd.concat([report, pd.DataFrame([grand_total])], ignore_index=True)

# ----------------------------------------------------------------
# STEP 4: Sanity-check the MapReduce result against each file's own
#         footer statistics (No. of students appeared / absentees / ...)
# ----------------------------------------------------------------
print("\n" + "=" * 70)
print("STEP 3: Validating MapReduce output against source-file footers")
print("=" * 70)
all_ok = True
for _, row in report.iterrows():
    subj = row["Subject"]
    graded_sum = sum(row[g] for g in GRADES)
    others_sum = row["Others (I/DT/MP)"]
    f = footer_stats[subj]
    expected_others = (f["absentees"] or 0) + (f["malpractices"] or 0) + (f["detentions"] or 0)
    ok_appeared = (f["appeared"] is None) or (graded_sum == f["appeared"])
    ok_others = others_sum == expected_others
    all_ok &= ok_appeared and ok_others
    status = "OK" if (ok_appeared and ok_others) else "MISMATCH"
    print(f"{subj:10s} graded={graded_sum:4d} (appeared={f['appeared']})  "
          f"others={others_sum:3d} (AB+MP+DT={expected_others:3d})  -> {status}")
print("\nAll subjects validated OK" if all_ok else "\nSome subjects need review")

# ----------------------------------------------------------------
# STEP 5: Save the report + print it
# ----------------------------------------------------------------
report_with_total.to_csv("grade_distribution_by_subject.csv", index=False)

pd.set_option("display.width", 120)
print("\n" + "=" * 70)
print("FINAL RESULT: Number of students per grade, per subject")
print("=" * 70)
print(report_with_total.drop(columns=["Title"]).to_string(index=False))

# ----------------------------------------------------------------
# STEP 6: Visualise as a stacked bar chart
# ----------------------------------------------------------------
plot_df = report.set_index("Subject")[GRADES]
colors = ["#2e7d32", "#66bb6a", "#9ccc65", "#ffca28", "#ffa726", "#ef5350", "#b71c1c"]

ax = plot_df.plot(kind="bar", stacked=True, figsize=(10, 6), color=colors)
plt.title("Student Grade Distribution per Subject (MapReduce output)")
plt.xlabel("Subject Code")
plt.ylabel("Number of Students")
plt.xticks(rotation=45, ha="right")
plt.legend(title="Grade", bbox_to_anchor=(1.02, 1), loc="upper left")
plt.tight_layout()
plt.savefig("grade_distribution_chart.png", dpi=150)
print("\nSaved: grade_distribution_by_subject.csv, grade_distribution_chart.png")
