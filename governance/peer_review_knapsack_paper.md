# Peer Review: "Knapsack Optimization: An Experimental Study of Classical Algorithms Under Different Problem Characteristics"

*Reviewed as an anonymous reviewer, judging only the manuscript content provided (`draft.md`). No external repository, code, or supplementary material was consulted.*

---

## 1. Paper Summary

The manuscript presents an empirical comparison of three classical 0/1 Knapsack algorithms — Greedy (ratio-based), Dynamic Programming, and Branch & Bound — across the five canonical Pisinger instance families (Uncorrelated, Weakly Correlated, Strongly Correlated, Inverse Correlated, Almost Equal Ratios), at six problem sizes (n = 20 to 1000), under two capacity regimes (fixed W = 1000 and scaled W = 0.5·Σwᵢ), with 100 random seeds per configuration (18,000 total algorithm runs). The paper reports runtime, memory, optimality gap (for Greedy), and B&B node counts, with bootstrap confidence intervals and a dedicated threats-to-validity section addressing a 50-million-node B&B safety cap and its censoring effects on reported statistics. Findings include a proof that Greedy is provably optimal on Inverse Correlated instances, an explanation of why B&B's fractional bound degrades on that same family, near-linear DP scaling at fixed W (becoming quadratic under scaled W), and a practical algorithm-selection framework.

## 2. Major Strengths

- **A correct, non-trivial theoretical result.** Section 7.2's exchange-argument proof that Greedy is exactly optimal on Inverse Correlated instances (where vᵢ + wᵢ = constant) is mathematically sound. I verified it independently: if vᵢ = C − wᵢ, then vᵢ/wᵢ is strictly decreasing in wᵢ, and for any feasible solution containing a heavier item j while excluding a lighter item i, swapping i for j strictly increases value while relaxing the weight constraint — so no optimal solution can contain such an inversion. This confirms the maximal ascending-weight prefix (i.e., ratio-greedy) is optimal for this family. This is a genuine, verified contribution, not just an empirical observation.
- **Unusually careful treatment of a real data-quality problem.** Rather than quietly averaging over instances that hit the 50M-node B&B safety cap, Section 9 explicitly quantifies per-cell censoring rates and explains, correctly, that right-censored runtimes bias the mean downward and can even compromise the median once >50% of a cell is capped. This is a level of statistical honesty that many empirical-algorithms papers omit.
- **Internal numerical consistency in most places.** Several cross-checks I ran independently reproduce the paper's own stated figures: the Strongly-Correlated/Uncorrelated node ratio (1,521/150 = 10.14x, matches "10.1x"); the B&B growth exponents (36.0x → 0.92, 10.6x → 0.60, 23,094x → 2.57, all correctly derived from the stated ratios); the DP/B&B 2–3x speed claim on Uncorrelated (0.87 ms / 0.30 ms ≈ 2.9x); and the maximum observed B&B runtime (9,318.62 ms ≈ "~9s," matching the timeout discussion). This suggests the underlying numbers, where checkable, were derived carefully rather than invented.
- **A well-motivated instance design** grounded directly in Pisinger's hardness taxonomy, with clear generative formulas for each family.

## 3. Major Weaknesses

- The submitted manuscript does not contain any of its own tables or figures — Tables 1–6 are LaTeX `\input{}` placeholders and Figures 1–6 are references to external PDF paths, none of which are reproduced in the document. Most claims can only be checked against numbers restated in prose, not against the primary tabulated/visual evidence.
- A specific, load-bearing practical recommendation ("DP is reliable for W ≤ 10⁴") is stated three times but is not derived from any reported experiment in the visible text.
- A verifiable arithmetic inconsistency exists in the Greedy scaling analysis (Section 6.7).
- The word "exponential" is used in the Abstract and Section 6.7 to describe B&B node growth that the paper's own methodology (log-log fitted exponent ≈ 2.57) characterizes as polynomial/power-law, not exponential.
- The manuscript claims code and data are "publicly available" but provides no URL, DOI, or anonymized link anywhere in the text.

Each is detailed with evidence below.

## 4. Detailed Comments

### Issue 1 — Tables and figures are not present in the manuscript

