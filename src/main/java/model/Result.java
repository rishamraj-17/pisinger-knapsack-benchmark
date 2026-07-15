package model;

public final class Result {
    private final String algorithm;
    private final String datasetType;
    private final int n;
    private final int capacity;
    private final int instanceId;
    private final int seed;
    private final long timeNanos;
    private final long memoryBytes;
    private final int solutionValue;
    private final int optimalValue;
    private final double optimalityGap;
    private final long nodesExplored;
    private final long nodesPruned;
    private final int maxQueueSize;
    private final boolean optimal;

    private Result(Builder builder) {
        this.algorithm = builder.algorithm;
        this.datasetType = builder.datasetType;
        this.n = builder.n;
        this.capacity = builder.capacity;
        this.instanceId = builder.instanceId;
        this.seed = builder.seed;
        this.timeNanos = builder.timeNanos;
        this.memoryBytes = builder.memoryBytes;
        this.solutionValue = builder.solutionValue;
        this.optimalValue = builder.optimalValue;
        this.optimalityGap = builder.optimalityGap;
        this.nodesExplored = builder.nodesExplored;
        this.nodesPruned = builder.nodesPruned;
        this.maxQueueSize = builder.maxQueueSize;
        this.optimal = builder.optimal;
    }

    public String getAlgorithm() { return algorithm; }
    public String getDatasetType() { return datasetType; }
    public int getN() { return n; }
    public int getCapacity() { return capacity; }
    public int getInstanceId() { return instanceId; }
    public int getSeed() { return seed; }
    public long getTimeNanos() { return timeNanos; }
    public double getTimeMillis() { return timeNanos / 1_000_000.0; }
    public long getMemoryBytes() { return memoryBytes; }
    public double getMemoryMB() { return memoryBytes / (1024.0 * 1024.0); }
    public int getSolutionValue() { return solutionValue; }
    public int getOptimalValue() { return optimalValue; }
    public double getOptimalityGap() { return optimalityGap; }
    public long getNodesExplored() { return nodesExplored; }
    public long getNodesPruned() { return nodesPruned; }
    public int getMaxQueueSize() { return maxQueueSize; }
    public boolean isOptimal() { return optimal; }

    public String[] toCsvRow() {
        return new String[]{
            algorithm,
            datasetType,
            String.valueOf(n),
            String.valueOf(capacity),
            String.valueOf(instanceId),
            String.valueOf(seed),
            String.valueOf(timeNanos),
            String.format("%.3f", getTimeMillis()),
            String.valueOf(memoryBytes),
            String.format("%.3f", getMemoryMB()),
            String.valueOf(solutionValue),
            optimalValue > 0 ? String.valueOf(optimalValue) : "",
            optimalValue > 0 ? String.format("%.6f", optimalityGap) : "",
            String.valueOf(nodesExplored),
            String.valueOf(nodesPruned),
            String.valueOf(maxQueueSize),
            String.valueOf(optimal)
        };
    }

    public static String[] csvHeader() {
        return new String[]{
            "algorithm", "dataset_type", "n", "capacity", "instance_id", "seed",
            "time_nanos", "time_millis", "memory_bytes", "memory_mb",
            "solution_value", "optimal_value", "optimality_gap",
            "nodes_explored", "nodes_pruned", "max_queue_size", "optimal"
        };
    }

    public static Builder builder() {
        return new Builder();
    }

    public static final class Builder {
        private String algorithm;
        private String datasetType;
        private int n;
        private int capacity;
        private int instanceId;
        private int seed;
        private long timeNanos;
        private long memoryBytes;
        private int solutionValue;
        private int optimalValue;
        private double optimalityGap;
        private long nodesExplored;
        private long nodesPruned;
        private int maxQueueSize;
        private boolean optimal;

        public Builder algorithm(String v) { algorithm = v; return this; }
        public Builder datasetType(String v) { datasetType = v; return this; }
        public Builder n(int v) { n = v; return this; }
        public Builder capacity(int v) { capacity = v; return this; }
        public Builder instanceId(int v) { instanceId = v; return this; }
        public Builder seed(int v) { seed = v; return this; }
        public Builder timeNanos(long v) { timeNanos = v; return this; }
        public Builder memoryBytes(long v) { memoryBytes = v; return this; }
        public Builder solutionValue(int v) { solutionValue = v; return this; }
        public Builder optimalValue(int v) { optimalValue = v; return this; }
        public Builder optimalityGap(double v) { optimalityGap = v; return this; }
        public Builder nodesExplored(long v) { nodesExplored = v; return this; }
        public Builder nodesPruned(long v) { nodesPruned = v; return this; }
        public Builder maxQueueSize(int v) { maxQueueSize = v; return this; }
        public Builder optimal(boolean v) { optimal = v; return this; }

        public Result build() {
            if (optimalValue > 0) {
                optimalityGap = (optimalValue - solutionValue) / (double) optimalValue;
            }
            return new Result(this);
        }
    }
}