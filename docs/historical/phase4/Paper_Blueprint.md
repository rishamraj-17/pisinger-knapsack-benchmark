# Paper Publication Protocol (Blueprint v8.1: Locked Governing Standard)

> **DOCUMENT CONTROL**
> **Version:** v8.1
> **Status:** APPROVED & LOCKED FOR DRAFTING
> **Date:** 2026-07-26
> **Supersedes:** v8

> **GOVERNANCE DECLARATION:** This protocol governs manuscript production. If any future writing conflicts with this protocol, the protocol takes precedence unless formally revised. 
> **FUTURE REVISION PROTOCOL:** Once drafting begins, revisions require a version increment (e.g., v8.2), rationale, affected sections, and formal approval logged in the Change Log.

---

## 0. Evidence Usage & Editorial Rules

### 0.1 Hierarchy of Evidence & Exclusivity
1. **Primary Evidence:** Aggregated metrics, nested LOFO results, and critical diagnostic thresholds. *Only Primary Evidence may support conclusions.*
2. **Secondary Evidence:** Coefficient tables, permutation importance, standardized betas. *Supports interpretation only.*
3. **Supplementary Evidence:** Residual plots, assumption summaries. *Supports methodological robustness only.*
4. **Exclusivity Rule:** Every metric has exactly one canonical location. No metric may be cited from Secondary evidence if it exists in Primary evidence.
5. **No Evidence Migration:** Evidence ownership does not change unless the protocol itself is revised.
6. **No Orphan Evidence:** Every produced figure/table must either appear in the manuscript, be explicitly designated supplementary, or be intentionally unused. Nothing silently disappears.

### 0.2 Prose Redundancy & Claim Immutability
- **Claim Immutability:** Claim IDs (e.g., P01, D03) are immutable. One Claim ID maps to exactly one scientific claim. They are never reused or split.
- **Prose Redundancy:** A claim is introduced once. Every later mention references it.
- **Claim Retirement:** Unsupported claims discovered during drafting are **deleted—not weakened**. 

### 0.3 Terminology, Notation, Abbreviation, and Citation Freeze
- **Terminology:** Always use "execution metrics", "instance characteristics".
- **Notation:** Always use $\Delta R^2$, pseudo-$R^2$.
- **Citation Style & Protocol:** Author-Year (APA style). During drafting, use `[Author, Year]` placeholders before final bibliography compilation.
- **Abbreviation Registry:**
  - `B&B` = Branch and Bound
  - `DP` = Dynamic Programming
  - `LOFO` = Leave-One-Family-Out
  - `VIF` = Variance Inflation Factor
  - `SV` = Smithson-Verkuilen (smearing)
  - `OLS` = Ordinary Least Squares

### 0.4 Statistical & Decimal Precision Standards
- **Always report:** effect size, confidence intervals, sample size ($N$), exact metric, and units.
- **Decimal Precision:** $R^2$ (3 decimals), p-values (3 decimals unless <0.001), Confidence Intervals (2 decimals), Time/Seconds (2 decimals).
- *All derived values (e.g., $\Delta R^2$) must use the same precision as their parent metric unless otherwise justified.*
- **Negative findings:** Null results *must* be explicitly reported.
- **Statistical Language Policy:**
  - **ALLOWED:** *associated with, consistent with, suggests, indicates, observed, estimated.*
  - **FORBIDDEN:** *caused, drives, proves, determines, guarantees.* (Strict violations of the study boundary).

### 0.5 Supplementary Material Policy
The following items are strictly quarantined to the Supplementary Appendix to prevent main-text bloat:
- Unused diagnostic plots (e.g., secondary QQ plots).
- Additional raw coefficient tables.
- Residual plots and calibration curves.
- LOFO fold-level raw outputs.

### 0.6 Contradiction Handling Protocol
*If archived evidence contradicts governance documents, the frozen computational outputs are reported as truth, while the discrepancy is explicitly acknowledged.* 

---

## 1. Evidence Dependency Graph & Traceability

