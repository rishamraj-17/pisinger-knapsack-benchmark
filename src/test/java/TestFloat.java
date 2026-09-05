import java.util.*;

public class TestFloat {
    static class Item {
        int weight, value;
        double ratio;
        public Item(int v, int w) { this.value = v; this.weight = w; this.ratio = (double)v/w; }
        public int getWeight() { return weight; }
        public int getValue() { return value; }
        public double getRatio() { return ratio; }
    }
    
    public static void main(String[] args) {
        Random rand = new Random(42);
        for (int test = 0; test < 1000; test++) {
            int n = 100;
            Item[] items = new Item[n];
            for (int i = 0; i < n; i++) {
                items[i] = new Item(rand.nextInt(1000) + 1, rand.nextInt(1000) + 1);
            }
            Arrays.sort(items, Comparator.comparingDouble(Item::getRatio).reversed());
            
            int[] pw = new int[n + 1];
            int[] pv = new int[n + 1];
            for (int i = 0; i < n; i++) {
                pw[i + 1] = pw[i] + items[i].getWeight();
                pv[i + 1] = pv[i] + items[i].getValue();
            }
            
            int capacity = 5000;
            for (int level = 0; level < n; level++) {
                for (int w = 0; w <= capacity; w += 50) {
                    for (int v = 0; v <= 10000; v += 100) {
                        double b1 = boundOld(level, v, w, items, capacity, n);
                        double b2 = boundNew(level, v, w, items, capacity, n, pw, pv);
                        if (Double.doubleToLongBits(b1) != Double.doubleToLongBits(b2)) {
                            System.out.println("Mismatch: " + b1 + " != " + b2);
                            System.exit(1);
                        }
                    }
                }
            }
        }
        System.out.println("No mismatches found!");
    }
    
    private static double boundOld(int level, int value, int weight, Item[] items, int capacity, int n) {
        if (weight >= capacity) return value;
        double bound = value;
        int w = weight;
        for (int i = level; i < n; i++) {
            if (w + items[i].getWeight() <= capacity) {
                w += items[i].getWeight();
                bound += items[i].getValue();
            } else {
                bound += (capacity - w) * items[i].getRatio();
                break;
            }
        }
        return bound;
    }
    
    private static double boundNew(int level, int value, int weight, Item[] items, int capacity, int n, int[] prefixWeight, int[] prefixValue) {
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
