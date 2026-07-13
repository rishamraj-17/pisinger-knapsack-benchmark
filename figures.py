#!/usr/bin/env python3
"""
Publication-quality figure generation for the Knapsack Empirical Comparison.

Generates six figures in PDF, PNG (600 DPI), and SVG:
  1. Runtime vs problem size (three-panel, one per algorithm)
  2. Greedy optimality gap boxplot by instance family
  3. Branch & Bound nodes explored (broken Y-axis for outliers)
  4. Branch & Bound runtime distribution at n=500 (broken Y-axis)
  5. Runtime comparison at n=500 (split panel for Inverse Correlated)
  6. Dynamic Programming runtime scaling with confidence intervals

Color scheme: Okabe-Ito (colorblind-safe).
All typography and spacing follow IEEE/Springer publication standards.

Requires: numpy, matplotlib.
"""

import os
import statistics
import random
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib.ticker import FixedLocator
from mpl_toolkits.axes_grid1.inset_locator import mark_inset

from plot_utils import (
    setup_publication_style, save_figure, style_boxplot, add_major_grid_only,
    setup_axes, create_broken_y_axis, add_inset_zoom,
    create_figure_single, create_figure_subplots, finalize_figure,
    ALGO_COLORS, ALGO_MARKERS, FAM_COLORS, FAM_SHORT,
    get_fam_short,
    compute_bootstrap_ci,
    LINE_WIDTH, MARKER_SIZE, ERROR_CAPSIZE, ERROR_CAPTHICK, ERROR_LINEWIDTH, BOX_WIDTH,
    SPINE_LW, LEGEND_FONTSIZE,
)


# ─── Figure 1: Runtime vs n (3 subplots, inset zoom on B&B) ───────────────
def generate_figure_runtime_vs_n(fig_dir, rows, families, algorithms, max_n, ns):
    print("Generating Figure 1: runtime_vs_n...")
    fig, axes = create_figure_subplots(1, 3, figsize=(11.0, 3.5), sharey=False)

    for idx, algo in enumerate(algorithms):
        ax = axes[idx]
        for fam in families:
            subset = [r for r in rows if r['algorithm'] == algo and r['dataset_type'] == fam]
            if not subset:
                continue
            by_n = {}
            for r in subset:
                by_n.setdefault(r['n'], []).append(r['time_ms'])
            ns_sorted = sorted(by_n.keys())
            means = [statistics.mean(by_n[n]) for n in ns_sorted]
            ax.plot(ns_sorted, means,
                    marker=ALGO_MARKERS[algo], color=FAM_COLORS[fam],
                    label=get_fam_short(fam), linewidth=LINE_WIDTH, markersize=MARKER_SIZE,
                    markeredgewidth=0.4, markeredgecolor='white', zorder=3)

        setup_axes(ax, xlabel='Problem Size (n)',
                   ylabel='Execution Time (ms)' if idx == 0 else None,
                   title=algo, grid=True, x_fixed_ticks=ns)

    # Inset zoom on B&B panel (index 2) for non-InverseCorrelated families
    ax_bb = axes[2]
    bb_main_fams = [f for f in families if f != 'InverseCorrelated']
    y_max_main = 0
    for fam in bb_main_fams:
        subset = [r for r in rows if r['algorithm'] == 'BranchAndBound' and r['dataset_type'] == fam]
        if not subset:
            continue
        by_n = {}
        for r in subset:
            by_n.setdefault(r['n'], []).append(r['time_ms'])
        ns_sorted = sorted(by_n.keys())
        means = [statistics.mean(by_n[n]) for n in ns_sorted]
        if means:
            y_max_main = max(y_max_main, max(means))

    if y_max_main > 0:
        ax_inset = add_inset_zoom(ax_bb, xlim=(15, 550), ylim=(0, y_max_main * 1.15),
                                  loc='upper left', width='35%', height='35%')
        for fam in bb_main_fams:
            subset = [r for r in rows if r['algorithm'] == 'BranchAndBound' and r['dataset_type'] == fam]
            if not subset:
                continue
            by_n = {}
            for r in subset:
                by_n.setdefault(r['n'], []).append(r['time_ms'])
            ns_sorted = sorted(by_n.keys())
            means = [statistics.mean(by_n[n]) for n in ns_sorted]
            ax_inset.plot(ns_sorted, means,
                          marker=ALGO_MARKERS['BranchAndBound'], color=FAM_COLORS[fam],
                          label=get_fam_short(fam), linewidth=1.0, markersize=3,
                          markeredgewidth=0.3, markeredgecolor='white', zorder=3)
        ax_inset.set_title('Zoom: Other Instance Families', fontsize=6, pad=2)
        ax_inset.legend(fontsize=5, frameon=True, fancybox=True, framealpha=0.95)

    handles, labels = axes[0].get_legend_handles_labels()
    finalize_figure(fig, suptitle='Execution Time vs Problem Size (n) by Algorithm',
                    legend_handles=handles, legend_labels=labels,
                    legend_ncol=5, legend_bbox=(0.5, 1.10),
                    rect=[0, 0, 1, 0.90])
    return save_figure(fig, fig_dir, 'runtime_vs_n')


