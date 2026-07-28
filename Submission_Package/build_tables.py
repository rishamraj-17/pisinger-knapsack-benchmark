import pandas as pd
import os

OUT_DIR = "/home/risham-raj-byahut/IdeaProjects/Emperical_Comparision/Submission_Package/tables"

ARCHIVE = "/home/risham-raj-byahut/IdeaProjects/Emperical_Comparision/Phase_3_3_Modeling/Phase3_Archive/output"


def generate_table_1():
    """Table 1: Execution predictor counts by algorithm."""
    tex = (
        "\\begin{tabular}{ll}\n"
        "\\toprule\n"
        "\\textbf{Algorithm} & \\textbf{Number of execution predictors} \\\\\n"
        "\\midrule\n"
        "Greedy & 5 \\\\\n"
        "Dynamic Programming & 10 \\\\\n"
        "Branch and Bound & 24 \\\\\n"
        "\\bottomrule\n"
        "\\end{tabular}\n"
    )
    with open(os.path.join(OUT_DIR, "Table_1.tex"), "w") as f:
        f.write(tex)
    print("Table 1 generated.")


def generate_table_2():
    """Table 2: OLS baseline (M1) and augmented (M2) full-sample R2 values."""
    df = pd.read_csv(f"{ARCHIVE}/results/ols_metrics_aggregated.csv")
    df_fs = df[df['cv_scheme'] == 'full_sample'].copy()

    rows = [
        ("Greedy",  "log\\_time\\_millis"),
        ("DP",      "log\\_time\\_millis"),
        ("DP",      "log\\_memory\\_mb"),
        ("BandB",   "log\\_time\\_millis"),
        ("BandB",   "log\\_nodes\\_explored"),
    ]

    tex = (
        "\\begin{tabular}{llcccc}\n"
        "\\toprule\n"
        "\\textbf{Algorithm} & \\textbf{Outcome} & "
        "\\textbf{$R^2$ (M1)} & \\textbf{Adj.~$R^2$ (M1)} & "
        "\\textbf{$R^2$ (M2)} & \\textbf{Adj.~$R^2$ (M2)} \\\\\n"
        "\\midrule\n"
    )

    algo_map = {"Greedy": "Greedy", "DP": "DP", "BandB": "BandB"}
    resp_map = {"log\\_time\\_millis":      "log_time_millis",
                "log\\_memory\\_mb":        "log_memory_mb",
                "log\\_nodes\\_explored":   "log_nodes_explored"}

    for algo_tex, resp_tex in rows:
        algo_raw = algo_map[algo_tex]
        resp_raw = resp_map[resp_tex]
        m1 = df_fs[(df_fs['algorithm'] == algo_raw) &
                   (df_fs['response']  == resp_raw) &
                   (df_fs['model']     == 'M1')]
        m2 = df_fs[(df_fs['algorithm'] == algo_raw) &
                   (df_fs['response']  == resp_raw) &
                   (df_fs['model']     == 'M2')]
        r2_m1  = float(m1['r_squared'].iloc[0])
        ar2_m1 = float(m1['adj_r_squared'].iloc[0])
        r2_m2  = float(m2['r_squared'].iloc[0])
        ar2_m2 = float(m2['adj_r_squared'].iloc[0])
        display_algo = algo_tex.replace("DP", "Dynamic Programming").replace("BandB", "Branch \\& Bound")
        tex += (f"{display_algo} & \\texttt{{{resp_tex}}} & "
                f"{r2_m1:.3f} & {ar2_m1:.3f} & {r2_m2:.3f} & {ar2_m2:.3f} \\\\\n")

    tex += "\\bottomrule\n\\end{tabular}\n"
    with open(os.path.join(OUT_DIR, "Table_2.tex"), "w") as f:
        f.write(tex)
    print("Table 2 generated.")


def generate_table_3():
    """Table 3: Fractional Logit pseudo-R2 for bounded outcomes."""
    df = pd.read_csv(f"{ARCHIVE}/results/flogit_metrics_aggregated.csv")
    df_fs = df[df['cv_scheme'] == 'full_sample'].copy()

    rows = [
        ("Greedy", "optimality_gap"),
        ("DP",     "fill_rate"),
    ]

    tex = (
        "\\begin{tabular}{llcc}\n"
        "\\toprule\n"
        "\\textbf{Algorithm} & \\textbf{Outcome} & "
        "\\textbf{Pseudo-$R^2$ (M1)} & \\textbf{Pseudo-$R^2$ (M2)} \\\\\n"
        "\\midrule\n"
    )

    display_algo = {"Greedy": "Greedy", "DP": "Dynamic Programming"}

    for algo_raw, resp_raw in rows:
        m1 = df_fs[(df_fs['algorithm'] == algo_raw) &
                   (df_fs['response']  == resp_raw) &
                   (df_fs['model']     == 'M1')]
        m2 = df_fs[(df_fs['algorithm'] == algo_raw) &
                   (df_fs['response']  == resp_raw) &
                   (df_fs['model']     == 'M2')]
        pr2_m1 = float(m1['pseudo_r_squared'].iloc[0])
        pr2_m2 = float(m2['pseudo_r_squared'].iloc[0])
        resp_tex = resp_raw.replace('_', '\\_')
        tex += (f"{display_algo[algo_raw]} & \\texttt{{{resp_tex}}} & "
                f"{pr2_m1:.3f} & {pr2_m2:.3f} \\\\\n")

    tex += "\\bottomrule\n\\end{tabular}\n"
    with open(os.path.join(OUT_DIR, "Table_3.tex"), "w") as f:
        f.write(tex)
    print("Table 3 generated.")


def generate_table_4():
    """Table 4: Top-10 standardized coefficients (absolute) for B&B log_nodes_explored M2."""
    df = pd.read_csv(f"{ARCHIVE}/diagnostics/std_beta_BandB_log_nodes_explored_M2.csv")
    df['abs_coef'] = df['coefficient'].abs()
    df_sorted = df.sort_values('abs_coef', ascending=False).reset_index(drop=True)
    top10 = df_sorted.head(10)

    tex = (
        "\\begin{tabular}{lcc}\n"
        "\\toprule\n"
        "\\textbf{Predictor} & \\textbf{Std.~$\\beta$} & \\textbf{$|\\beta|$} \\\\\n"
        "\\midrule\n"
    )
    for _, row in top10.iterrows():
        pred_tex = row['predictor'].replace('_', '\\_')
        tex += f"\\texttt{{{pred_tex}}} & {row['coefficient']:.3f} & {row['abs_coef']:.3f} \\\\\n"

    tex += "\\bottomrule\n\\end{tabular}\n"
    with open(os.path.join(OUT_DIR, "Table_4.tex"), "w") as f:
        f.write(tex)
    print("Table 4 generated.")


if __name__ == "__main__":
    generate_table_1()
    generate_table_2()
    generate_table_3()
    generate_table_4()
    print("All tables generated successfully.")