**Manuscript Evidence:** Throughout Section 6, table content is represented only as `\input{tables/fixed_table_time_max_n}`, `\input{tables/scaled_table_greedy_gap}`, etc. (e.g., lines under 6.1, 6.2, 6.3, 6.4, 6.5). Figures are referenced only by file path, e.g., "shown in `figures/fixed/pdf/greedy_gap_boxplot.pdf`" (Figure 2), "`figures/fixed/pdf/bb_nodes_boxplot.pdf`" (Figure 3).

**Scientific Analysis:**
- *What the manuscript states:* Six tables and six figures are cited as the evidentiary basis for the Results section.
- *My reasoning:* As submitted, none of this content is viewable. A reviewer's job is to check whether the presented evidence supports the stated conclusions; here, the primary evidence (full distributions, confidence intervals, box plots, scaling curves) simply is not in the document. The manuscript does restate many individual statistics in prose (medians, means, specific node counts), which partially mitigates this, but full distributional claims (e.g., "heavy-tailed," "broken Y-axis," shapes of scaling curves in Figures 1 and 6) cannot be checked at all.
- *Conclusion:* This is a serious presentation defect independent of whether the underlying science is sound. It may be an artifact of manuscript-format conversion, but per the review's own instructions I can only evaluate what is in front of me, and what is in front of me does not include the primary evidence for roughly half the paper's claims.

**Severity:** Major
**Confidence:** High
**Recommendation:** Major Revision — resubmit with all tables and figures rendered/embedded.

---

### Issue 2 — Unsupported quantitative recommendation ("DP is reliable when W ≤ 10⁴")

**Manuscript Evidence:** Section 7.1: "DP is the reliable choice when W ≤ 10⁴... For larger W, consider FPTAS or B&B." Section 7.5 (Limitations): "All experiments use W = 1000 (fixed)... DP's O(nW) complexity means that scaling W to 10⁴ or 10⁶ would increase runtime by 10–1000x, potentially changing the algorithm ranking." Section 8 (Conclusion): "Use DP when W ≤ 10⁴."

**Scientific Analysis:**
- *What the manuscript states:* A specific numeric threshold (W ≤ 10⁴) for when DP remains the recommended exact algorithm.
- *My reasoning:* The fixed-capacity experiments test only W = 1000 — below the recommended threshold. The scaled-capacity experiments, by the paper's own arithmetic in Section 6.8 (W ≈ 250n, so at n = 1000, W ≈ 250,250), actually exceed 10⁴ by roughly 25x, yet no runtime figures for DP at these larger, already-tested capacities are given in the visible text, and Section 7.5 explicitly lists W-scaling beyond what was tested as future work ("Future work should explore W scaling"). The 10⁴ figure therefore appears either arbitrary or drawn from data not shown, and it is inconsistent with the paper's own statement elsewhere that W-scaling wasn't tested.
- *Conclusion:* Not demonstrated within the manuscript. This is the paper's most concrete, actionable practical claim, so its lack of grounding matters more than a typical limitation.

**Severity:** Major
**Confidence:** High
**Recommendation:** Major Revision — either report the scaled-mode DP-vs-W results that would justify a concrete threshold, or remove/soften the specific numeric recommendation.

---

### Issue 3 — Arithmetic inconsistency in the Greedy scaling analysis

**Manuscript Evidence:** Section 6.7: "Greedy: theoretical O(n log n), observed approximately O(n). Mean times scale from 0.01 ms (n=20) to 0.17 ms (n=1000), a 28x increase for 50x n — fitted exponent approximately 0.85."

**Scientific Analysis:**
- *What the manuscript states:* A 0.01 ms → 0.17 ms increase is characterized as "28x," yielding a fitted exponent of 0.85.
- *My reasoning:* 0.17 / 0.01 = 17, not 28. Working backward, an exponent of 0.85 over a 50x increase in n implies a ratio of 50^0.85 ≈ 27.8 ≈ 28 — consistent with the stated "28x" and "0.85" but not with the stated pair of times (0.01, 0.17). One of the three numbers (0.01 ms, 0.17 ms, or "28x"/"0.85") is incorrect. I confirmed this by direct calculation; it is not a matter of interpretation.
- *Conclusion:* A verifiable, single-cell arithmetic error. It does not change the qualitative conclusion (sublinear observed scaling relative to O(n log n)), but it should be corrected before publication, and it undermines confidence in the surrounding un-tabulated numbers.

