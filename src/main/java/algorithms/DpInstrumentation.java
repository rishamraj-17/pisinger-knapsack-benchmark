package algorithms;

public final class DpInstrumentation {

    private int instanceId;
    private int n;
    private String family;
    private int capacity;
    private int seed;

    private long totalEvaluations;
    private long includeCount;
    private long excludeCount;
    private long tieCount;

    private int optimalValue;
    private long nonzeroValueStates;
    private long sumValue;
    private long sumValueSq;

    private long sumImprovementAmount;

    public void setInstanceId(int v) { instanceId = v; }
    public void setN(int v) { n = v; }
    public void setFamily(String v) { family = v; }
    public void setCapacity(int v) { capacity = v; }
    public void setSeed(int v) { seed = v; }

    public void recordTransition(int newVal, int oldVal) {
        totalEvaluations++;
        if (newVal > oldVal) {
            includeCount++;
            sumImprovementAmount += (newVal - oldVal);
        } else if (newVal == oldVal) {
            tieCount++;
        } else {
            excludeCount++;
        }
    }

    public void finalizeStats(int[] dp) {
        optimalValue = dp[capacity];
        nonzeroValueStates = 0;
        sumValue = 0;
        sumValueSq = 0;
        for (int c = 0; c <= capacity; c++) {
            if (dp[c] > 0) nonzeroValueStates++;
            sumValue += dp[c];
            sumValueSq += (long) dp[c] * dp[c];
        }
    }

    public int getInstanceId() { return instanceId; }
    public int getN() { return n; }
    public String getFamily() { return family; }
    public int getCapacity() { return capacity; }
    public int getSeed() { return seed; }

    public double getCapacityDensity() { return n > 0 ? (double) capacity / n : 0.0; }

    public int getCellsAllocated() { return capacity + 1; }

    public long getTotalEvaluations() { return totalEvaluations; }

    public long getIncludeCount() { return includeCount; }
    public long getExcludeCount() { return excludeCount; }
    public long getTieCount() { return tieCount; }
    public double getIncludeRatio() {
        return totalEvaluations > 0 ? (double) includeCount / totalEvaluations : 0.0;
    }

    public long getNonzeroValueStates() { return nonzeroValueStates; }
    public long getZeroValueStates() { return getCellsAllocated() - nonzeroValueStates; }
    public double getFillRate() {
        int ca = getCellsAllocated();
        return ca > 0 ? (double) nonzeroValueStates / ca : 0.0;
    }

    public int getOptimalValue() { return optimalValue; }

    public double getMeanCellValue() {
        int ca = getCellsAllocated();
        return ca > 0 ? (double) sumValue / ca : 0.0;
    }

    public double getCellValueVariance() {
        int ca = getCellsAllocated();
        if (ca <= 1) return 0.0;
        double mean = (double) sumValue / ca;
        return (double) sumValueSq / ca - mean * mean;
    }

    public long getSumImprovementAmount() { return sumImprovementAmount; }
    public double getMeanImprovementAmount() {
        return includeCount > 0 ? (double) sumImprovementAmount / includeCount : 0.0;
    }

    public double getUpdatesPerCell() {
        int ca = getCellsAllocated();
        return ca > 0 ? (double) includeCount / ca : 0.0;
    }

    public static String[] csvHeader() {
        return new String[]{
            "instance_id", "n", "family", "capacity_mode", "capacity", "seed",
            "capacity_density",
            "cells_allocated", "total_evaluations",
            "include_count", "exclude_count", "tie_count", "include_ratio",
            "nonzero_value_states", "zero_value_states", "fill_rate",
            "optimal_value", "mean_cell_value", "cell_value_variance",
            "sum_improvement_amount", "mean_improvement_amount",
            "updates_per_cell"
        };
    }

    public String[] toCsvRow(String capacityMode) {
        return new String[]{
            String.valueOf(instanceId),
            String.valueOf(n),
            family,
            capacityMode,
            String.valueOf(capacity),
            String.valueOf(seed),
            String.format("%.4f", getCapacityDensity()),
            String.valueOf(getCellsAllocated()),
            String.valueOf(totalEvaluations),
            String.valueOf(includeCount),
            String.valueOf(excludeCount),
            String.valueOf(tieCount),
            String.format("%.6f", getIncludeRatio()),
            String.valueOf(nonzeroValueStates),
            String.valueOf(getZeroValueStates()),
            String.format("%.6f", getFillRate()),
            String.valueOf(optimalValue),
            String.format("%.4f", getMeanCellValue()),
            String.format("%.4f", getCellValueVariance()),
            String.valueOf(sumImprovementAmount),
            String.format("%.4f", getMeanImprovementAmount()),
            String.format("%.6f", getUpdatesPerCell())
        };
    }
}
