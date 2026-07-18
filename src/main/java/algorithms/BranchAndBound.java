package algorithms;

import model.Item;
import model.KnapsackInstance;
import model.Result;

import java.util.Comparator;
import java.util.PriorityQueue;

public final class BranchAndBound implements Algorithm {
    private static final long MAX_NODES = 50_000_000L;

    // MAX_NODES acts as a safety cap for untimed contexts (JIT warmup, per-instance warmup).
    // 50M nodes is generous enough to find optimal solutions for n≤500 instances with
    // fractional-bound pruning while preventing runaway computation in untimed warmup loops.
    // For timed runs, the 30-second thread timeout is the primary mechanism; MAX_NODES
    // rarely triggers because the interrupt flag (checked below) terminates first.

    private static class Node implements Comparable<Node> {
        final int level;
        final int value;
        final int weight;
        final double bound;

        Node(int level, int value, int weight, double bound) {
            this.level = level;
            this.value = value;
            this.weight = weight;
            this.bound = bound;
        }

        @Override
        public int compareTo(Node other) {
            return Double.compare(other.bound, this.bound);
        }
    }

    @Override
    public String getName() {
        return "BranchAndBound";
    }

    @Override
    public Result solve(KnapsackInstance instance) {
        long startMem = Runtime.getRuntime().totalMemory() - Runtime.getRuntime().freeMemory();
        long startTime = System.nanoTime();

        Item[] items = instance.getItems();
        int n = instance.getN();
        int capacity = instance.getCapacity();

        Item[] sorted = items.clone();
        java.util.Arrays.sort(sorted, Comparator.comparingDouble(Item::getRatio).reversed());

        int[] prefixWeight = new int[n + 1];
        int[] prefixValue = new int[n + 1];
        for (int i = 0; i < n; i++) {
            prefixWeight[i + 1] = prefixWeight[i] + sorted[i].getWeight();
            prefixValue[i + 1] = prefixValue[i] + sorted[i].getValue();
        }

        PriorityQueue<Node> pq = new PriorityQueue<>();
        double rootBound = fractionalBound(0, 0, 0, sorted, capacity, n, prefixWeight, prefixValue);
        pq.add(new Node(0, 0, 0, rootBound));

        int bestValue = 0;
        long nodesExplored = 0;
        long nodesPruned = 0;
        int maxQueueSize = 1;
        boolean searchCompleted = true;

        while (!pq.isEmpty()) {
            if (Thread.currentThread().isInterrupted()) {
                throw new RuntimeException("BranchAndBound interrupted at node " + nodesExplored);
            }
            if (nodesExplored >= MAX_NODES) {
                searchCompleted = false;
                break;
            }

            Node node = pq.poll();
            nodesExplored++;

            if (Math.floor(node.bound) <= bestValue) {
                nodesPruned++;
                continue;
            }
            if (node.level >= n) continue;

            int nextLevel = node.level + 1;
            Item nextItem = sorted[node.level];

            int includeWeight = node.weight + nextItem.getWeight();
            int includeValue = node.value + nextItem.getValue();
            if (includeWeight <= capacity && includeValue > bestValue) {
                bestValue = includeValue;
            }
            if (includeWeight <= capacity) {
                double bound = fractionalBound(nextLevel, includeValue, includeWeight, sorted, capacity, n, prefixWeight, prefixValue);
                if (Math.floor(bound) > bestValue && nodesExplored < MAX_NODES) {
                    pq.add(new Node(nextLevel, includeValue, includeWeight, bound));
                }
            }

            double excludeBound = fractionalBound(nextLevel, node.value, node.weight, sorted, capacity, n, prefixWeight, prefixValue);
            if (Math.floor(excludeBound) > bestValue && nodesExplored < MAX_NODES) {
                pq.add(new Node(nextLevel, node.value, node.weight, excludeBound));
            }

            if (pq.size() > maxQueueSize) {
                maxQueueSize = pq.size();
            }
        }

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
                .solutionValue(bestValue)
                .optimalValue(bestValue)
                .nodesExplored(nodesExplored)
                .nodesPruned(nodesPruned)
                .maxQueueSize(maxQueueSize)
                .optimal(searchCompleted)
                .build();
    }

    private static double fractionalBound(int level, int value, int weight, Item[] items, int capacity, int n,
                                           int[] prefixWeight, int[] prefixValue) {
        if (weight >= capacity) return value;
        int remaining = capacity - weight;
        int lo = level;
        int hi = n - 1;
        int split = -1;
        while (lo <= hi) {
            int mid = (lo + hi) >>> 1;
            long cum = prefixWeight[mid + 1] - prefixWeight[level];
            if (cum <= remaining) {
                lo = mid + 1;
            } else {
                split = mid;
                hi = mid - 1;
            }
        }
        double bound = value;
        if (split == -1) {
            bound += prefixValue[n] - prefixValue[level];
        } else {
            bound += prefixValue[split] - prefixValue[level];
            remaining -= prefixWeight[split] - prefixWeight[level];
            if (remaining > 0) {
                bound += remaining * items[split].getRatio();
            }
        }
        return bound;
    }
}