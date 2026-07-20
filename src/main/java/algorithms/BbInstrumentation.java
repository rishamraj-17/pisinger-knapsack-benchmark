package algorithms;

/**
 * Passive instrumentation collector for Branch & Bound search dynamics.
 *
 * Records per-instance search characteristics without influencing algorithm
 * behaviour. All methods are no-ops when stats is null, enabling the JIT
 * to elide instrumentation in the non-instrumented code path.
 *
 * Every metric is a running aggregate — no per-node storage is retained
 * beyond the duration of a single solve() call.
 */
public final class BbInstrumentation {

    // -----------------------------------------------------------------------
    // Identifiers (set before search)
    // -----------------------------------------------------------------------
    private int instanceId;
    private int n;
    private String family;
    private int capacity;
    private int seed;

    public void setInstanceId(int v) { instanceId = v; }
    public void setN(int v) { n = v; }
    public void setFamily(String v) { family = v; }
    public void setCapacity(int v) { capacity = v; }
    public void setSeed(int v) { seed = v; }

    // -----------------------------------------------------------------------
    // Search tree
    // -----------------------------------------------------------------------
    private long nodesExplored;
    private long leafNodes;
    private long internalNodes;
    private int maxDepth;
    private long sumDepth;
    private long sumDepthSq;
    private int minDepth = Integer.MAX_VALUE;
    private int[] depthHistogram = new int[1001]; // max level ≤ 1000

    // -----------------------------------------------------------------------
    // Queue
    // -----------------------------------------------------------------------
    private int maxQueueSize;
    private long sumQueueSize;
    private long queueSamples;
    // Buckets: 0-10, 11-50, 51-100, 101-500, 501-1000, 1001-5000, 5001+
    private long[] queueHistogram = new long[7];
    private int finalQueueSize;

    // -----------------------------------------------------------------------
    // Bounds
    // -----------------------------------------------------------------------
    private double sumBound;
    private double sumBoundSq;
    private double minBound = Double.MAX_VALUE;
    private double maxBound = -Double.MAX_VALUE;
    private double sumBoundGap;
    private double sumBoundGapSq;

    // -----------------------------------------------------------------------
    // Pruning reasons
    // -----------------------------------------------------------------------
    private long prunedByBound;
    private long prunedByCap;

    // -----------------------------------------------------------------------
    // Branching
    // -----------------------------------------------------------------------
    private long leftBranches;
    private long rightBranches;
    private long skippedLeftInfeasible;
    private long skippedLeftBound;
    private long skippedRightBound;
    private long skippedByCap;

    // -----------------------------------------------------------------------
    // Nodes generated (root + left + right added to queue)
    // -----------------------------------------------------------------------
    private long nodesGenerated;

    // -----------------------------------------------------------------------
    // Incumbent improvements
    // -----------------------------------------------------------------------
    private long improvementCount;
    private long sumImprovementAmount;
    private int firstImprovementNode;
    private boolean firstImprovementSet;
    private int lastImprovementNode;
    private int maxImprovements = 1000;
    private int[] improvementDepths;
    private int[] improvementNodes;
    private int improvementIdx;

    public BbInstrumentation() {
        improvementDepths = new int[maxImprovements];
        improvementNodes = new int[maxImprovements];
    }

    // -----------------------------------------------------------------------
    // Record methods (called from instrumented solve)
    // -----------------------------------------------------------------------

    public void recordNodeExplored(int depth, double bound, int bestValue, int queueSize) {
        nodesExplored++;

        // Depth
        if (depth > maxDepth) maxDepth = depth;
        if (depth < minDepth) minDepth = depth;
        sumDepth += depth;
        sumDepthSq += (long) depth * depth;
        if (depth <= 1000) depthHistogram[depth]++;

        // Bound
        sumBound += bound;
        sumBoundSq += bound * bound;
        if (bound < minBound) minBound = bound;
        if (bound > maxBound) maxBound = bound;

        // Bound gap (bound - incumbent, always >= 0 since bound-pruned nodes are skipped)
        double gap = bound - bestValue;
        sumBoundGap += gap;
        sumBoundGapSq += gap * gap;

        // Queue
        sumQueueSize += queueSize;
        queueSamples++;
        if (queueSize > maxQueueSize) maxQueueSize = queueSize;
        int bucket = queueSize <= 10 ? 0
                   : queueSize <= 50 ? 1
                   : queueSize <= 100 ? 2
                   : queueSize <= 500 ? 3
                   : queueSize <= 1000 ? 4
                   : queueSize <= 5000 ? 5
                   : 6;
        queueHistogram[bucket]++;
        finalQueueSize = queueSize;
    }