```text
RQ1: How are instance characteristics associated with observed problem hardness across the benchmark dataset?
 │
 ├── Table 1 (Dataset Summary & Families) - Owner: Section 3.1
 ├── Claim: Zero-event LOFO families demonstrate structural hardness.
 └── Evidence: `canonical_dataset.csv`, `zero_event_families.txt`

RQ2: What is the baseline predictability using only instance characteristics?
 │
 ├── Table 2 (OLS Performance M1) - Owner: Section 4.1
 ├── Table 3 (Fractional Logit/Elastic-Net M1) - Owner: Section 4.1
 ├── Claim P01, P02, P04 (Baseline predictive saturation)
 └── Evidence: `ols_metrics_aggregated.csv`, `flogit_metrics_aggregated.csv`

RQ3: To what extent do internal execution metrics provide additional explanatory power?
 │
 ├── Sub-RQ3a: Incremental Explanatory Power ($\Delta R^2$)
 │    ├── Table 2 ($\Delta R^2$ metrics) - Owner: Section 4.2
 │    ├── Claim P03 (B&B metrics add substantial variance)
 │    └── Evidence: `vif_thinned_delta_r2_comparison.csv`
 │
 ├── Sub-RQ3b: Most Influential Execution Metrics
 │    ├── Table 4 (Top Influential Metrics) - Owner: Section 4.3
 │    ├── Figure 1 (Feature Importance Profiles) - Owner: Section 4.3
 │    ├── Claim F01 (Standardized Betas)
 │    └── Evidence: `std_beta_*.csv`
 │
 └── Sub-RQ3c: Robustness & Statistical Integrity
      ├── Figure 2 (Elastic-Net $\lambda$ Paths) - Owner: Section 4.4.4
      ├── Figure 3 (Assumption Checks) - Owner: Section 4.4.2
      ├── Claim D01, D02, D03, D04
      └── Evidence: `vif_thinned_delta_r2_comparison.csv`, `assumption_summary_*.txt`
```

---

## 2. Table & Figure Ownership and Messaging

### 2.1 Table Ownership
- **Table 1:** Dataset Summary
  - **Owner:** Section 3.1
  - **Primary Message:** Benchmark diversity and variable counts.
  - **Forbidden:** Concluding algorithm superiority based on pure dataset composition.
- **Table 2:** OLS Predictive Performance
  - **Owner:** Section 4.1 & 4.2
  - **Primary Message:** Baseline predictive saturation and incremental $\Delta R^2$.
  - **Forbidden:** Repeating these statistics elsewhere in the text.
- **Table 3:** Fractional Logit & Elastic-Net Performance
  - **Owner:** Section 4.1
  - **Primary Message:** Bounded metrics (optimality/fill rate) maintain predictability.
  - **Forbidden:** Interpreting pseudo-$R^2$ as exact variance explained.
- **Table 4:** Top Influential Execution Metrics
  - **Owner:** Section 4.3
  - **Primary Message:** Most influential execution metrics across all applicable models.
  - **Forbidden:** Interpreting standardized $\beta$ as causal weights.

### 2.2 Figure Ownership
- **Figure 1:** Feature Importance Profiles
  - **Owner:** Section 4.3
  - **Primary Message:** Algorithms isolate distinct internal phases.
  - **Forbidden:** Claiming causality.
- **Figure 2:** Elastic-Net $\lambda$ Regularization Paths
  - **Owner:** Section 4.4.4
  - **Primary Message:** Penalty selection is stable across extreme out-of-distribution LOFO folds.
  - **Forbidden:** Claiming optimality outside the 6,000 instance benchmark.
- **Figure 3:** Assumption Checks (Residuals, QQ, Calibration)
  - **Owner:** Section 4.4.2
  - **Primary Message:** Baseline assumptions hold despite heavy-tailed targets.
  - **Forbidden:** Overstating homoskedasticity.

### 2.3 Bibliography Matrix (RQ Mapped)
| Citation | Role | Status | Supported RQ / Section |
| :--- | :--- | :--- | :--- |
| [Leyton-Brown, 2014] | Background | Mandatory | RQ1 / Introduction |
| [Hutter, 2014] | Comparison | Contextual | Sub-RQ3a / Discussion 5.2 |
| [Hastie, 2009] | Methodology | Mandatory | Methodology 3.3 |
| [Papke, 1996] | Methodology | Mandatory | Methodology 3.3 |
| [Duan, 1983] | Methodology | Mandatory | Sub-RQ3c / Results 4.4.3 |
| [Pisinger, 2005] | Background / Limitation | Mandatory | RQ1 / Dataset 3.1 & Limitations 6.2 |

---

## 3. Mandatory Writing Workflows & Budgets

### 3.1 Multi-Pass Writing Protocol
1. **Pass 1:** Structure & Architecture (Bullet points).
2. **Pass 2:** Technical Accuracy (Mapping claims/numbers to evidence).
3. **Pass 3:** Scientific Language (Applying the allowed/forbidden vocabulary).
4. **Pass 4:** Flow & Transitions.
5. **Pass 5:** Journal Formatting.

### 3.2 Deterministic Results Ordering & Paragraph Budgets
Every Results subsection (max 5 paragraphs) MUST follow this sequence:
- **Paragraph 1:** "To address Sub-RQX..." (Question & Method reminder).
- **Paragraph 2:** Primary figure/table callout & Objective observations.
- **Paragraph 3:** Secondary supporting evidence.
- **Paragraph 4:** Negative findings (explicit).
- **Paragraph 5:** "Therefore, Sub-RQX is answered as follows..."