**Severity:** Minor (does not affect the paper's conclusions)
**Confidence:** High
**Recommendation:** Minor Revision — correct the discrepant value(s).

---

### Issue 4 — "Exponential" is used to describe growth the paper's own method characterizes as polynomial

**Manuscript Evidence:** Abstract: "B&B... suffers exponential blowup on Inverse Correlated." Section 6.7: "Inverse Correlated shows superlinear growth (exponent ≈ 2.57)... Inverse Correlated nodes grow super-exponentially (40 → 923,740)." Section 6.7 also states the fitted values come "from a log-log plot," i.e., a power-law fit y ≈ n^k.

**Scientific Analysis:**
- *What the manuscript states:* Both a specific fitted power-law exponent (n^2.57) and the qualitative descriptor "exponential"/"super-exponential" are applied to the same growth pattern.
- *My reasoning:* A log-log linear fit is, by construction, a power-law (polynomial) fit — the "exponent" recovered (2.57) is the polynomial degree, not a base of a true exponential (c^n). Polynomial growth with a high exponent still grows asymptotically slower than any true exponential function. These are mathematically distinct growth classes, and the paper's own methodology (log-log fitting) only supports the polynomial characterization. The word "exponential" would be accurate for individual pathological instances that exhaust the 50M-node safety cap (Section 7.3 does describe this correctly, in terms consistent with worst-case 2ⁿ behavior for specific hard instances), but applying "exponential blowup" as a headline Abstract-level descriptor for the *typical/fitted* trend conflates a worst-case, per-instance phenomenon with the average scaling behavior the paper actually measured and fit.
- *Conclusion:* This is a real terminological imprecision, appearing prominently in the Abstract, that a technically careful reader would flag. It risks overstating how fast typical (median/mean) B&B cost grows with n on this family.

**Severity:** Moderate (appears in the Abstract as a headline claim, though the underlying node-count numbers appear correct)
**Confidence:** High
**Recommendation:** Minor Revision — distinguish "exponential in the worst case / at the node-cap boundary" from "polynomial (n^2.57) in the fitted median/mean trend" throughout, starting with the Abstract.

---

### Issue 5 — No access point given for the claimed public code/data

**Manuscript Evidence:** Section 9 (Reliability): "All experimental data, analysis scripts, and figure generation code are publicly available. Running `./reproduce.sh` regenerates the complete experimental dataset (18,000 runs)..." Appendix: "All code available in this repository."

**Scientific Analysis:**
- *What the manuscript states:* Full public availability of code and data sufficient for independent reproduction.
- *My reasoning:* No URL, DOI, anonymized repository link, or supplementary-material reference is given anywhere in the manuscript — only a script name (`./reproduce.sh`) and an output path (`out/results/full_experiment.csv`). As an anonymous reviewer with access only to the manuscript, I have no way to locate or verify "this repository."
- *Conclusion:* The reproducibility claim, as written, cannot currently be acted on by a reader. This may simply need an anonymized link added (common in double-blind review), but as submitted it is a gap.

**Severity:** Major (directly affects the "reproducibility" review criterion)
**Confidence:** High
**Recommendation:** Minor Revision — add an anonymized repository link or supplementary archive reference.

---

### Issue 6 — Bootstrap methodology is underspecified, including under censoring

**Manuscript Evidence:** Table captions throughout Section 6 refer to "95% bootstrap CI" (e.g., Tables 1, 4, 5) without further elaboration in the visible text. Section 9 separately establishes that some cells (e.g., scaled-mode Inverse Correlated at n=1000) have 75% of runs right-censored at the node cap.

**Scientific Analysis:**
- *What the manuscript states:* Bootstrap confidence intervals are reported for means/medians, and, separately, an analysis of censoring rates per cell.
- *My reasoning:* The manuscript never states the number of bootstrap resamples, the resampling method (e.g., percentile vs. BCa), or — most importantly — whether/how the bootstrap procedure accounts for the fact that in some cells the "observed" runtime for a majority of instances is itself an artificial floor value (the node-cap time) rather than a true completion time. A standard nonparametric bootstrap over such data would produce a CI for the *censored* distribution, not the true underlying completion-time distribution, and nothing in the text indicates this distinction was made in constructing the CIs.
- *Conclusion:* Not fully demonstrated within the manuscript. The censoring discussion in Section 9 is honest about point-estimate bias but doesn't extend that same rigor to the reported CIs.

**Severity:** Moderate
**Confidence:** Medium
**Recommendation:** Minor Revision — state bootstrap parameters and clarify how (or whether) censored cells' CIs should be interpreted.

---

### Issue 7 — Unsupported claim about B&B's sensitivity to capacity W

**Manuscript Evidence:** Section 7.5: "B&B's performance is less sensitive to W because its bound computation does not depend on W directly (the fractional knapsack subproblem is solved analytically)."

**Scientific Analysis:**
- *What the manuscript states:* B&B is largely insensitive to the capacity parameter W.
- *My reasoning:* The fractional-knapsack bound used at every B&B node is computed with respect to the *remaining capacity* at that node — by the paper's own description in Section 3.3 and Section 7.3 ("packing items greedily by v_i/w_i and allowing fractional inclusion... until capacity is exhausted"), the bound is explicitly a function of capacity. The claim that it "does not depend on W directly" is not obviously true and is not supported by any reported experiment comparing B&B under fixed vs. scaled capacity (the two experimental modes that would let this be tested directly are both present in the paper's own data, but no such comparison is reported in the visible text).
- *Conclusion:* Not demonstrated within the manuscript, and arguably in tension with the algorithm's own description elsewhere in the paper.

