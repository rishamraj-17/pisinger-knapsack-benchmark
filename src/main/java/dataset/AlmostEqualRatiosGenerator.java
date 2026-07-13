package dataset;

import model.Item;
import model.KnapsackInstance;

import java.util.Random;

public final class AlmostEqualRatiosGenerator implements InstanceGenerator {
    final int n;
    final int capacity;
    final int maxWeight;
    final double baseRatio;

    public AlmostEqualRatiosGenerator(int n, int capacity, int maxWeight, double baseRatio) {
        this.n = n;
        this.capacity = capacity;
        this.maxWeight = maxWeight;
        this.baseRatio = baseRatio;
    }

    @Override
    public KnapsackInstance generate(int id, Random rng) {
        Item[] items = new Item[n];
        for (int i = 0; i < n; i++) {
            int w = rng.nextInt(maxWeight) + 1;
            double noise = rng.nextDouble() * 0.2 - 0.1;
            int v = (int) Math.round(w * baseRatio * (1 + noise));
            v = Math.max(1, v);
            items[i] = new Item(i, w, v);
        }
        String params = String.format("n=%d,C=%d,maxW=%d,baseRatio=%.2f", n, capacity, maxWeight, baseRatio);
        return new KnapsackInstance(id, n, capacity, items, getFamilyName(), params);
    }

    @Override
    public String getFamilyName() {
        return "AlmostEqualRatios";
    }

    @Override
    public String getParams() {
        return String.format("n=%d,C=%d,maxW=%d,baseRatio=%.2f", n, capacity, maxWeight, baseRatio);
    }
}