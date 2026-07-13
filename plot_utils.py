#!/usr/bin/env python3
"""
Publication-quality plotting utilities for Knapsack Empirical Comparison.

Generates figures meeting IEEE/Springer/INFORMS/ACM standards:
- Linear scales with broken axes & inset zooms for outliers
- Consistent typography, colors, and styling
- 600 DPI PNG, vector PDF/SVG exports
"""

import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib.ticker import FixedLocator, MaxNLocator
import numpy as np


# ─── Color Schemes (Okabe-Ito / Wong - Colorblind Safe) ────────────────
ALGO_COLORS = {
    'Greedy': '#0072B2',           # Blue
    'DynamicProgramming': '#D55E00',  # Vermillion
    'BranchAndBound': '#009E73',     # Bluish Green
}

ALGO_MARKERS = {
    'Greedy': 'o',
    'DynamicProgramming': 's',
    'BranchAndBound': '^',
}

FAM_COLORS = {
    'Uncorrelated': '#0072B2',       # Blue
    'WeaklyCorrelated': '#D55E00',   # Vermillion
    'StronglyCorrelated': '#009E73', # Bluish Green
    'InverseCorrelated': '#CC79A7',  # Reddish Purple
    'AlmostEqualRatios': '#E69F00',  # Orange
}

FAM_SHORT = {
    'Uncorrelated': 'Uncorr.',
    'WeaklyCorrelated': 'WeakCorr.',
    'StronglyCorrelated': 'StrongCorr.',
    'InverseCorrelated': 'InverseCorr.',
    'AlmostEqualRatios': 'EqualRatios',
}


# ─── Shared Typography Constants ──────────────────────────────────────
TITLE_FONTSIZE = 10
LABEL_FONTSIZE = 9
TICK_FONTSIZE = 8
LEGEND_FONTSIZE = 7
SUP_FONTSIZE = 11
MARKER_SIZE = 4
LINE_WIDTH = 1.3
ERROR_CAPSIZE = 2.5
ERROR_CAPTHICK = 0.8
ERROR_LINEWIDTH = 0.8
BOX_WIDTH = 0.6
GRID_ALPHA = 0.3
GRID_LW = 0.5
SPINE_LW = 0.6


# ─── Axis Helpers ─────────────────────────────────────────────────────
def add_major_grid_only(ax):
    ax.grid(True, which='major', axis='both', alpha=GRID_ALPHA, linewidth=GRID_LW, color='#cccccc')
    ax.grid(False, which='minor', axis='both')


def setup_axes(ax, xlabel=None, ylabel=None, title=None, grid=True,
               x_fixed_ticks=None, y_lim=None, show_xlabel=True, show_ylabel=True):
    """Configure a linear-scale axis with consistent styling."""
    if show_xlabel and xlabel:
        ax.set_xlabel(xlabel, fontsize=LABEL_FONTSIZE, labelpad=4)
    if show_ylabel and ylabel:
        ax.set_ylabel(ylabel, fontsize=LABEL_FONTSIZE, labelpad=4)
    if title:
        ax.set_title(title, fontsize=TITLE_FONTSIZE, fontweight='bold', pad=5)

    if x_fixed_ticks is not None:
        ax.xaxis.set_major_locator(FixedLocator(x_fixed_ticks))
        ax.xaxis.set_major_formatter(lambda x, _: f'{int(x)}')
    else:
        ax.xaxis.set_major_locator(MaxNLocator(nbins=5, integer=True, prune='both'))

    ax.yaxis.set_major_locator(MaxNLocator(nbins=5, prune='both'))
    ax.tick_params(axis='both', labelsize=TICK_FONTSIZE, width=SPINE_LW, length=3)

    if y_lim is not None:
        ax.set_ylim(y_lim)

    if grid:
        add_major_grid_only(ax)

    for spine in ('top', 'right'):
        ax.spines[spine].set_visible(False)
    for spine in ('bottom', 'left'):
        ax.spines[spine].set_linewidth(SPINE_LW)
        ax.spines[spine].set_color('#333333')


