import re
import os

draft_path = "paper/draft.md"
with open(draft_path, "r") as f:
    content = f.read()

# Replace general numbers
content = content.replace("750 instances", "3,000 instances per mode (6,000 total)")
content = content.replace("2,250 algorithm runs", "18,000 algorithm runs")
content = content.replace("30 seeds per (n, family)", "100 seeds per (n, family)")
content = content.replace("30 seeds", "100 seeds")
content = content.replace("n=500", "n=1000")
content = content.replace("n = 500", "n = 1000")
content = content.replace("250,000 for n=1000", "500,000 for n=1000")  # Adjust for new n
content = content.replace("n \\in \\{20, 50, 100, 200, 500\\}", "n \\in \\{20, 50, 100, 200, 500, 1000\\}")
content = content.replace("W = 1000", "W = 1000 (fixed) and W = 0.5 \\sum w_i (scaled)")
content = content.replace("1.00 MB for Greedy at n \\ge 50", "1.00 MB for Greedy at n \\ge 50 (and at n=1000)")

# Add section about Scaled Capacity vs Fixed Capacity
new_section = """
### 6.8 DP Scaling: Fixed vs Scaled Capacity

The results above focus on the fixed capacity mode ($W=1000$). In this mode, DP's runtime scales linearly with $n$ because the maximum work is $O(nW) = O(1000n) = O(n)$. 

However, in the scaled capacity mode where $W = 0.5 \\sum w_i$, capacity grows proportionally with $n$. Since item weights are drawn from $U(1, 1000)$, the expected capacity is approximately $250n$. Consequently, the total work $nW$ scales quadratically: $O(n(250n)) = O(n^2)$. 

This exposes a critical limitation of DP that is hidden when $W$ is fixed. While DP remains exact, its practical utility diminishes for very large $n$ when capacity scales with the problem size.
"""

if "6.8 DP Scaling" not in content:
    content = content.replace("## 7. Discussion", new_section + "\n## 7. Discussion")

# Replace tables with \input directives
# Table 1
t1_pattern = re.compile(r"\*\*Table 1\*\*: Mean execution time.*?\| B&B \|.*?\|\n", re.DOTALL)
content = t1_pattern.sub(r"**Table 1**: Mean execution time (ms) at n=1000 with 95% bootstrap CI\n\n\\input{tables/fixed_table_time_max_n}\n\\input{tables/scaled_table_time_max_n}\n", content)

# Table 2
t2_pattern2 = re.compile(r"\*\*Table 2\*\*: Greedy optimality gap statistics.*?\*\*Why gap depends on correlation structure\.\*\*", re.DOTALL)
content = t2_pattern2.sub(r"**Table 2**: Greedy optimality gap statistics (all n pooled)\n\n\\input{tables/fixed_table_greedy_gap}\n\\input{tables/scaled_table_greedy_gap}\n\n**Why gap depends on correlation structure.**", content)

# Table 3
t3_pattern = re.compile(r"\*\*Table 3\*\*: B&B nodes explored.*?\*\*Why bound tightness varies by family\.\*\*", re.DOTALL)
content = t3_pattern.sub(r"**Table 3**: B&B nodes explored (all n pooled)\n\n\\input{tables/fixed_table_bb_nodes}\n\\input{tables/scaled_table_bb_nodes}\n\n**Why bound tightness varies by family.**", content)

# Table 4
t4_pattern = re.compile(r"\*\*Table 4\*\*: B&B execution time \(ms\) at n=1000.*?\*\*Runtime-node correspondence\.\*\*", re.DOTALL)
content = t4_pattern.sub(r"**Table 4**: B&B execution time (ms) at n=1000 with outlier analysis (95% bootstrap CI)\n\n\\input{tables/fixed_table_bb_time}\n\\input{tables/scaled_table_bb_time}\n\n**Runtime-node correspondence.**", content)

# Table 5
t5_pattern = re.compile(r"\*\*Table 5\*\*: DP mean time \(ms\) by n and family.*?\*\*Why DP runtime is linear in n at fixed W\.\*\*", re.DOTALL)
content = t5_pattern.sub(r"**Table 5**: DP mean time (ms) by n and family with 95% bootstrap CI\n\n\\input{tables/fixed_table_dp_scaling}\n\\input{tables/scaled_table_dp_scaling}\n\n**Why DP runtime is linear in n at fixed W.**", content)

with open(draft_path, "w") as f:
    f.write(content)

print("Updated draft.md successfully.")
