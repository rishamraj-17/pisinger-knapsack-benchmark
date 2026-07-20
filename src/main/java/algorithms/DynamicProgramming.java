package algorithms;

import model.Item;
import model.KnapsackInstance;
import model.Result;

public final class DynamicProgramming implements Algorithm {
    @Override
    public String getName() {
        return "DynamicProgramming";
    }

    @Override
    public Result solve(KnapsackInstance instance) {
        return solve(instance, null);
    }

    public Result solve(KnapsackInstance instance, DpInstrumentation stats) {
        long startMem = Runtime.getRuntime().totalMemory() - Runtime.getRuntime().freeMemory();
        long startTime = System.nanoTime();

        Item[] items = instance.getItems();
        int n = instance.getN();
        int capacity = instance.getCapacity();

        int[] dp = new int[capacity + 1];

        if (stats != null) {
            stats.setInstanceId(instance.getId());
            stats.setN(n);
            stats.setFamily(instance.getFamilyName());
            stats.setCapacity(capacity);
            stats.setSeed(instance.getBaseSeed());
        }

        for (int i = 0; i < n; i++) {
            if (Thread.currentThread().isInterrupted()) {
                throw new RuntimeException("DynamicProgramming interrupted");
            }
            int w = items[i].getWeight();
            int v = items[i].getValue();
            for (int wCap = capacity; wCap >= w; wCap--) {
                int newVal = dp[wCap - w] + v;
                if (stats != null) stats.recordTransition(newVal, dp[wCap]);
                if (newVal > dp[wCap]) {
                    dp[wCap] = newVal;
                }
            }
        }

        if (stats != null) {
            stats.finalizeStats(dp);
        }

        int optimalValue = dp[capacity];

        long timeNanos = System.nanoTime() - startTime;
        long endMem = Runtime.getRuntime().totalMemory() - Runtime.getRuntime().freeMemory();
        long memUsed = Math.max(0, endMem - startMem);

        return Result.builder()
                .algorithm(getName())
                .datasetType(instance.getFamilyName())
                .n(instance.getN())
                .capacity(instance.getCapacity())
                .instanceId(instance.getId())
                .seed(instance.getBaseSeed())
                .timeNanos(timeNanos)
                .memoryBytes(memUsed)
                .solutionValue(optimalValue)
                .optimalValue(optimalValue)
                .nodesExplored(0)
                .optimal(true)
                .build();
    }
}