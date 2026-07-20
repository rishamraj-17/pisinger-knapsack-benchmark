import java.util.Random;
public class TestRandom {
    public static void main(String[] args) {
        // Simulate the first instance: n=20, Uncorrelated, seed=42
        // DatasetGenerator does: Random rng = new Random(42 + 20) for n=20
        long seed = 42L;
        int n = 20;
        Random rng = new Random(seed + n);
        // Generate first 10 items like UncorrelatedGenerator
        System.out.println("=== First 10 Uncorrelated items (n=20, seed=42) ===");
        for (int i = 0; i < 10; i++) {
            int w = rng.nextInt(1000) + 1;
            int v = rng.nextInt(1000) + 1;
            System.out.println("Item " + i + ": w=" + w + ", v=" + v);
        }
        // Now verify the random sequence
        rng = new Random(42 + 20);
        System.out.println("=== First 10 nextInt(1000) values ===");
        for (int i = 0; i < 10; i++) {
            System.out.println("nextInt(1000)[" + i + "] = " + rng.nextInt(1000));
        }
        // Test nextDouble
        rng = new Random(42 + 20);
        System.out.println("=== First 5 nextDouble() values ===");
        for (int i = 0; i < 5; i++) {
            System.out.println("nextDouble()[" + i + "] = " + rng.nextDouble());
        }
    }
}