def style_boxplot(bp, facecolor, alpha=0.5, edgecolor='#333333'):
    for patch in bp['boxes']:
        patch.set_facecolor(facecolor); patch.set_alpha(alpha)
        patch.set_edgecolor(edgecolor); patch.set_linewidth(SPINE_LW)
    for whisker in bp['whiskers']:
        whisker.set_color(edgecolor); whisker.set_linewidth(SPINE_LW)
    for cap in bp['caps']:
        cap.set_color(edgecolor); cap.set_linewidth(SPINE_LW)
    for median in bp['medians']:
        median.set_color('#333333'); median.set_linewidth(1.5)
    for flier in bp['fliers']:
        flier.set_marker('o'); flier.set_markersize(2.5)
        flier.set_markerfacecolor('#666666'); flier.set_markeredgecolor(edgecolor)
        flier.set_alpha(0.4)


def create_broken_y_axis(ax_bottom, ax_top, d=0.015):
    """Add diagonal break marks between stacked axes for broken Y-axis."""
    ax_bottom.spines['top'].set_visible(False)
    ax_top.spines['bottom'].set_visible(False)

    kwargs = dict(color='k', clip_on=False, linewidth=0.8, transform=ax_bottom.transAxes)
    ax_bottom.plot((-d, +d), (-d, +d), **kwargs)       # bottom-left
    ax_bottom.plot((1-d, 1+d), (-d, +d), **kwargs)     # bottom-right

    kwargs.update(transform=ax_top.transAxes)
    ax_top.plot((-d, +d), (1-d, 1+d), **kwargs)        # top-left
    ax_top.plot((1-d, 1+d), (1-d, 1+d), **kwargs)      # top-right


def add_inset_zoom(ax_main, xlim, ylim, loc='upper left', width='35%', height='35%'):
    """Add inset zoom with connector lines. Returns inset axis."""
    from mpl_toolkits.axes_grid1.inset_locator import inset_axes, mark_inset
    ax_inset = inset_axes(ax_main, width=width, height=height, loc=loc,
                          borderpad=1.5, axes_class=type(ax_main))
    ax_inset.set_xlim(xlim)
    ax_inset.set_ylim(ylim)
    ax_inset.patch.set_facecolor('#fafafa')
    ax_inset.patch.set_edgecolor('#999999')
    ax_inset.patch.set_linewidth(0.8)

    for spine in ax_inset.spines.values():
        spine.set_linewidth(0.5)
        spine.set_color('#666666')
    ax_inset.tick_params(labelsize=5, width=0.5, length=2)
    ax_inset.xaxis.set_major_locator(MaxNLocator(nbins=4, prune='both'))
    ax_inset.yaxis.set_major_locator(MaxNLocator(nbins=4, prune='both'))

    # Connector lines from main plot to inset
    mark_inset(ax_main, ax_inset, loc1=2, loc2=4, fc="none", ec='0.5', lw=0.8)
    return ax_inset


# ─── Global Style ─────────────────────────────────────────────────────
def setup_publication_style():
    plt.rcParams.update({
        'font.family': 'sans-serif',
        'font.sans-serif': ['DejaVu Sans', 'Arial', 'Helvetica'],
        'font.size': TICK_FONTSIZE,
        'axes.titlesize': TITLE_FONTSIZE,
        'axes.labelsize': LABEL_FONTSIZE,
        'legend.fontsize': LEGEND_FONTSIZE,
        'xtick.labelsize': TICK_FONTSIZE,
        'ytick.labelsize': TICK_FONTSIZE,
        'axes.linewidth': SPINE_LW,
        'axes.edgecolor': '#333333',
        'axes.labelcolor': '#333333',
        'xtick.color': '#333333',
        'ytick.color': '#333333',
        'text.color': '#333333',
        'figure.dpi': 600,
        'savefig.dpi': 600,
        'savefig.bbox': 'tight',
        'savefig.transparent': False,
        'savefig.facecolor': 'white',
        'grid.color': '#cccccc',
        'grid.linewidth': GRID_LW,
        'grid.alpha': GRID_ALPHA,
        'lines.linewidth': LINE_WIDTH,
        'lines.markersize': MARKER_SIZE,
        'errorbar.capsize': ERROR_CAPSIZE,
        'boxplot.boxprops.linewidth': SPINE_LW,
        'boxplot.whiskerprops.linewidth': SPINE_LW,
        'boxplot.capprops.linewidth': SPINE_LW,
        'boxplot.medianprops.linewidth': 1.5,
        'boxplot.medianprops.color': '#333333',
        'boxplot.flierprops.markersize': 2.5,
        'boxplot.flierprops.marker': 'o',
        'boxplot.flierprops.markerfacecolor': '#666666',
        'boxplot.flierprops.markeredgecolor': '#333333',
        'axes.spines.top': False,
        'axes.spines.right': False,
    })


