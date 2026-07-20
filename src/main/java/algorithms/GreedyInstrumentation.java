package algorithms;

public final class GreedyInstrumentation {

    private int instanceId;
    private int n;
    private String family;
    private int capacity;
    private int seed;

    private int selectedCount;
    private int totalWeight;
    private int lastSelectedPosition = -1;
    private int firstSkippedPosition = -1;

    public void setInstanceId(int v) { instanceId = v; }
    public void setN(int v) { n = v; }
    public void setFamily(String v) { family = v; }
    public void setCapacity(int v) { capacity = v; }
    public void setSeed(int v) { seed = v; }

    public void recordSelection(int position) {
        selectedCount++;
        lastSelectedPosition = position;
    }

    public void recordSkip(int position) {
        if (firstSkippedPosition == -1) {
            firstSkippedPosition = position;
        }
    }

    public void finalize(int totalWeight) {
        this.totalWeight = totalWeight;
    }

    public int getInstanceId() { return instanceId; }
    public int getN() { return n; }
    public String getFamily() { return family; }
    public int getCapacity() { return capacity; }
    public int getSeed() { return seed; }

    public int getSelectedCount() { return selectedCount; }
    public int getTotalWeight() { return totalWeight; }
    public int getLastSelectedPosition() { return lastSelectedPosition; }
    public int getFirstSkippedPosition() { return firstSkippedPosition; }

    public double getSolutionDensity() {
        if (n == 0) return 0.0;
        return (double) selectedCount / n;
    }

    public int getResidualCapacity() {
        return capacity - totalWeight;
    }

    public double getCapacityUtilization() {
        if (capacity == 0) return 0.0;
        return (double) totalWeight / capacity;
    }

    public static String[] csvHeader() {
        return new String[]{
            "instance_id", "n", "family", "capacity_mode", "capacity", "seed",
            "selected_count", "solution_density", "residual_capacity",
            "capacity_utilization", "last_selected_position", "first_skipped_position"
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
            String.valueOf(selectedCount),
            String.format("%.6f", getSolutionDensity()),
            String.valueOf(getResidualCapacity()),
            String.format("%.6f", getCapacityUtilization()),
            String.valueOf(lastSelectedPosition),
            String.valueOf(firstSkippedPosition)
        };
    }
}