### 3.3 Strict Results vs. Discussion Boundary
- **RESULTS:** ❌ explaining, ❌ interpreting, ❌ comparing with literature, ❌ implying causality.
- **DISCUSSION:** ✓ interpretation, ✓ literature comparison, ✓ implications, ✓ limitations. **❌ NO NEW STATISTICS.**
- **DISCUSSION STRUCTURE LIMIT:** One paragraph = One claim = One literature comparison = One implication.
- **DISCUSSION EVIDENCE ORDER:** Primary findings $\rightarrow$ Literature $\rightarrow$ Implications $\rightarrow$ Limitations.

### 3.4 Abstract Dependency Rule
The Abstract, Title, and Keywords are explicitly **FORBIDDEN** from being written until the Final Manuscript QA Gate is passed.

### 3.5 Authorship Protocol
- **Section Owner:** Antigravity Agent
- **Reviewer:** User
- **Final Approver:** User

---

## 4. Reviewer Objection Mapping

| Anticipated Reviewer Objection | Existing Frozen Evidence | Manuscript Response Location |
| :--- | :--- | :--- |
| *Execution metrics merely reflect instance size.* | Controlled by M1 baseline. $\Delta R^2$ isolating execution variance. | Section 4.2 / Table 2 / Claim P03 |
| *High $R^2$ is an artifact of multicollinearity.* | VIF thinning threshold > 10 resulted in $\Delta R^2$ drop of only 0.006. | Section 4.4.1 / Claim D01 |
| *The fractional logit is misspecified.* | Link tests acknowledged as significant; potential non-linearities reported. | Section 4.4.2 / Claim D03 |

---

## 5. Section Hierarchy & Evidence Budgets

### 1. Introduction
- **Budget:** 0 Figures, 0 Tables. $\le$ 3 claims.

### 2. Related Work
- **Budget:** 0 Figures, 0 Tables.

### 3. Methodology
- **3.1 Dataset:** 0 Figures, 1 Table (Table 1), $\le$ 5 metrics.
- **3.2 Experimental Design:** 0 Figures, 0 Tables, 1 Claim (F02).
- **3.3 Modeling Hierarchy:** 0 Figures, 0 Tables.

### 4. Results (Strictly Descriptive)
- **4.1 Baseline Performance (RQ2):** 0 Figures, 2 Tables (Table 2, 3), $\le$ 5 claims.
- **4.2 Incremental Contribution (Sub-RQ3a):** 0 Figures, 0 Tables (ref Table 2), $\le$ 4 claims.
- **4.3 Important Predictors (Sub-RQ3b):** 1 Figure (Fig 1), 1 Table (Table 4), $\le$ 4 claims.
- **4.4 Model Robustness (Sub-RQ3c):** 2 Figures (Fig 2, 3), 0 Tables, $\le$ 5 claims.

### 5. Discussion (Interpretive)
- **Budget:** 0 Figures, 0 Tables. *No new statistics allowed.*
- 5.1 Main Findings
- 5.2 Comparison with Literature
- 5.3 Practical Implications
- 5.4 Unanswered Questions & Future Work

### 6. Limitations
- 6.1 Internal Validity
- 6.2 External Validity
- 6.3 Construct Validity

### 7. Conclusion
- **Budget:** Strictly limited to answering RQs, summarizing contributions, limitations, and future work.

### 8. Reproducibility Appendix (Mapping)
- **Archive:** `Phase3_Archive/` | **Freeze Point:** `Phase4_Freeze/` | **Scripts:** `Phase_3_3_Modeling/scripts/`

---

## 6. QA Checklists

### 6.1 Claim Consistency Audit (Pre-Drafting/Pre-Submission)
Before submission, trace every Claim ID (Results $\rightarrow$ Discussion $\rightarrow$ Conclusion):
- [ ] Wording stays consistent across all sections.
- [ ] Numbers remain identical (no drift).
- [ ] No contradictions appear between Results framing and Discussion interpretation.

### 6.2 Figure QA Checklist (Pre-Drafting/Pre-Submission)
- [ ] Readable in grayscale & when printed.
- [ ] Axis units explicitly defined.
- [ ] Caption is entirely self-contained.
- [ ] All abbreviations defined.

### 6.3 Technical QA Gate (Pre-Submission)
- [ ] Does every numerical claim trace to frozen evidence?
- [ ] Is every Claim ID unique and immutable?
- [ ] Are unsupported claims deleted (not weakened)?
- [ ] Is primary vs secondary exclusivity respected?
- [ ] Are structural bounds explicitly stated?
- [ ] Figure & Table constraints obeyed.

### 6.4 Editorial QA Gate (Pre-Submission)
- [ ] Grammar, flow, and transitions are seamless.
- [ ] Prose redundancy is eliminated.
- [ ] Terminology, notation, abbreviations, and statistical language match the strict registry.
- [ ] Citations correctly format `[Author, Year]` and perfectly match the Bibliography Matrix.

## 7. Manuscript Change Log
*(To be populated if structural changes occur post-drafting commencement)*
| Date | Version | Section | Reason | Evidence Affected | Approval |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 2026-07-26 | v8.1 | Protocol | Final pre-drafting editorial safeguards | None | User |
