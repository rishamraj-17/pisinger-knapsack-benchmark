package dataset;

import model.Item;
import model.KnapsackInstance;

import java.util.Random;

public final class UncorrelatedGenerator implements InstanceGenerator {
    final int n;
    final int capacity;
    final int maxWeight;
    final int maxValue;

    public UncorrelatedGenerator(int n, int capacity, int maxWeight, int maxValue) {
        this.n = n;
        this.capacity = capacity;
        this.maxWeight = maxWeight;
        this.maxValue = maxValue;
    }

    @Override
    public KnapsackInstance generate(int id, Random rng) {
        Item[] items = new Item[n];
        for (int i = 0; i < n; i++) {
            int w = rng.nextInt(maxWeight) + 1;
            int v = rng.nextInt(maxValue) + 1;
            items[i] = new Item(i, w, v);
        }
        String params = String.format("n=%d,C=%d,maxW=%d,maxV=%d", n, capacity, maxWeight, maxValue);
        return new KnapsackInstance(id, n, capacity, items, getFamilyName(), params);
    }

    @Override
    public String getFamilyName() {
        return "Uncorrelated";
    }

    @Override
    public String getParams() {
        return String.format("n=%d,C=%d,maxW=%d,maxV=%d", n, capacity, maxWeight, maxValue);
    }
}