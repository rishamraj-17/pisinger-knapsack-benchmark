import algorithms.AlgorithmFactory;
import benchmark.BenchmarkRunner;
import benchmark.ResultsExporter;
import dataset.DatasetGenerator;
import dataset.UncorrelatedGenerator;
import dataset.WeaklyCorrelatedGenerator;
import dataset.StronglyCorrelatedGenerator;
import dataset.InverseCorrelatedGenerator;
import dataset.AlmostEqualRatiosGenerator;
import model.Result;

import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.List;

/**
 * Canonical experiment entry point for Knapsack empirical comparison.
 * 
 * Usage:
 *   java -jar knapsack.jar [n-values] [capacity] [instances-per-config] [seed]
 *   Example: java -jar knapsack.jar 20,50,100,200,500 1000 30 42
 * 
 * Defaults: n={20,50,100,200,500}, capacity=1000, instances=30, seed=42
 * 
 * Output: out/results/full_experiment.csv (canonical CSV with 2250 rows x 3 algorithms = 6750 rows)
 * 
 * Pipeline:
 *   1. Run this class -> generates out/results/full_experiment.csv
 *   2. Run python3 analyze.py out/results/full_experiment.csv -> generates tables/ and figures/
 *   3. Use tables/*.tex in paper
 */
public final class Main {
    public static void main(String[] args) {
        int[] ns = args.length > 0 ? parseIntArray(args[0]) : new int[]{20, 50, 100, 200, 500};
        int capacity = args.length > 1 ? Integer.parseInt(args[1]) : 1000;
        int instancesPerConfig = args.length > 2 ? Integer.parseInt(args[2]) : 30;
        long seed = args.length > 3 ? Long.parseLong(args[3]) : 42L;

        System.out.println("=== Knapsack Empirical Comparison ===");
        System.out.println("ns: " + java.util.Arrays.toString(ns));
        System.out.println("capacity: " + capacity + ", instances/config: " + instancesPerConfig + ", seed: " + seed);
        System.out.println("Total instances: " + (ns.length * 5 * instancesPerConfig));
        System.out.println("Total runs: " + (ns.length * 5 * instancesPerConfig * 3));

        DatasetGenerator generator = DatasetGenerator.builder()
                .addGenerator(new UncorrelatedGenerator(0, capacity, 1000, 1000))
                .addGenerator(new WeaklyCorrelatedGenerator(0, capacity, 1000, 100))
                .addGenerator(new StronglyCorrelatedGenerator(0, capacity, 1000))
                .addGenerator(new InverseCorrelatedGenerator(0, capacity, 1000))
                .addGenerator(new AlmostEqualRatiosGenerator(0, capacity, 1000, 1.0))
                .sizes(ns)
                .instancesPerConfig(instancesPerConfig)
                .seed(seed)
                .build();

        AlgorithmFactory[] algorithms = {
                AlgorithmFactory.GREEDY,
                AlgorithmFactory.DYNAMIC_PROGRAMMING,
                AlgorithmFactory.BRANCH_AND_BOUND
        };

        BenchmarkRunner runner = new BenchmarkRunner(generator, algorithms, 3, 30);
        List<Result> results = runner.run();

        Path outputDir = Paths.get("results");
        outputDir.toFile().mkdirs();
        Path output = outputDir.resolve("full_experiment.csv");

        try {
            ResultsExporter.export(results, output);
        } catch (Exception e) {
            System.err.println("Export failed: " + e.getMessage());
            e.printStackTrace();
            System.exit(1);
        }

        System.out.println("Done! Results: " + results.size() + " rows");
        System.out.println("Output: " + output.toAbsolutePath());
    }

    private static int[] parseIntArray(String s) {
        String[] parts = s.split(",");
        int[] arr = new int[parts.length];
        for (int i = 0; i < parts.length; i++) {
            arr[i] = Integer.parseInt(parts[i].trim());
        }
        return arr;
    }
}