# ─── Figure 2: Greedy Gap Boxplot ─────────────────────────────────────────
def generate_figure_greedy_gap(fig_dir, greedy_rows, families):
    print("Generating Figure 2: greedy_gap_boxplot...")
    gap_data = []
    gap_labels = []
    for fam in families:
        gaps = [r.get('gap_pct', 0) for r in greedy_rows if r['dataset_type'] == fam]
        if gaps:
            gap_data.append(gaps)
            gap_labels.append(get_fam_short(fam))

    fig, ax = create_figure_single(figsize=(7.0, 3.8))
    bp = ax.boxplot(gap_data, tick_labels=gap_labels, patch_artist=True, showfliers=True,
                    flierprops={'markersize': 2.5, 'marker': 'o'}, widths=BOX_WIDTH)
    style_boxplot(bp, ALGO_COLORS['Greedy'], alpha=0.5)
    ax.axhline(y=0, color='#888888', linestyle='--', linewidth=0.5, zorder=0)
    setup_axes(ax, ylabel='Optimality Gap (%)',
               title='Greedy Optimality Gap by Instance Family', grid=True)
    finalize_figure(fig)
    return save_figure(fig, fig_dir, 'greedy_gap_boxplot')


# ─── Figure 3: B&B Nodes (Broken Y-axis) ──────────────────────────────────
def generate_figure_bb_nodes(fig_dir, bb_rows, families):
    print("Generating Figure 3: bb_nodes_boxplot...")
    node_data = []
    node_labels = []
    all_nodes = []
    for fam in families:
        nodes = [r['nodes_explored'] for r in bb_rows if r['dataset_type'] == fam]
        if nodes:
            node_data.append(nodes)
            node_labels.append(get_fam_short(fam))
            all_nodes.extend(nodes)

    # 95th percentile split for broken axis
    sorted_nodes = sorted(all_nodes)
    clip_val = sorted_nodes[int(len(sorted_nodes) * 0.95)]
    max_all = max(all_nodes)

    fig, axes = plt.subplots(2, 1, figsize=(7.0, 4.5), sharex=True,
                             gridspec_kw={'height_ratios': [3, 1], 'hspace': 0.04})
    ax_main, ax_zoom = axes[0], axes[1]

    bp_main = ax_main.boxplot(node_data, tick_labels=node_labels, patch_artist=True, showfliers=True,
                              flierprops={'markersize': 2.5, 'marker': 'o'}, widths=BOX_WIDTH)
    bp_zoom = ax_zoom.boxplot(node_data, patch_artist=True, showfliers=True,
                              flierprops={'markersize': 2.5, 'marker': 'o'}, widths=BOX_WIDTH)

    style_boxplot(bp_main, ALGO_COLORS['BranchAndBound'], alpha=0.5)
    style_boxplot(bp_zoom, ALGO_COLORS['BranchAndBound'], alpha=0.5)

    ax_main.set_ylim(0, clip_val * 1.05)
    ax_zoom.set_ylim(clip_val * 0.95, max_all * 1.02)

    setup_axes(ax_main, ylabel='Nodes Explored',
               title='Branch & Bound Nodes Explored by Instance Family',
               grid=True, show_xlabel=False)
    setup_axes(ax_zoom, grid=True, show_xlabel=True)

    ax_main.set_xticklabels([])
    ax_zoom.xaxis.set_major_locator(FixedLocator(range(len(node_labels))))
    ax_zoom.set_xticklabels(node_labels)

    create_broken_y_axis(ax_main, ax_zoom)
    fig.tight_layout(rect=[0, 0, 1, 0.97])
    return save_figure(fig, fig_dir, 'bb_nodes_boxplot')


