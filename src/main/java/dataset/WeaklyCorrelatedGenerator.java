package dataset;

import model.Item;
import model.KnapsackInstance;

import java.util.Random;

public final class WeaklyCorrelatedGenerator implements InstanceGenerator {
    final int n;
    final int capacity;
    final int maxWeight;
    final int delta;

    public WeaklyCorrelatedGenerator(int n, int capacity, int maxWeight, int delta) {
        this.n = n;
        this.capacity = capacity;
        this.maxWeight = maxWeight;
        this.delta = delta;
    }

    @Override
    public KnapsackInstance generate(int id, Random rng) {
        Item[] items = new Item[n];
        for (int i = 0; i < n; i++) {
            int w = rng.nextInt(maxWeight) + 1;
            int v = w + rng.nextInt(2 * delta + 1) - delta;
            v = Math.max(1, v);
            items[i] = new Item(i, w, v);
        }
        String params = String.format("n=%d,C=%d,maxW=%d,delta=%d", n, capacity, maxWeight, delta);
        return new KnapsackInstance(id, n, capacity, items, getFamilyName(), params);
    }

    @Override
    public String getFamilyName() {
        return "WeaklyCorrelated";
    }

    @Override
    public String getParams() {
        return String.format("n=%d,C=%d,maxW=%d,delta=%d", n, capacity, maxWeight, delta);
    }
}