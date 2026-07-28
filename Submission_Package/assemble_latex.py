import os, re

ARTIFACT_DIR = "/home/risham-raj-byahut/.gemini/antigravity/brain/cbb6daa1-05c2-4856-99ca-e19d4507cba1"
OUTPUT_FILE  = "/home/risham-raj-byahut/IdeaProjects/Emperical_Comparision/Submission_Package/manuscript.tex"

# Maps the top-level section header text to (section title, command)
SECTION_MAP = {
    "Section 1: Introduction":          ("Introduction",  r"\section"),
    "Section 2: Related Work":          ("Related Work",  r"\section"),
    "Section 3: Methodology":           ("Methodology",   r"\section"),
    "Section 4: Results":               ("Results",       r"\section"),
    "Section 5: Discussion":            ("Discussion",    r"\section"),
    "Section 6: Limitations":           ("Limitations",   r"\section"),
    "Section 7: Conclusion":            ("Conclusion",    r"\section"),
}

# Maps "## 2.1 ..." style headers to subsection titles
SUBSECTION_LABELS = {
    "2.1 Empirical Algorithm Performance Prediction": "Empirical Algorithm Performance Prediction",
    "2.2 Statistical Modeling of Performance":        "Statistical Modeling of Performance",
    "2.3 Benchmark Generation":                       "Benchmark Generation",
    "2.4 Positioning This Study":                     "Positioning This Study",
    "3.1 Dataset & Variables":                        "Dataset and Variables",
    "3.2 Experimental Design":                        "Experimental Design",
    "3.3 Modeling Hierarchy":                         "Modeling Hierarchy",
    "3.4 Evaluation Metrics":                         "Evaluation Metrics",
    "4.1 Baseline Performance (RQ2)":                 "Baseline Performance (RQ2)",
    "4.2 Incremental Contribution (Sub-RQ3a)":        "Incremental Contribution",
    "4.3 Important Predictors (Sub-RQ3b)":            "Important Predictors",
    "4.4 Model Robustness (Sub-RQ3c)":                "Model Robustness",
    "5.1 Main Findings":                              "Main Findings",
    "5.2 Comparison with Literature":                 "Comparison with Literature",
    "5.3 Practical Implications":                     "Practical Implications",
    "5.4 Unanswered Questions & Future Work":         "Unanswered Questions and Future Work",
    "6.1 Internal Validity":                          "Internal Validity",
    "6.2 External Validity":                          "External Validity",
    "6.3 Construct Validity":                         "Construct Validity",
}

PREAMBLE = r"""\documentclass[11pt,a4paper]{article}
\usepackage[utf8]{inputenc}
\usepackage{amsmath,amssymb}
\usepackage{graphicx}
\usepackage{booktabs}
\usepackage[hidelinks]{hyperref}
\usepackage[margin=1in]{geometry}
\usepackage{natbib}

\title{The Predictive Value of Internal Execution Metrics\\in the Multidimensional Knapsack Problem}
\author{Anonymous Authors \\ \textit{Anonymous Affiliation}}
\date{}

\begin{document}
\maketitle

\begin{abstract}
The multidimensional knapsack problem is a canonical NP-hard challenge serving
as a fundamental model for resource allocation. Existing literature heavily
emphasises predicting empirical hardness from static instance features alone.
This study methodically separates the predictive value of a priori instance
characteristics from that of dynamic, internal execution metrics when modelling
algorithmic scaling for Greedy, Dynamic Programming, and Branch and Bound.
Using a benchmark of 6,000 knapsack instances, we show that baseline
predictability using only static characteristics is extremely high for
deterministic runtimes ($R^2_{\mathrm{adj}} \ge 0.856$), but substantially
lower for heuristic optimality gaps.  Internal execution metrics provide
substantial incremental explanatory power ($\Delta R^2_{\mathrm{adj}} \ge
0.216$) for Branch and Bound node exploration.  The results indicate that
deterministic heuristics are largely predictable from static topologies alone,
whereas exact search algorithms derive significant additional explanatory power
from dynamic execution metrics.
\end{abstract}

\bigskip
\noindent\textbf{Keywords:} Algorithm runtime prediction; multidimensional
knapsack problem; empirical hardness; execution metrics; combinatorial
optimisation

"""

