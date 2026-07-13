package dataset;

import model.Item;
import model.KnapsackInstance;

import java.util.Random;

public final class InverseCorrelatedGenerator implements InstanceGenerator {
    final int n;
    final int capacity;
    final int maxWeight;

    public InverseCorrelatedGenerator(int n, int capacity, int maxWeight) {
        this.n = n;
        this.capacity = capacity;
        this.maxWeight = maxWeight;
    }

    @Override
    public KnapsackInstance generate(int id, Random rng) {
        Item[] items = new Item[n];
        for (int i = 0; i < n; i++) {
            int w = rng.nextInt(maxWeight) + 1;
            int v = maxWeight - w + 1;
            items[i] = new Item(i, w, v);
        }
        String params = String.format("n=%d,C=%d,maxW=%d", n, capacity, maxWeight);
        return new KnapsackInstance(id, n, capacity, items, getFamilyName(), params);
    }

    @Override
    public String getFamilyName() {
        return "InverseCorrelated";
    }

    @Override
    public String getParams() {
        return String.format("n=%d,C=%d,maxW=%d", n, capacity, maxWeight);
    }
}