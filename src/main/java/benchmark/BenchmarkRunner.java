package benchmark;

import algorithms.Algorithm;
import algorithms.AlgorithmFactory;
import dataset.DatasetGenerator;
import model.KnapsackInstance;
import model.Result;

import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;

public final class BenchmarkRunner {
    private final DatasetGenerator datasetGenerator;
    private final AlgorithmFactory[] algorithmFactories;
    private final int perInstanceWarmupRuns;
    private final int timeoutSeconds;

    public BenchmarkRunner(DatasetGenerator datasetGenerator, AlgorithmFactory[] algorithmFactories, int perInstanceWarmupRuns, int timeoutSeconds) {
        this.datasetGenerator = datasetGenerator;
        this.algorithmFactories = algorithmFactories;
        this.perInstanceWarmupRuns = perInstanceWarmupRuns;
        this.timeoutSeconds = timeoutSeconds;
    }

    public List<Result> run() {
        List<KnapsackInstance> instances = datasetGenerator.generate();
        System.out.println("Generated " + instances.size() + " instances");

        // Global JIT warmup: run each algorithm on representative instances
        // to ensure JIT compilation reaches steady state before timed runs
        warmupJit(instances);

        List<Result> allResults = new ArrayList<>();

        for (AlgorithmFactory factory : algorithmFactories) {
            Algorithm algo = factory.create();
            System.out.println("Running " + algo.getName() + "...");

            for (KnapsackInstance instance : instances) {
                for (int w = 0; w < perInstanceWarmupRuns; w++) {
                    warmupWithTimeout(algo, instance, Math.min(timeoutSeconds, 5));
                }

                Result result = runWithTimeout(algo, instance);
                allResults.add(result);
            }
        }

        return allResults;
    }

    private void warmupJit(List<KnapsackInstance> instances) {
        System.out.println("Performing global JIT warmup...");
        
        // Group instances by algorithm-relevant characteristics
        // For warmup, we just need to exercise the hot paths with varying data sizes
        for (AlgorithmFactory factory : algorithmFactories) {
            Algorithm algo = factory.create();
            
            // Warm up with a few instances of each size to trigger JIT compilation
            // Use first instance of each (n, family) combination
            java.util.Set<String> seen = new java.util.HashSet<>();
            int warmupCount = 0;
            
            for (KnapsackInstance instance : instances) {
                String key = instance.getN() + ":" + instance.getFamilyName();
                if (seen.add(key)) {
                    // Run many iterations to ensure JIT reaches C2 compilation
                    // Greedy is very fast, so we need many iterations
                    int iterations = 10000;
                    long startNanos = System.nanoTime();
                    for (int i = 0; i < iterations; i++) {
                        algo.solve(instance);
                    }
                    long elapsedMs = (System.nanoTime() - startNanos) / 1_000_000;
                    warmupCount++;
                    // Only need a few distinct (n, family) combos per algorithm
                    if (warmupCount >= 10) break;
                }
            }
            System.out.println("  Warmed up " + algo.getName() + " (" + warmupCount + " instance types)");
        }
        System.out.println("Global JIT warmup complete");
    }

    private Result runWithTimeout(Algorithm algo, KnapsackInstance instance) {
        return runWithTimeout(algo, instance, timeoutSeconds);
    }

    private Result runWithTimeout(Algorithm algo, KnapsackInstance instance, int timeoutSec) {
        ExecutorService executor = Executors.newSingleThreadExecutor();
        try {
            Future<Result> future = executor.submit(() -> algo.solve(instance));
            return future.get(timeoutSec, java.util.concurrent.TimeUnit.SECONDS);
        } catch (java.util.concurrent.TimeoutException | java.util.concurrent.ExecutionException e) {
            System.err.println("Error/Timeout: " + algo.getName() + " on instance " + instance.getId() + ": " + e.getMessage());
            return Result.builder()
                    .algorithm(algo.getName())
                    .datasetType(instance.getFamilyName())
                    .n(instance.getN())
                    .capacity(instance.getCapacity())
                    .instanceId(instance.getId())
                    .seed(instance.getId())
                    .timeNanos(timeoutSec * 1_000_000_000L)
                    .memoryBytes(0)
                    .solutionValue(0)
                    .nodesExplored(0)
                    .optimal(false)
                    .build();
        } catch (Exception e) {
            System.err.println("Error: " + algo.getName() + " on instance " + instance.getId() + ": " + e.getMessage());
            return Result.builder()
                    .algorithm(algo.getName())
                    .datasetType(instance.getFamilyName())
                    .n(instance.getN())
                    .capacity(instance.getCapacity())
                    .instanceId(instance.getId())
                    .seed(instance.getId())
                    .timeNanos(0)
                    .memoryBytes(0)
                    .solutionValue(0)
                    .nodesExplored(0)
                    .optimal(false)
                    .build();
        } finally {
            executor.shutdownNow();
            try {
                if (!executor.awaitTermination(5, java.util.concurrent.TimeUnit.SECONDS)) {
                    System.err.println("WARNING: Worker thread did not terminate within 5s after interrupt for "
                            + algo.getName() + " on instance " + instance.getId());
                }
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
        }
    }

    private void warmupWithTimeout(Algorithm algo, KnapsackInstance instance, int timeoutSec) {
        ExecutorService executor = Executors.newSingleThreadExecutor();
        try {
            Future<?> future = executor.submit(() -> algo.solve(instance));
            future.get(timeoutSec, java.util.concurrent.TimeUnit.SECONDS);
        } catch (java.util.concurrent.TimeoutException | java.util.concurrent.ExecutionException e) {
            // Warmup timed out or errored — acceptable, just skip
        } catch (Exception e) {
            // Ignore warmup errors
        } finally {
            executor.shutdownNow();
            try {
                executor.awaitTermination(2, java.util.concurrent.TimeUnit.SECONDS);
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
        }
    }

    public static Builder builder() {
        return new Builder();
    }

    public static final class Builder {
        private DatasetGenerator datasetGenerator;
        private AlgorithmFactory[] algorithmFactories;
        private int warmupRuns = 3;
        private int timeoutSeconds = 30;

        public Builder datasetGenerator(DatasetGenerator dg) {
            datasetGenerator = dg;
            return this;
        }

        public Builder algorithms(AlgorithmFactory... factories) {
            algorithmFactories = factories;
            return this;
        }

        public Builder warmupRuns(int n) {
            warmupRuns = n;
            return this;
        }

        public Builder timeoutSeconds(int s) {
            timeoutSeconds = s;
            return this;
        }

        public BenchmarkRunner build() {
            return new BenchmarkRunner(datasetGenerator, algorithmFactories, warmupRuns, timeoutSeconds);
        }
    }
}