**Severity:** Moderate
**Confidence:** Medium
**Recommendation:** Minor Revision — either substantiate with a fixed-vs-scaled B&B comparison or remove the claim.

---

### Minor additional comments (not raised to full "major issue" status)

- **Family naming inconsistency:** the fifth instance family is called "Almost Equal Ratios" in Section 4's table and in Section 9, but "Equal Ratios" in Sections 6.2, 6.3, and 6.7. This should be standardized.
- **Seeding description ambiguity:** Section 4 specifies "100 seeds per (n, family)" (implying 100 distinct instance-generating seeds), while Section 9 states instances are "generated from seeded PRNGs (seed 42)" and Section 8 refers to "seed = 42 for all statistical computations." It's plausible that 42 is a master seed that deterministically generates the 100 sub-seeds, but the manuscript never states this explicitly, leaving the two descriptions looking like they could refer to different things.
- **Pruning-rate metric may understate actual pruning:** the pruning rate is defined (Section 6.3) as nodes discarded upon being polled from the queue, divided by nodes polled — even the best family (Uncorrelated) is reported at only 7.3%. If nodes that are never generated/enqueued at all (e.g., via bound checks at generation time) aren't counted in either the numerator or denominator, this metric may substantially understate how much of the search space the bound is actually eliminating. This isn't necessarily wrong, but the low headline numbers (0.5%–7.3%) are counterintuitive enough to warrant an explicit definition of what counts as a "node" in this accounting.
- The phrase "the manuscript has been independently verified against the generated tables" (Conclusion and Appendix) is unusual for a scientific paper — "independent" verification ordinarily implies checking by a party other than the authors, whereas this appears to describe the authors checking their own manuscript against their own generated output. This isn't a scientific error, but the terminology could mislead a reader about what kind of verification occurred.
- The "Almost Equal Ratios" family description states that ties "break arbitrarily," but with values drawn from a continuous uniform distribution, exact ties have probability zero; the actual phenomenon is near-ties / high sensitivity to small perturbations, which is a related but distinct issue from tie-breaking in the sorting-algorithm sense.

## 5. Questions for the Authors