POSTAMBLE = r"""
\bibliographystyle{plain}
\bibliography{references}
\end{document}
"""

TABLES_AND_FIGURES = r"""
% -------------------------------------------------------
\section*{Tables}
% -------------------------------------------------------

\begin{table}[htbp]
\centering
\input{tables/Table_1}
\caption{Number of execution predictors appended for each algorithm in $M2$.}
\label{tab:predictor_counts}
\end{table}

\begin{table}[htbp]
\centering
\input{tables/Table_2}
\caption{Full-sample $R^2$ and adjusted $R^2$ for baseline ($M1$) and
         augmented ($M2$) OLS models across all outcome variables.}
\label{tab:ols_metrics}
\end{table}

\begin{table}[htbp]
\centering
\input{tables/Table_3}
\caption{Full-sample pseudo-$R^2$ for baseline ($M1$) and augmented ($M2$)
         Fractional Logit models for bounded proportional outcomes.}
\label{tab:flogit_metrics}
\end{table}

\begin{table}[htbp]
\centering
\input{tables/Table_4}
\caption{Top-10 standardised $\beta$ coefficients (by absolute magnitude) for
         the Branch and Bound \texttt{log\_nodes\_explored} $M2$ model.}
\label{tab:std_beta}
\end{table}

% -------------------------------------------------------
\section*{Figures}
% -------------------------------------------------------

\begin{figure}[htbp]
\centering
\includegraphics[width=\textwidth]{figures/Figure_1.png}
\caption{Feature importance profiles for Branch and Bound
         \texttt{log\_nodes\_explored} ($M2$).}
\label{fig:importance}
\end{figure}

\begin{figure}[htbp]
\centering
\includegraphics[width=\textwidth]{figures/Figure_2.png}
\caption{Elastic-Net regularisation paths across LOFO folds.}
\label{fig:reg_paths}
\end{figure}

\begin{figure}[htbp]
\centering
\includegraphics[width=\textwidth]{figures/Figure_3.png}
\caption{Residuals vs.\ fitted values for Branch and Bound
         \texttt{log\_time\_millis} ($M2$).  Slight heteroskedasticity in the
         distribution tails is visible (Claim~D04).}
\label{fig:residuals}
\end{figure}
"""


# ------------------------------------------------------------------
# Citation conversion table  (must cover ALL in-text citations)
# ------------------------------------------------------------------
CITE_SUBS = [
    (r'\[Leyton-Brown, 2014\]', r'\\cite{LeytonBrown2014}'),
    (r'Leyton-Brown \[2014\]',  r'\\citet{LeytonBrown2014}'),
    (r'\[Hutter, 2014\]',       r'\\cite{Hutter2014}'),
    (r'Hutter et al\. \[Hutter, 2014\]', r'Hutter et al.\ \\cite{Hutter2014}'),
    (r'\[Papke, 1996\]',        r'\\cite{Papke1996}'),
    (r'\[Hastie, 2009\]',       r'\\cite{Hastie2009}'),
    (r'\[Pisinger, 2005\]',     r'\\cite{Pisinger2005}'),
    (r'Pisinger \[Pisinger, 2005\]', r'Pisinger \\cite{Pisinger2005}'),
    (r'\[Duan, 1983\]',         r'\\cite{Duan1983}'),
]

def apply_citations(text):
    for pattern, repl in CITE_SUBS:
        text = re.sub(pattern, repl, text)
    return text


def escape_ampersands_in_text(text):
    """Escape bare & only when NOT already inside a LaTeX command or tabular."""
    # Replace ' & ' that is NOT preceded by \ with ' \& '
    return re.sub(r'(?<!\\)&', r'\\&', text)


