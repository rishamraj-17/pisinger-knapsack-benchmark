import pandas as pd
import os

# Ensure output directory exists
os.makedirs('outputs/tables', exist_ok=True)

# 1. Build Table 2 (OLS Metrics)
df_ols = pd.read_csv('python/modeling/output/results/ols_metrics_aggregated.csv')

def get_ols_row(algo, outcome, df):
    # M1 full sample adj R2
    m1_fs = df[(df['cv_scheme']=='full_sample') & (df['algorithm']==algo) & (df['response']==outcome) & (df['model']=='M1')]['adj_r_squared'].values[0]
    # M2 full sample adj R2
    m2_fs = df[(df['cv_scheme']=='full_sample') & (df['algorithm']==algo) & (df['response']==outcome) & (df['model']=='M2')]['adj_r_squared'].values[0]
    # M2 5-fold R2
    m2_5f = df[(df['cv_scheme']=='5-fold') & (df['algorithm']==algo) & (df['response']==outcome) & (df['model']=='M2')]['r_squared_mean'].values[0]
    # M2 LOFO R2
    m2_lofo = df[(df['cv_scheme']=='LOFO') & (df['algorithm']==algo) & (df['response']==outcome) & (df['model']=='M2')]['r_squared_mean'].values[0]
    
    delta_r2 = m2_fs - m1_fs
    
    # Formatting
    m1_fs_str = f"{m1_fs:.3f}"
    m2_fs_str = f"{m2_fs:.3f}"
    delta_str = f"+{delta_r2:.3f}" if delta_r2 > 0.001 else ("$\\approx 0$" if delta_r2 > -0.001 else f"{delta_r2:.3f}")
    m2_5f_str = f"{m2_5f:.3f}"
    
    # LOFO formatting with daggers for negative
    lofo_str = f"{m2_lofo:.3f}"
    if m2_lofo < 0:
        lofo_str = f"{m2_lofo:.1f}\\textsuperscript{{$\\dagger$}}"
    elif algo == "DP" and outcome == "log_time_millis":
        lofo_str = f"+{m2_lofo:.3f}\\textsuperscript{{$\\ddagger$}}"
    elif m2_lofo > 0:
        lofo_str = f"+{m2_lofo:.3f}"
        
    return f"{m1_fs_str} & {m2_fs_str} & {delta_str} & {m2_5f_str} & {lofo_str}"

rows = [
    "Greedy & \\texttt{log\\_time\\_millis} & " + get_ols_row("Greedy", "log_time_millis", df_ols) + " \\\\",
    "Dynamic Programming & \\texttt{log\\_time\\_millis} & " + get_ols_row("DP", "log_time_millis", df_ols) + " \\\\",
    "Dynamic Programming & \\texttt{log\\_memory\\_mb} & " + get_ols_row("DP", "log_memory_mb", df_ols) + " \\\\",
    "Branch \\& Bound & \\texttt{log\\_time\\_millis} & " + get_ols_row("BandB", "log_time_millis", df_ols) + " \\\\",
    "Branch \\& Bound & \\texttt{log\\_nodes\\_explored} & " + get_ols_row("BandB", "log_nodes_explored", df_ols) + " \\\\"
]

table2_tex = """\\begin{table}[t]
\\centering
\\caption{Full-sample $R^2$, 5-fold CV $R^2$, and LOFO mean $R^2$ for baseline (M1) and augmented (M2) OLS models. The three protocols tell qualitatively different stories: full-sample and 5-fold CV are close; LOFO exposes structural distribution shift.}
\\label{tab:ols_metrics}
\\begin{tabular}{llccccc}
\\toprule
\\textbf{Algorithm} & \\textbf{Outcome} & \\textbf{Adj.~$R^2$ M1} & \\textbf{Adj.~$R^2$ M2} & \\textbf{$\\Delta R^2_{adj}$} & \\textbf{5-Fold $R^2$ M2} & \\textbf{LOFO $R^2$ M2} \\\\
\\midrule
""" + "\n".join(rows) + """
\\bottomrule
\\end{tabular}
{\\small $\\dagger$~LOFO $R^2 < 0$: model performs worse than predicting the family mean. $\\ddagger$~DP log\\_time LOFO is positive but driven by one family; others vary widely.}
\\end{table}"""

with open('outputs/tables/table_ols_metrics.tex', 'w') as f:
    f.write(table2_tex)

# 2. Build Table 3 (Fractional Logit Metrics)
df_flogit = pd.read_csv('python/modeling/output/results/flogit_metrics_aggregated.csv')

def get_flogit_row(algo, outcome, df):
    m1_fs = df[(df['cv_scheme']=='full_sample') & (df['algorithm']==algo) & (df['response']==outcome) & (df['model']=='M1')]['pseudo_r_squared'].values[0]
    m2_fs = df[(df['cv_scheme']=='full_sample') & (df['algorithm']==algo) & (df['response']==outcome) & (df['model']=='M2')]['pseudo_r_squared'].values[0]
    delta = m2_fs - m1_fs
    return f"{m1_fs:.3f} & {m2_fs:.3f} & +{delta:.3f}"

flogit_rows = [
    "Greedy & \\texttt{optimality\\_gap} & " + get_flogit_row("Greedy", "optimality_gap", df_flogit) + " \\\\",
    "Dynamic Programming & \\texttt{fill\\_rate} & " + get_flogit_row("DP", "fill_rate", df_flogit) + " \\\\"
]

table3_tex = """\\begin{table}[t]
\\centering
\\caption{Full-sample and LOFO pseudo-$R^2$ for baseline (M1) and augmented (M2) Fractional Logit models for bounded proportional outcomes}
\\label{tab:flogit_metrics}
\\begin{tabular}{llcccc}
\\toprule
\\textbf{Algorithm} & \\textbf{Outcome} & \\textbf{Pseudo-$R^2$ (M1)} & \\textbf{Pseudo-$R^2$ (M2)} & \\textbf{$\\Delta$pseudo-$R^2$} \\\\
\\midrule
""" + "\n".join(flogit_rows) + """
\\bottomrule
\\end{tabular}
\\end{table}"""

with open('outputs/tables/table_flogit_metrics.tex', 'w') as f:
    f.write(table3_tex)

print("Generated regression tables successfully.")