# ─── Figure 4: B&B Runtime at n=max_n (Broken Y-axis) ─────────────────────
def generate_figure_bb_runtime(fig_dir, bb_rows, families, max_n):
    print("Generating Figure 4: bb_runtime_distribution...")
    bb_max_n = [r for r in bb_rows if r['n'] == max_n]
    runtime_data = []
    runtime_labels = []
    colors_bb = []
    all_times = []
    HIGHLIGHT_COLOR = '#D55E00'
    OTHER_COLOR = '#0072B2'
    for fam in families:
        times = [r['time_ms'] for r in bb_max_n if r['dataset_type'] == fam]
        if times:
            runtime_data.append(times)
            runtime_labels.append(get_fam_short(fam))
            colors_bb.append(HIGHLIGHT_COLOR if fam == 'InverseCorrelated' else OTHER_COLOR)
            all_times.extend(times)

    non_inv_times = [t for fam in families if fam != 'InverseCorrelated'
                     for t in [r['time_ms'] for r in bb_max_n if r['dataset_type'] == fam]]
    sorted_times = sorted(non_inv_times)
    clip_val = sorted_times[int(len(sorted_times) * 0.95)] if sorted_times else 1.0
    max_all = max(all_times)

    fig, axes = plt.subplots(2, 1, figsize=(7.0, 4.5), sharex=True,
                             gridspec_kw={'height_ratios': [3, 1], 'hspace': 0.04})
    ax_main, ax_zoom = axes[0], axes[1]

    bp_main = ax_main.boxplot(runtime_data, tick_labels=runtime_labels, patch_artist=True, showfliers=True,
                              flierprops={'markersize': 2.5, 'marker': 'o'}, widths=BOX_WIDTH)
    bp_zoom = ax_zoom.boxplot(runtime_data, patch_artist=True, showfliers=True,
                              flierprops={'markersize': 2.5, 'marker': 'o'}, widths=BOX_WIDTH)

    for patch, color in zip(bp_main['boxes'], colors_bb):
        patch.set_facecolor(color); patch.set_alpha(0.5); patch.set_edgecolor('#333333'); patch.set_linewidth(SPINE_LW)
    for patch, color in zip(bp_zoom['boxes'], colors_bb):
        patch.set_facecolor(color); patch.set_alpha(0.5); patch.set_edgecolor('#333333'); patch.set_linewidth(SPINE_LW)

    for whisker in bp_main['whiskers']: whisker.set_color('#333333'); whisker.set_linewidth(SPINE_LW)
    for whisker in bp_zoom['whiskers']: whisker.set_color('#333333'); whisker.set_linewidth(SPINE_LW)
    for cap in bp_main['caps']: cap.set_color('#333333'); cap.set_linewidth(SPINE_LW)
    for cap in bp_zoom['caps']: cap.set_color('#333333'); cap.set_linewidth(SPINE_LW)
    for median in bp_main['medians']: median.set_color('#333333'); median.set_linewidth(1.5)
    for median in bp_zoom['medians']: median.set_color('#333333'); median.set_linewidth(1.5)
    for flier in bp_main['fliers']: flier.set_marker('o'); flier.set_markersize(2.5); flier.set_markerfacecolor('#666666'); flier.set_markeredgecolor('#333333'); flier.set_alpha(0.4)
    for flier in bp_zoom['fliers']: flier.set_marker('o'); flier.set_markersize(2.5); flier.set_markerfacecolor('#666666'); flier.set_markeredgecolor('#333333'); flier.set_alpha(0.4)

    ax_main.set_ylim(0, clip_val * 1.1)
    ax_zoom.set_ylim(clip_val * 0.9, max_all * 1.02)

    setup_axes(ax_main, ylabel='Execution Time (ms)',
               title=f'Branch & Bound Runtime at n={max_n} by Instance Family',
               grid=True, show_xlabel=False)
    setup_axes(ax_zoom, grid=True, show_xlabel=True)

    ax_main.set_xticklabels([])
    ax_zoom.xaxis.set_major_locator(FixedLocator(range(len(runtime_labels))))
    ax_zoom.set_xticklabels(runtime_labels)

    create_broken_y_axis(ax_main, ax_zoom)

    legend_elements = [
        Patch(facecolor=HIGHLIGHT_COLOR, alpha=0.5, edgecolor='#333333',
              label='InverseCorrelated (heavy-tailed)'),
        Patch(facecolor=OTHER_COLOR, alpha=0.5, edgecolor='#333333',
              label='Other families')
    ]
    ax_main.legend(handles=legend_elements, loc='upper left', fontsize=LEGEND_FONTSIZE,
                   frameon=True, fancybox=True, framealpha=0.95, borderpad=0.3)
    finalize_figure(fig, rect=[0, 0, 1, 0.97], tight=False)
    fig.tight_layout(rect=[0, 0, 1, 0.97])
    return save_figure(fig, fig_dir, 'bb_runtime_distribution')