    public void recordLeaf() {
        leafNodes++;
    }

    public void recordInternal() {
        internalNodes++;
    }

    public void recordGenerated() {
        nodesGenerated++;
    }

    public void recordPruneByBound() {
        prunedByBound++;
    }

    public void recordPruneByCap() {
        prunedByCap++;
    }

    public void recordLeftBranch() {
        leftBranches++;
    }

    public void recordRightBranch() {
        rightBranches++;
    }

    public void recordSkippedLeftInfeasible() {
        skippedLeftInfeasible++;
    }

    public void recordSkippedLeftBound() {
        skippedLeftBound++;
    }

    public void recordSkippedRightBound() {
        skippedRightBound++;
    }

    public void recordSkippedByCap() {
        skippedByCap++;
    }

    public void recordImprovement(int depth, int oldValue, int newValue) {
        improvementCount++;
        int amount = newValue - oldValue;
        sumImprovementAmount += amount;
        if (!firstImprovementSet) {
            firstImprovementNode = (int) nodesExplored;
            firstImprovementSet = true;
        }
        lastImprovementNode = (int) nodesExplored;
        if (improvementIdx < maxImprovements) {
            improvementDepths[improvementIdx] = depth;
            improvementNodes[improvementIdx] = (int) nodesExplored;
            improvementIdx++;
        }
    }

    // -----------------------------------------------------------------------
    // Accessors for CSV export
    // -----------------------------------------------------------------------

    public int getInstanceId() { return instanceId; }
    public int getN() { return n; }
    public String getFamily() { return family; }
    public int getCapacity() { return capacity; }
    public int getSeed() { return seed; }

    public long getNodesGenerated() { return nodesGenerated; }
    public long getNodesExplored() { return nodesExplored; }
    public long getLeafNodes() { return leafNodes; }
    public long getInternalNodes() { return internalNodes; }
    public int getMaxDepth() { return maxDepth; }
    public double getMeanDepth() { return nodesExplored > 0 ? (double) sumDepth / nodesExplored : 0.0; }
    public int getMinDepth() { return minDepth == Integer.MAX_VALUE ? 0 : minDepth; }

    public double getMedianDepth() {
        if (nodesExplored == 0) return 0.0;
        long target = nodesExplored / 2;
        long count = 0;
        for (int d = 0; d < depthHistogram.length; d++) {
            count += depthHistogram[d];
            if (count > target) return d;
        }
        return maxDepth;
    }

    public String getDepthHistogramCsv() {
        StringBuilder sb = new StringBuilder();
        int maxD = Math.min(maxDepth, 1000);
        for (int d = 0; d <= maxD; d++) {
            if (d > 0) sb.append(',');
            sb.append(depthHistogram[d]);
        }
        return sb.toString();
    }

    public int getMaxQueueSize() { return maxQueueSize; }
    public double getMeanQueueSize() { return queueSamples > 0 ? (double) sumQueueSize / queueSamples : 0.0; }
    public int getFinalQueueSize() { return finalQueueSize; }