def md_inline_to_latex(text):
    """Convert inline markdown marks to LaTeX equivalents."""
    # Bold **...**
    text = re.sub(r'\*\*(.+?)\*\*', r'\\textbf{\1}', text)
    # Italic *...*
    text = re.sub(r'\*(.+?)\*', r'\\textit{\1}', text)
    # Inline code `...`
    text = re.sub(r'`([^`]+)`', lambda m: '\\texttt{' + m.group(1).replace('_', '\\_') + '}', text)
    return text


def convert_section(raw_text):
    """Convert one markdown section file to LaTeX body text."""
    lines = raw_text.splitlines()
    out   = []
    # Track list depth so we can open/close \begin{itemize} correctly
    list_depth = 0   # 0 = not in list

    def close_lists(target_depth=0):
        nonlocal list_depth
        while list_depth > target_depth:
            out.append('\\end{itemize}')
            list_depth -= 1

    i = 0
    current_section_cmd = None  # set once per file

    while i < len(lines):
        line = lines[i]

        # ---- top-level heading (# Section X:…) ----
        if line.startswith('# '):
            close_lists()
            heading_text = line[2:].strip()
            # Strip " (Pass 2: …)" suffix if present
            heading_text = re.sub(r'\s*\(Pass \d+[^)]*\)', '', heading_text)
            matched_cmd = None
            matched_title = None
            for key, (title, cmd) in SECTION_MAP.items():
                if key in heading_text:
                    matched_cmd  = cmd
                    matched_title = title
                    break
            if matched_cmd:
                current_section_cmd = matched_cmd
                out.append(f'{matched_cmd}{{{matched_title}}}')
            i += 1
            continue

        # ---- subsection heading (## X.Y …) ----
        if line.startswith('## '):
            close_lists()
            sub_raw = line[3:].strip()
            sub_title = SUBSECTION_LABELS.get(sub_raw, sub_raw)
            out.append(f'\\subsection{{{sub_title}}}')
            i += 1
            continue

        # ---- blank line ----
        if line.strip() == '':
            close_lists()
            out.append('')
            i += 1
            continue

        # ---- list item starting with "- " ----
        if re.match(r'^( {0,3})-\s', line):
            indent = len(line) - len(line.lstrip())
            depth  = indent // 2 + 1        # one per 2-space indent
            # open lists
            while list_depth < depth:
                out.append('\\begin{itemize}')
                list_depth += 1
            # close excess lists
            while list_depth > depth:
                out.append('\\end{itemize}')
                list_depth -= 1

            item_text = re.sub(r'^[ ]*-\s', '', line)
            item_text = md_inline_to_latex(item_text)
            item_text = apply_citations(item_text)
            item_text = escape_ampersands_in_text(item_text)
            out.append(f'  \\item {item_text}')
            i += 1
            continue

        # ---- normal paragraph line ----
        close_lists()
        paragraph = md_inline_to_latex(line)
        paragraph = apply_citations(paragraph)
        paragraph = escape_ampersands_in_text(paragraph)
        out.append(paragraph)
        i += 1

    close_lists()
    return '\n'.join(out)


SECTION_FILES = [
    "paper_draft_pass2_section1.md",
    "paper_draft_pass2_section2.md",
    "paper_draft_pass2_section3.md",
    "paper_draft_pass2_section4.md",
    "paper_draft_pass2_section5.md",
    "paper_draft_pass2_section6.md",
    "paper_draft_pass2_section7.md",
]

if __name__ == "__main__":
    with open(OUTPUT_FILE, "w", encoding="utf-8") as out_fh:
        out_fh.write(PREAMBLE)

        for fname in SECTION_FILES:
            path = os.path.join(ARTIFACT_DIR, fname)
            with open(path, "r", encoding="utf-8") as fh:
                raw = fh.read()
            latex_body = convert_section(raw)
            out_fh.write(latex_body)
            out_fh.write("\n\n")

        out_fh.write(TABLES_AND_FIGURES)
        out_fh.write(POSTAMBLE)

    print(f"Assembled: {OUTPUT_FILE}")