# ─── Figure 5: Runtime Comparison at n=500 (Split Panel) ──────────────────
def generate_figure_runtime_comparison(fig_dir, rows, families, algorithms, max_n):
    print("Generating Figure 5: runtime_comparison_n500...")
    offsets = [-0.2, 0, 0.2]

    # Two panels: main (4:1 width) + InverseCorrelated expanded
    fig, axes = plt.subplots(1, 2, figsize=(11.0, 3.8),
                             gridspec_kw={'width_ratios': [4, 1], 'wspace': 0.08})
    ax_main, ax_inv = axes[0], axes[1]

    # Main panel: all 5 families
    x_main = np.arange(len(families))

    for i, algo in enumerate(algorithms):
        means = []
        cis = []
        for fam in families:
            subset = [r for r in rows if r['algorithm'] == algo and r['dataset_type'] == fam and r['n'] == max_n]
            if subset:
                times = [r['time_ms'] for r in subset]
                means.append(statistics.mean(times))
                cis.append(compute_bootstrap_ci(times, n_bootstrap=5000))
            else:
                means.append(0)
                cis.append((0, 0))

        x_pos = x_main + offsets[i]
        ci_lower = [m - c[0] if m > 0 else 0 for m, c in zip(means, cis)]
        ci_upper = [c[1] - m if m > 0 else 0 for m, c in zip(means, cis)]
        yerr = [ci_lower, ci_upper]
        ax_main.errorbar(x_pos, means, yerr=yerr, fmt='o', color=ALGO_COLORS[algo],
                         label=algo, linewidth=LINE_WIDTH, markersize=MARKER_SIZE,
                         capsize=ERROR_CAPSIZE, capthick=ERROR_CAPTHICK,
                         elinewidth=ERROR_LINEWIDTH, alpha=0.9, zorder=3)

    setup_axes(ax_main, ylabel='Mean Runtime (ms)',
               title=f'Execution Time at n={max_n}',
               grid=True, show_ylabel=True)
    ax_main.set_xticks(x_main)
    ax_main.set_xticklabels([get_fam_short(f) for f in families])

    # Right panel: InverseCorrelated only (expanded scale)
    inv_fams = ['InverseCorrelated']
    x_inv = np.arange(len(inv_fams))

    for i, algo in enumerate(algorithms):
        means = []
        cis = []
        for fam in inv_fams:
            subset = [r for r in rows if r['algorithm'] == algo and r['dataset_type'] == fam and r['n'] == max_n]
            if subset:
                times = [r['time_ms'] for r in subset]
                means.append(statistics.mean(times))
                cis.append(compute_bootstrap_ci(times, n_bootstrap=5000))
            else:
                means.append(0)
                cis.append((0, 0))

        x_pos = x_inv + offsets[i]
        ci_lower = [m - c[0] if m > 0 else 0 for m, c in zip(means, cis)]
        ci_upper = [c[1] - m if m > 0 else 0 for m, c in zip(means, cis)]
        yerr = [ci_lower, ci_upper]
        ax_inv.errorbar(x_pos, means, yerr=yerr, fmt='o', color=ALGO_COLORS[algo],
                        linewidth=LINE_WIDTH, markersize=MARKER_SIZE,
                        capsize=ERROR_CAPSIZE, capthick=ERROR_CAPTHICK,
                        elinewidth=ERROR_LINEWIDTH, alpha=0.9, zorder=3)

    setup_axes(ax_inv, ylabel='', title='InverseCorrelated\n(expanded scale)',
               grid=True, show_ylabel=False)
    ax_inv.set_xticks(x_inv)
    ax_inv.set_xticklabels([get_fam_short(f) for f in inv_fams], rotation=30, ha='right')
    ax_inv.yaxis.set_label_position('right')
    ax_inv.yaxis.tick_right()

    # Single legend for entire figure
    handles, labels = ax_main.get_legend_handles_labels()
    finalize_figure(fig, suptitle='Execution Time at n=500 by Algorithm and Instance Family',
                    legend_handles=handles, legend_labels=labels,
                    legend_ncol=3, legend_bbox=(0.5, 1.10),
                    rect=[0, 0, 1, 0.90])
    return save_figure(fig, fig_dir, 'runtime_comparison_n500')


