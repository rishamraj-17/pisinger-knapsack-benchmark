import dataset.*;
import model.*;
import algorithms.*;
import java.util.*;

public class TestPQ {
    public static void main(String[] args) {
        InstanceFactory factory = new InstanceFactory(1468);
        Instance instance = factory.generateAlmostEqualRatios(100);
        int capacity = instance.getCapacityFixed();
        
        System.out.println("Items: " + instance.getItems().length);
        System.out.println("Capacity: " + capacity);
        
        Item[] sorted = instance.getItems().clone();
        Arrays.sort(sorted, Comparator.comparingDouble(Item::getRatio).reversed());
        
        int n = sorted.length;
        int[] pw = new int[n + 1];
        int[] pv = new int[n + 1];
        for (int i = 0; i < n; i++) {
            pw[i + 1] = pw[i] + sorted[i].getWeight();
            pv[i + 1] = pv[i] + sorted[i].getValue();
        }
        
        // Randomly generate some nodes and compare bounds
        int mismatches = 0;
        for (int level = 0; level < n; level++) {
            for (int w = 0; w <= capacity; w += 10) {
                for (int v = 0; v <= 10000; v += 100) {
                    double b1 = boundOld(level, v, w, sorted, capacity, n);
                    double b2 = boundNew(level, v, w, sorted, capacity, n, pw, pv);
                    if (Double.doubleToLongBits(b1) != Double.doubleToLongBits(b2)) {
                        mismatches++;
                        System.out.println("Mismatch: " + b1 + " != " + b2);
                    }
                }
            }
        }
        System.out.println("Mismatches: " + mismatches);
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
