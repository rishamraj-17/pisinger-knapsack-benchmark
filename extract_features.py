#!/usr/bin/env python3
"""
Phase 2.1: Instance feature extraction for the Knapsack Empirical Comparison.

Generates results/instances.csv containing descriptive features for every
generated knapsack instance, without modifying any benchmark outputs.

Usage:
  python3 extract_features.py [n-values] [capacity] [instances-per-config] [seed]

All arguments are optional. Defaults match the full reproduction pipeline:
  n-values: 20,50,100,200,500,1000
  capacity: 1000
  instances-per-config: 100
  seed: 42
"""

import csv
import math
import os
import statistics
import sys
from collections import Counter

# ---------------------------------------------------------------------------
# Java Random reproduction (exact match for java.util.Random)
# ---------------------------------------------------------------------------

class JavaRandom:
    """Exact replica of java.util.Random for deterministic instance generation."""

    def __init__(self, seed):
        self.seed = (seed ^ 0x5DEECE66D) & ((1 << 48) - 1)

    def next(self, bits):
        self.seed = (self.seed * 0x5DEECE66D + 0xB) & ((1 << 48) - 1)
        return self.seed >> (48 - bits)

    def nextInt(self, bound):
        r = self.next(31)
        m = bound - 1
        if (bound & m) == 0:
            return (bound * (r & 0xFFFFFFFF)) >> 31
        u = r
        rv = u % bound
        while True:
            val = (u - rv + m) & 0xFFFFFFFF
            if val >= 0x80000000:
                u = self.next(31)
                rv = u % bound
            else:
                break
        return rv

    def nextDouble(self):
        return ((self.next(26) << 27) + self.next(27)) / (1 << 53)


# ---------------------------------------------------------------------------
# Instance generators (exact replicas of Java generators)
# ---------------------------------------------------------------------------

class Family:
    UNCORRELATED = 'Uncorrelated'
    WEAKLY_CORRELATED = 'WeaklyCorrelated'
    STRONGLY_CORRELATED = 'StronglyCorrelated'
    INVERSE_CORRELATED = 'InverseCorrelated'
    ALMOST_EQUAL_RATIOS = 'AlmostEqualRatios'


def generate_uncorrelated(n, rng, max_weight=1000, max_value=1000):
    items = []
    for i in range(n):
        w = rng.nextInt(max_weight) + 1
        v = rng.nextInt(max_value) + 1
        items.append((w, v))
    return items


def generate_weakly_correlated(n, rng, max_weight=1000, delta=100):
    items = []
    for i in range(n):
        w = rng.nextInt(max_weight) + 1
        v = w + rng.nextInt(2 * delta + 1) - delta
        v = max(1, v)
        items.append((w, v))
    return items


def generate_strongly_correlated(n, rng, max_weight=1000):
    items = []
    for i in range(n):
        w = rng.nextInt(max_weight) + 1
        v = w + rng.nextInt(10) + 1
        items.append((w, v))
    return items


def generate_inverse_correlated(n, rng, max_weight=1000):
    items = []
    for i in range(n):
        w = rng.nextInt(max_weight) + 1
        v = max_weight - w + 1
        items.append((w, v))
    return items


def generate_almost_equal_ratios(n, rng, max_weight=1000, base_ratio=1.0):
    items = []
    for i in range(n):
        w = rng.nextInt(max_weight) + 1
        noise = rng.nextDouble() * 0.2 - 0.1
        v = int(round(w * base_ratio * (1 + noise)))
        v = max(1, v)
        items.append((w, v))
    return items


GENERATORS = [
    (Family.UNCORRELATED, generate_uncorrelated),
    (Family.WEAKLY_CORRELATED, generate_weakly_correlated),
    (Family.STRONGLY_CORRELATED, generate_strongly_correlated),
    (Family.INVERSE_CORRELATED, generate_inverse_correlated),
    (Family.ALMOST_EQUAL_RATIOS, generate_almost_equal_ratios),
]


def generate_instances(ns, instances_per_config, seed):
    """Generate all instances matching the Java DatasetGenerator exactly."""
    instances = []
    instance_id = 0
    for n in ns:
        rng = JavaRandom(seed + n)
        for family_name, gen_func in GENERATORS:
            for _ in range(instances_per_config):
                items = gen_func(n, rng)
                instances.append({
                    'instance_id': instance_id,
                    'n': n,
                    'family': family_name,
                    'items': items,
                })
                instance_id += 1
    return instances


# ---------------------------------------------------------------------------
# Feature computation
# ---------------------------------------------------------------------------

