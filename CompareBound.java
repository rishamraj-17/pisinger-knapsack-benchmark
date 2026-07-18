import java.util.*;
import java.nio.file.*;
import java.io.*;

public class CompareBound {
    static class Item {
        int weight, value;
        double ratio;
        public Item(int v, int w) { this.value = v; this.weight = w; this.ratio = (double)v/w; }
    }
    
    public static void main(String[] args) throws Exception {
        // Read instance AlmostEqualRatios 100 fixed 1468
        // Actually, let's just generate it the exact same way the benchmark does.
        // Wait, BenchmarkRunner reads or generates?
        // Let's check how BenchmarkRunner generates it.
    }
}
