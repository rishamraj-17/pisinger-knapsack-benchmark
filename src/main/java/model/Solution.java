package model;

import java.util.Arrays;

public final class Solution {
    private final int instanceId;
    private final String algorithm;
    private final long timeNanos;
    private final int totalValue;
    private final int totalWeight;
    private final boolean[] included;
    private final boolean optimal;

    public Solution(int instanceId, String algorithm, long timeNanos, int totalValue, int totalWeight, boolean[] included, boolean optimal) {
        this.instanceId = instanceId;
        this.algorithm = algorithm;
        this.timeNanos = timeNanos;
        this.totalValue = totalValue;
        this.totalWeight = totalWeight;
        this.included = included.clone();
        this.optimal = optimal;
    }

    public int getInstanceId() {
        return instanceId;
    }

    public String getAlgorithm() {
        return algorithm;
    }

    public long getTimeNanos() {
        return timeNanos;
    }

    public double getTimeMillis() {
        return timeNanos / 1_000_000.0;
    }

    public int getTotalValue() {
        return totalValue;
    }

    public int getTotalWeight() {
        return totalWeight;
    }

    public boolean[] getIncluded() {
        return included.clone();
    }

    public boolean isOptimal() {
        return optimal;
    }

    public double getOptimalityGap(int optimalValue) {
        if (optimalValue == 0) return 0.0;
        return (optimalValue - totalValue) / (double) optimalValue;
    }

    @Override
    public String toString() {
        return "Solution{alg=" + algorithm + ", val=" + totalValue + ", wt=" + totalWeight + ", time=" + String.format("%.3f", getTimeMillis()) + "ms, opt=" + optimal + "}";
    }
}