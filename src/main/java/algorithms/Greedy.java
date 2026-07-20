package algorithms;

import model.Item;
import model.KnapsackInstance;
import model.Result;

import java.util.Arrays;
import java.util.Comparator;

public final class Greedy implements Algorithm {
    @Override
    public String getName() {
        return "Greedy";
    }

    @Override
    public Result solve(KnapsackInstance instance) {
        return solve(instance, null);
    }

    public Result solve(KnapsackInstance instance, GreedyInstrumentation stats) {
        long startMem = Runtime.getRuntime().totalMemory() - Runtime.getRuntime().freeMemory();
        long startTime = System.nanoTime();

        Item[] items = instance.getItems();
        int capacity = instance.getCapacity();

        Item[] sorted = items.clone();
        Arrays.sort(sorted, Comparator.comparingDouble(Item::getRatio).reversed());

        if (stats != null) {
            stats.setInstanceId(instance.getId());
            stats.setN(instance.getN());
            stats.setFamily(instance.getFamilyName());
            stats.setCapacity(capacity);
            stats.setSeed(instance.getBaseSeed());
        }

        int totalValue = 0;
        int totalWeight = 0;
        for (int i = 0; i < sorted.length; i++) {
            Item item = sorted[i];
            if (Thread.currentThread().isInterrupted()) {
                throw new RuntimeException("Greedy interrupted");
            }
            if (totalWeight + item.getWeight() <= capacity) {
                totalWeight += item.getWeight();
                totalValue += item.getValue();
                if (stats != null) stats.recordSelection(i);
            } else {
                if (stats != null) stats.recordSkip(i);
            }
        }

        if (stats != null) stats.finalize(totalWeight);

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
                .solutionValue(totalValue)
                .nodesExplored(0)
                .optimal(false)
                .build();
    }
}