    public String getQueueHistogramCsv() {
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < queueHistogram.length; i++) {
            if (i > 0) sb.append(',');
            sb.append(queueHistogram[i]);
        }
        return sb.toString();
    }

    public double getMeanBound() { return nodesExplored > 0 ? sumBound / nodesExplored : 0.0; }
    public double getBoundVariance() {
        if (nodesExplored <= 1) return 0.0;
        double mean = sumBound / nodesExplored;
        return (sumBoundSq / nodesExplored) - (mean * mean);
    }
    public double getMinBound() { return minBound == Double.MAX_VALUE ? 0.0 : minBound; }
    public double getMaxBound() { return maxBound == -Double.MAX_VALUE ? 0.0 : maxBound; }

    public double getMeanBoundGap() { return nodesExplored > 0 ? sumBoundGap / nodesExplored : 0.0; }
    public double getBoundGapVariance() {
        if (nodesExplored <= 1) return 0.0;
        double mean = sumBoundGap / nodesExplored;
        return (sumBoundGapSq / nodesExplored) - (mean * mean);
    }

    public long getPrunedByBound() { return prunedByBound; }
    public long getPrunedByCap() { return prunedByCap; }

    public long getLeftBranches() { return leftBranches; }
    public long getRightBranches() { return rightBranches; }
    public long getExploredChildren() { return leftBranches + rightBranches; }
    public long getSkippedChildren() {
        return skippedLeftInfeasible + skippedLeftBound + skippedRightBound + skippedByCap;
    }
    public long getSkippedInfeasible() { return skippedLeftInfeasible; }
    public long getSkippedByBound() { return skippedLeftBound + skippedRightBound; }
    public long getSkippedByCap() { return skippedByCap; }

    public long getImprovementCount() { return improvementCount; }
    public long getSumImprovementAmount() { return sumImprovementAmount; }
    public double getMeanImprovementAmount() {
        return improvementCount > 0 ? (double) sumImprovementAmount / improvementCount : 0.0;
    }
    public int getFirstImprovementNode() {
        return firstImprovementSet ? firstImprovementNode : 0;
    }
    public int getLastImprovementNode() { return lastImprovementNode; }

    public String getImprovementDepthsCsv() {
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < improvementIdx; i++) {
            if (i > 0) sb.append(',');
            sb.append(improvementDepths[i]);
        }
        return sb.toString();
    }

    public String getImprovementNodesCsv() {
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < improvementIdx; i++) {
            if (i > 0) sb.append(',');
            sb.append(improvementNodes[i]);
        }
        return sb.toString();
    }

    public double getExploredGeneratedRatio() {
        return nodesGenerated > 0 ? (double) nodesExplored / nodesGenerated : 0.0;
    }

    public double getPrunedGeneratedRatio() {
        long totalPruned = prunedByBound + prunedByCap;
        return nodesGenerated > 0 ? (double) totalPruned / nodesGenerated : 0.0;
    }

    public double getAvgBranchingFactor() {
        return nodesExplored > 0 ? (double) (leftBranches + rightBranches) / nodesExplored : 0.0;
    }

    // -----------------------------------------------------------------------
    // CSV header
    // -----------------------------------------------------------------------

    public static String[] csvHeader() {
        return new String[]{
            "instance_id", "n", "family", "capacity_mode", "capacity", "seed",
            "nodes_generated", "nodes_explored", "leaf_nodes", "internal_nodes",
            "max_depth", "mean_depth", "median_depth", "min_depth",
            "depth_histogram",
            "max_queue_size", "mean_queue_size", "final_queue_size",
            "queue_histogram",
            "mean_bound", "bound_variance", "min_bound", "max_bound",
            "mean_bound_gap", "bound_gap_variance",
            "pruned_by_bound", "pruned_by_cap",
            "left_branches", "right_branches", "explored_children", "skipped_children",
            "skipped_infeasible", "skipped_by_bound", "skipped_by_cap",
            "improvement_count", "sum_improvement_amount", "mean_improvement_amount",
            "first_improvement_node", "last_improvement_node",
            "improvement_depths", "improvement_nodes",
            "explored_generated_ratio", "pruned_generated_ratio", "avg_branching_factor"
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
            String.valueOf(nodesGenerated),
            String.valueOf(nodesExplored),
            String.valueOf(leafNodes),
            String.valueOf(internalNodes),
            String.valueOf(maxDepth),
            String.format("%.4f", getMeanDepth()),
            String.format("%.1f", getMedianDepth()),
            String.valueOf(getMinDepth()),
            getDepthHistogramCsv(),
            String.valueOf(maxQueueSize),
            String.format("%.4f", getMeanQueueSize()),
            String.valueOf(finalQueueSize),
            getQueueHistogramCsv(),
            String.format("%.4f", getMeanBound()),
            String.format("%.4f", getBoundVariance()),
            String.format("%.4f", getMinBound()),
            String.format("%.4f", getMaxBound()),
            String.format("%.4f", getMeanBoundGap()),
            String.format("%.4f", getBoundGapVariance()),
            String.valueOf(prunedByBound),
            String.valueOf(prunedByCap),
            String.valueOf(leftBranches),
            String.valueOf(rightBranches),
            String.valueOf(getExploredChildren()),
            String.valueOf(getSkippedChildren()),
            String.valueOf(skippedLeftInfeasible),
            String.valueOf(getSkippedByBound()),
            String.valueOf(skippedByCap),
            String.valueOf(improvementCount),
            String.valueOf(sumImprovementAmount),
            String.format("%.4f", getMeanImprovementAmount()),
            String.valueOf(getFirstImprovementNode()),
            String.valueOf(getLastImprovementNode()),
            getImprovementDepthsCsv(),
            getImprovementNodesCsv(),
            String.format("%.6f", getExploredGeneratedRatio()),
            String.format("%.6f", getPrunedGeneratedRatio()),
            String.format("%.6f", getAvgBranchingFactor())
        };
    }
}