1. Can you provide the missing tables and figures (or an anonymized repository link) so that the full distributional evidence behind Sections 6 and 7 can be reviewed directly?
2. What empirical or theoretical basis supports the specific W ≤ 10⁴ threshold for recommending DP, given that the fixed-mode experiments only reach W = 1000 and the scaled-mode experiments (which do reach W ≈ 250,000) aren't reported broken out by W?
3. Please reconcile the 0.01 ms → 0.17 ms Greedy timings in Section 6.7 with the stated "28x" ratio and 0.85 exponent.
4. Was the bootstrap CI procedure applied identically to censored (node-capped) and uncensored cells? If so, how should readers interpret a CI computed partly from artificial cap-time floors rather than true completion times?
5. Is "seed 42" in Section 9 the master seed that generates the 100 per-instance seeds described in Section 4, or a separate, single seed used for instance generation? Please clarify explicitly.
6. Do you have direct experimental evidence (rather than an analytic argument) that B&B node counts/runtime are similar under fixed vs. scaled capacity at matched n? This would substantiate the W-insensitivity claim in Section 7.5.

## 6. Overall Assessment

**Novelty:** Incremental but real. The paper doesn't introduce a new algorithm, but the systematic joint comparison of all three classical algorithms across all five Pisinger families with a unified statistical treatment, plus a correct proof of an under-appreciated exact-optimality result for Greedy on Inverse Correlated instances, is a legitimate (if modest) contribution.

**Technical quality:** Mixed. The core exchange-argument proof (Section 7.2) is correct and well-argued. Most cross-checkable arithmetic throughout the paper is internally consistent. However, I found one clear arithmetic error (Issue 3), one clear terminological misuse of "exponential" for what the paper's own methodology treats as a power law (Issue 4), and one claim presented without supporting evidence and in tension with the algorithm's own description elsewhere (Issue 7).

**Experimental quality:** Generally strong for what can be assessed. The design (5 families × 6 sizes × 100 seeds × 2 capacity modes) is sensible and reasonably large-scale; the treatment of the B&B node-cap censoring problem (Section 9) is unusually careful and a genuine strength.

**Clarity:** Adequate in prose, but undermined by the missing tables/figures and by two internal naming/terminology inconsistencies (Equal Ratios vs. Almost Equal Ratios; seed 42 vs. 100 seeds).

**Significance:** Moderate. The practical decision-framework (Section 7.1/8) is useful, but several of its most concrete numeric recommendations (notably W ≤ 10⁴) are not clearly grounded in the reported data, which limits how much weight practitioners should place on them as stated.

**Reproducibility:** The experimental protocol itself is described in good detail (warmup iterations, timeout, hardware, seed structure), which is commendable, but the claim of public code/data availability is not backed by any access point in the manuscript as submitted, and the primary tables/figures needed to check the numeric claims are not included.

## 7. Final Recommendation

**Weak Reject.**

Justification: The paper contains real, verifiable strengths — a correct proof of a non-obvious optimality result, an unusually rigorous treatment of B&B censoring, and mostly self-consistent numbers where they can be checked. However, as submitted, the manuscript has several concrete, evidence-based problems that go beyond typical revision-level polish: the primary tables and figures are absent from the document, so a substantial fraction of the paper's quantitative claims cannot be directly verified; a headline practical recommendation (W ≤ 10⁴) is not demonstrated by the reported experiments; there is at least one clear arithmetic inconsistency; the Abstract uses "exponential" to describe what the paper's own log-log fitting methodology characterizes as polynomial growth; and the reproducibility claim lacks any access point. None of these issues appear to reflect a fundamentally flawed study — most look correctable — but collectively they are enough that I cannot currently verify or endorse the full evidentiary chain behind the paper's conclusions. With the missing tables/figures restored, the identified numerical and terminological issues corrected, and the W ≤ 10⁴ claim either substantiated or removed, this could plausibly become an Accept.

## 8. Reviewer Confidence

**Medium.** My confidence is high on the specific, checkable items (the arithmetic error, the exponential/polynomial terminology issue, the proof verification, the missing-tables observation) because these follow directly and unambiguously from the manuscript text. My confidence is medium overall because a meaningful share of the paper's claims rest on tables and figures I could not inspect directly, and my assessment of those claims is necessarily based on the paper's own prose restatement of numbers I cannot independently cross-check against raw data.
