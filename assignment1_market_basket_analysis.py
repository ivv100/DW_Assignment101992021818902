"""
======================================================================
 ASSIGNMENT 1 : Market Basket Analysis (MBA) on Real-World Data
======================================================================
 Technique   : Apriori Algorithm -> Frequent Itemsets -> Association Rules
 Metrics     : Support, Confidence, Lift
 Library     : mlxtend  (pip install mlxtend)
 Dataset     : Market_Basket_Optimisation.csv
               7,501 REAL transactions recorded over one week at a
               grocery retail store. Each row = one customer's basket
               (a variable-length list of items bought together).
               Source: https://github.com/Karan-Malik/Apriori-Eclat
======================================================================
"""

import pandas as pd
import matplotlib.pyplot as plt
from mlxtend.preprocessing import TransactionEncoder
from mlxtend.frequent_patterns import apriori, association_rules

# ----------------------------------------------------------------
# STEP 1: Load the real-world transactional data
# ----------------------------------------------------------------
# The file has NO header row, and each row has a different number of
# items, so empty cells become NaN -> we clean these in Step 2.
DATA_FILE = "Market_Basket_Optimisation.csv"
data = pd.read_csv(DATA_FILE, header=None)
print(f"Loaded {data.shape[0]} real transactions (up to {data.shape[1]} items each)\n")

# ----------------------------------------------------------------
# STEP 2: Convert every row into a clean Python list of items
# ----------------------------------------------------------------
transactions = []
for i in range(data.shape[0]):
    row = [str(item) for item in data.iloc[i].tolist() if str(item) != "nan"]
    transactions.append(row)

print("Sample transaction #1:", transactions[0])
print("Sample transaction #3:", transactions[2], "\n")

# ----------------------------------------------------------------
# STEP 3: One-Hot Encode the transactions (required by mlxtend)
# ----------------------------------------------------------------
te = TransactionEncoder()
te_array = te.fit(transactions).transform(transactions)
df = pd.DataFrame(te_array, columns=te.columns_)
print(f"Encoded matrix -> {df.shape[0]} transactions x {df.shape[1]} unique items\n")

# ----------------------------------------------------------------
# STEP 4: Mine FREQUENT ITEMSETS using the Apriori algorithm
# ----------------------------------------------------------------
MIN_SUPPORT = 0.02   # an itemset must appear in at least 2% of all baskets
frequent_itemsets = apriori(df, min_support=MIN_SUPPORT, use_colnames=True)
frequent_itemsets["length"] = frequent_itemsets["itemsets"].apply(len)
frequent_itemsets = frequent_itemsets.sort_values("support", ascending=False)

print(f"Frequent itemsets found (support >= {MIN_SUPPORT}): {len(frequent_itemsets)}")
print(frequent_itemsets.head(10).to_string(index=False), "\n")

# ----------------------------------------------------------------
# STEP 5: Generate ASSOCIATION RULES (Support, Confidence, Lift)
# ----------------------------------------------------------------
rules = association_rules(frequent_itemsets, metric="lift", min_threshold=1.0)
rules = rules.sort_values("lift", ascending=False)

print(f"Association rules found (lift >= 1.0): {len(rules)}")
print(
    rules[["antecedents", "consequents", "support", "confidence", "lift"]]
    .head(10)
    .to_string(index=False),
    "\n",
)

# ----------------------------------------------------------------
# STEP 6: Save results so they can be attached to the assignment report
# ----------------------------------------------------------------
frequent_itemsets.to_csv("frequent_itemsets.csv", index=False)
rules.to_csv("association_rules.csv", index=False)
print("Saved: frequent_itemsets.csv, association_rules.csv")

# ----------------------------------------------------------------
# STEP 7: Visualise the Top-10 frequent itemsets
# ----------------------------------------------------------------
top10 = frequent_itemsets.head(10).iloc[::-1]
labels = [", ".join(sorted(s)) for s in top10["itemsets"]]

plt.figure(figsize=(9, 6))
plt.barh(labels, top10["support"], color="seagreen")
plt.xlabel("Support")
plt.title("Top 10 Frequent Itemsets - Market Basket Analysis")
plt.tight_layout()
plt.savefig("top10_frequent_itemsets.png", dpi=150)
print("Saved chart: top10_frequent_itemsets.png")