def compute_features(instance, capacity):
    """Compute all descriptive features for a knapsack instance."""
    items = instance['items']
    n = instance['n']
    weights = [item[0] for item in items]
    values = [item[1] for item in items]
    ratios = [v / w for w, v in items]

    total_weight = sum(weights)
    total_value = sum(values)

    mean_weight = statistics.mean(weights)
    mean_value = statistics.mean(values)

    sorted_w = sorted(weights)
    sorted_v = sorted(values)

    def _median(arr):
        m = len(arr)
        if m % 2 == 0:
            return (arr[m // 2 - 1] + arr[m // 2]) / 2.0
        return arr[m // 2]

    median_weight = _median(sorted_w)
    median_value = _median(sorted_v)

    std_weight = statistics.pstdev(weights)
    std_value = statistics.pstdev(values)

    min_weight = min(weights)
    max_weight = max(weights)
    min_value = min(values)
    max_value = max(values)

    weight_cv = std_weight / mean_weight if mean_weight > 0 else 0.0
    value_cv = std_value / mean_value if mean_value > 0 else 0.0

    def _skewness(arr):
        mu = statistics.mean(arr)
        sigma = statistics.pstdev(arr)
        if sigma == 0:
            return 0.0
        m3 = sum((x - mu) ** 3 for x in arr) / len(arr)
        return m3 / (sigma ** 3)

    def _kurtosis(arr):
        mu = statistics.mean(arr)
        sigma = statistics.pstdev(arr)
        if sigma == 0:
            return 0.0
        m4 = sum((x - mu) ** 4 for x in arr) / len(arr)
        return m4 / (sigma ** 4) - 3.0

    weight_skewness = _skewness(weights)
    value_skewness = _skewness(values)
    weight_kurtosis = _kurtosis(weights)
    value_kurtosis = _kurtosis(values)

    capacity_ratio = capacity / total_weight if total_weight > 0 else 0.0
    slack = total_weight - capacity
    average_fillable_items = capacity / mean_weight if mean_weight > 0 else 0.0

    def _pearson(x, y):
        n_ = len(x)
        mx = sum(x) / n_
        my = sum(y) / n_
        cov = sum((x[i] - mx) * (y[i] - my) for i in range(n_))
        sx = math.sqrt(sum((xi - mx) ** 2 for xi in x) / n_)
        sy = math.sqrt(sum((yi - my) ** 2 for yi in y) / n_)
        if sx == 0 or sy == 0:
            return 0.0
        return cov / (n_ * sx * sy)

    def _spearman(x, y):
        def _rank(v):
            n_ = len(v)
            sorted_v = sorted(enumerate(v), key=lambda e: e[1])
            ranks = [0] * n_
            i = 0
            while i < n_:
                j = i
                while j < n_ and sorted_v[j][1] == sorted_v[i][1]:
                    j += 1
                avg_rank = (i + j - 1) / 2.0 + 1
                for k in range(i, j):
                    ranks[sorted_v[k][0]] = avg_rank
                i = j
            return ranks

        rx = _rank(x)
        ry = _rank(y)
        return _pearson(rx, ry)

    def _kendall(x, y):
        n_ = len(x)
        concordant = 0
        discordant = 0
        for i in range(n_):
            for j in range(i + 1, n_):
                dx = x[i] - x[j]
                dy = y[i] - y[j]
                if dx > 0 and dy > 0:
                    concordant += 1
                elif dx < 0 and dy < 0:
                    concordant += 1
                elif dx != 0 and dy != 0:
                    discordant += 1
        total = concordant + discordant
        if total == 0:
            return 0.0
        return (concordant - discordant) / total

    pearson_corr = _pearson(weights, values)
    spearman_corr = _spearman(weights, values)
    kendall_corr = _kendall(weights, values)

    mean_ratio = statistics.mean(ratios)
    median_ratio = _median(sorted(ratios))
    std_ratio = statistics.pstdev(ratios)

    def _entropy(arr, bins=20):
        if len(arr) == 0:
            return 0.0
        mn = min(arr)
        mx = max(arr)
        if mx == mn:
            return 0.0
        bin_w = (mx - mn) / bins
        counts = [0] * bins
        for v in arr:
            idx = min(int((v - mn) / bin_w), bins - 1)
            counts[idx] += 1
        total = len(arr)
        ent = 0.0
        for c in counts:
            if c > 0:
                p = c / total
                ent -= p * math.log(p)
        return ent

    ratio_entropy = _entropy(ratios)

    ratio_counter = Counter(ratios)
    unique_ratio_count = len(ratio_counter)
    duplicate_ratio_fraction = (
        sum(c - 1 for c in ratio_counter.values()) / n if n > 0 else 0.0
    )

    unique_weights = len(set(weights))
    unique_values = len(set(values))
    pair_counter = Counter(items)
    unique_pairs = len(pair_counter)
    duplicate_items = sum(c - 1 for c in pair_counter.values())
    duplicate_pairs = sum(1 for c in pair_counter.values() if c > 1)

    return {
        'instance_id': instance['instance_id'],
        'n': instance['n'],
        'family': instance['family'],

        'total_weight': total_weight,
        'total_value': total_value,
        'mean_weight': mean_weight,
        'mean_value': mean_value,
        'median_weight': median_weight,
        'median_value': median_value,
        'std_weight': std_weight,
        'std_value': std_value,
        'min_weight': min_weight,
        'max_weight': max_weight,
        'min_value': min_value,
        'max_value': max_value,

        'weight_cv': weight_cv,
        'value_cv': value_cv,
        'weight_skewness': weight_skewness,
        'value_skewness': value_skewness,
        'weight_kurtosis': weight_kurtosis,
        'value_kurtosis': value_kurtosis,

        'capacity': capacity,
        'capacity_ratio': capacity_ratio,
        'slack': slack,
        'average_fillable_items': average_fillable_items,

        'pearson_corr': pearson_corr,
        'spearman_corr': spearman_corr,
        'kendall_corr': kendall_corr,

        'mean_ratio': mean_ratio,
        'median_ratio': median_ratio,
        'std_ratio': std_ratio,
        'ratio_entropy': ratio_entropy,
        'unique_ratio_count': unique_ratio_count,
        'duplicate_ratio_fraction': duplicate_ratio_fraction,

        'unique_weights': unique_weights,
        'unique_values': unique_values,
        'unique_pairs': unique_pairs,
        'duplicate_items': duplicate_items,
        'duplicate_pairs': duplicate_pairs,
    }


# ---------------------------------------------------------------------------
# CSV schema
# ---------------------------------------------------------------------------

FEATURE_FIELDS = [
    'instance_id', 'n', 'family', 'capacity_mode',
    'total_weight', 'total_value',
    'mean_weight', 'mean_value',
    'median_weight', 'median_value',
    'std_weight', 'std_value',
    'min_weight', 'max_weight',
    'min_value', 'max_value',
    'weight_cv', 'value_cv',
    'weight_skewness', 'value_skewness',
    'weight_kurtosis', 'value_kurtosis',
    'capacity',
    'capacity_ratio', 'slack', 'average_fillable_items',
    'pearson_corr', 'spearman_corr', 'kendall_corr',
    'mean_ratio', 'median_ratio', 'std_ratio',
    'ratio_entropy', 'unique_ratio_count', 'duplicate_ratio_fraction',
    'unique_weights', 'unique_values', 'unique_pairs',
    'duplicate_items', 'duplicate_pairs',
]


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    ns = [20, 50, 100, 200, 500, 1000]
    capacity = 1000
    instances_per_config = 100
    seed = 42

    if len(sys.argv) > 1:
        ns = [int(x) for x in sys.argv[1].split(',')]
    if len(sys.argv) > 2:
        capacity = int(sys.argv[2])
    if len(sys.argv) > 3:
        instances_per_config = int(sys.argv[3])
    if len(sys.argv) > 4:
        seed = int(sys.argv[4])

    os.makedirs('results', exist_ok=True)

    all_instances = generate_instances(ns, instances_per_config, seed)
    print(f"Generated {len(all_instances)} base instances")

    all_features = []
    for inst in all_instances:
        total_w = sum(item[0] for item in inst['items'])
        feat_fixed = compute_features(inst, capacity)
        feat_fixed['capacity_mode'] = 'fixed'
        all_features.append(feat_fixed)
        scaled_cap = int(total_w * 0.5)
        feat_scaled = compute_features(inst, scaled_cap)
        feat_scaled['capacity_mode'] = 'scaled'
        all_features.append(feat_scaled)

    output_path = os.path.join('results', 'instances.csv')
    with open(output_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=FEATURE_FIELDS, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(all_features)

    print(f"Exported {len(all_features)} feature rows to {output_path}")
    print(f"  Fixed mode: {len([r for r in all_features if r['capacity_mode'] == 'fixed'])} rows")
    print(f"  Scaled mode: {len([r for r in all_features if r['capacity_mode'] == 'scaled'])} rows")
    print("Done.")


if __name__ == '__main__':
    main()