def save_figure(fig, fig_dir, basename, formats=('png', 'pdf', 'svg')):
    saved = []
    for fmt in formats:
        path = os.path.join(fig_dir, f'{basename}.{fmt}')
        fig.savefig(path, format=fmt, dpi=600, bbox_inches='tight', facecolor='white')
        saved.append(path)
    return saved


def create_figure_single(figsize=(7.0, 3.8)):
    fig, ax = plt.subplots(figsize=figsize)
    return fig, ax


def create_figure_subplots(nrows, ncols, figsize=(11.0, 3.5), sharex=False, sharey=False):
    fig, axes = plt.subplots(nrows, ncols, figsize=figsize, sharex=sharex, sharey=sharey)
    if nrows * ncols == 1:
        axes = np.array([axes])
    return fig, axes.flatten()


def finalize_figure(fig, suptitle=None, legend_handles=None, legend_labels=None,
                    legend_loc='upper center', legend_bbox=(0.5, 1.12),
                    legend_ncol=3, tight=True, rect=None):
    if suptitle:
        fig.suptitle(suptitle, fontsize=SUP_FONTSIZE, fontweight='bold', y=0.98)
    if legend_handles and legend_labels:
        fig.legend(legend_handles, legend_labels, loc=legend_loc,
                   bbox_to_anchor=legend_bbox, ncol=legend_ncol,
                   frameon=True, fontsize=LEGEND_FONTSIZE, fancybox=True,
                   framealpha=0.95, columnspacing=0.7, handletextpad=0.4, borderpad=0.3)
    if tight:
        if rect:
            fig.tight_layout(rect=rect)
        else:
            fig.tight_layout()
    return fig


# ─── Helpers ──────────────────────────────────────────────────────────
def get_algo_color(algo): return ALGO_COLORS.get(algo, '#333333')
def get_algo_marker(algo): return ALGO_MARKERS.get(algo, 'o')
def get_fam_color(fam): return FAM_COLORS.get(fam, '#333333')
def get_fam_short(fam): return FAM_SHORT.get(fam, fam)

def group_by_n(rows, key_n='n', key_val='time_ms'):
    from collections import defaultdict
    import statistics
    by_n = defaultdict(list)
    for r in rows:
        by_n[r[key_n]].append(r[key_val])
    ns = sorted(by_n.keys())
    means = [statistics.mean(by_n[n]) for n in ns]
    medians = [statistics.median(by_n[n]) for n in ns]
    stds = [statistics.stdev(by_n[n]) if len(by_n[n]) > 1 else 0 for n in ns]
    return ns, means, medians, stds, by_n

def compute_bootstrap_ci(data, n_bootstrap=5000, confidence=0.95):
    import random, statistics
    if len(data) < 2:
        return (data[0], data[0]) if data else (0, 0)
    stats = []
    n = len(data)
    for _ in range(n_bootstrap):
        sample = [data[i] for i in [int(random.random() * n) for _ in range(n)]]
        stats.append(statistics.mean(sample))
    stats.sort()
    alpha = (1 - confidence) / 2
    return (stats[int(alpha * n_bootstrap)], stats[int((1 - alpha) * n_bootstrap)])


__all__ = [
    'setup_publication_style', 'save_figure', 'style_boxplot', 'add_major_grid_only',
    'setup_axes', 'create_broken_y_axis', 'add_inset_zoom',
    'get_algo_color', 'get_algo_marker', 'get_fam_color', 'get_fam_short',
    'create_figure_single', 'create_figure_subplots', 'finalize_figure',
    'group_by_n', 'compute_bootstrap_ci',
    'ALGO_COLORS', 'ALGO_MARKERS', 'FAM_COLORS', 'FAM_SHORT',
]