# ─── Figure 6: DP Scaling (Clean Linear) ──────────────────────────────────
def generate_figure_dp_scaling(fig_dir, table4_rows, families, ns):
    print("Generating Figure 6: dp_scaling...")
    fig, ax = create_figure_single(figsize=(7.0, 3.8))

    for fam in families:
        fam_idx = families.index(fam) + 1
        ns_dp = []
        means_dp = []
        cis_dp = []
        for row in table4_rows:
            n_val = int(row[0])
            cell = row[fam_idx]
            if cell != '---':
                try:
                    parts = cell.split(' (CI: ')
                    mean_val = float(parts[0])
                    ci_part = parts[1].rstrip(')')
                    ci_lower, ci_upper = map(float, ci_part.split('–'))
                    ns_dp.append(n_val)
                    means_dp.append(mean_val)
                    cis_dp.append((ci_lower, ci_upper))
                except:
                    pass
        if ns_dp:
            ax.errorbar(ns_dp, means_dp,
                        yerr=[[m - c[0] for m, c in zip(means_dp, cis_dp)],
                              [c[1] - m for m, c in zip(means_dp, cis_dp)]],
                        marker='o', color=FAM_COLORS[fam], label=get_fam_short(fam),
                        linewidth=LINE_WIDTH, markersize=MARKER_SIZE + 1,
                        capsize=ERROR_CAPSIZE + 1, capthick=ERROR_CAPTHICK,
                        elinewidth=ERROR_LINEWIDTH, alpha=0.85, zorder=3)

    setup_axes(ax, xlabel='Problem Size (n)', ylabel='DP Runtime (ms)',
               title='Dynamic Programming Runtime Scaling with n (W=1000 fixed)',
               grid=True, x_fixed_ticks=ns)

    # Legend outside plotting area (top center)
    handles, labels = ax.get_legend_handles_labels()
    fig.legend(handles, labels, loc='upper center', bbox_to_anchor=(0.5, 1.12),
               ncol=3, frameon=True, fontsize=LEGEND_FONTSIZE, fancybox=True,
               framealpha=0.95, columnspacing=0.7, handletextpad=0.4, borderpad=0.3)
    finalize_figure(fig, rect=[0, 0, 1, 0.90])
    return save_figure(fig, fig_dir, 'dp_scaling')


def generate_all_figures(rows, greedy_rows, bb_rows, families, algorithms,
                         fig_dir, max_n, ns, table4_rows=None):
    setup_publication_style()
    os.makedirs(fig_dir, exist_ok=True)

    all_files = []
    files = generate_figure_runtime_vs_n(fig_dir, rows, families, algorithms, max_n, ns)
    all_files.extend([os.path.basename(f) for f in files])
    files = generate_figure_greedy_gap(fig_dir, greedy_rows, families)
    all_files.extend([os.path.basename(f) for f in files])
    files = generate_figure_bb_nodes(fig_dir, bb_rows, families)
    all_files.extend([os.path.basename(f) for f in files])
    files = generate_figure_bb_runtime(fig_dir, bb_rows, families, max_n)
    all_files.extend([os.path.basename(f) for f in files])
    files = generate_figure_runtime_comparison(fig_dir, rows, families, algorithms, max_n)
    all_files.extend([os.path.basename(f) for f in files])
    if table4_rows is not None:
        files = generate_figure_dp_scaling(fig_dir, table4_rows, families, ns)
        all_files.extend([os.path.basename(f) for f in files])

    return sorted(all_files)