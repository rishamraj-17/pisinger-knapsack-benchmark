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
    private final int warmupRuns;
    private final int timeoutSeconds;

    public BenchmarkRunner(DatasetGenerator datasetGenerator, AlgorithmFactory[] algorithmFactories, int warmupRuns, int timeoutSeconds) {
        this.datasetGenerator = datasetGenerator;
        this.algorithmFactories = algorithmFactories;
        this.warmupRuns = warmupRuns;
        this.timeoutSeconds = timeoutSeconds;
    }

    public List<Result> run() {
        List<KnapsackInstance> instances = datasetGenerator.generate();
        System.out.println("Generated " + instances.size() + " instances");

        List<Result> allResults = new ArrayList<>();

        for (AlgorithmFactory factory : algorithmFactories) {
            Algorithm algo = factory.create();
            System.out.println("Running " + algo.getName() + "...");

            for (KnapsackInstance instance : instances) {
                for (int w = 0; w < warmupRuns; w++) {
                    algo.solve(instance);
                }

                Result result = runWithTimeout(algo, instance);
                allResults.add(result);
            }
        }

        return allResults;
    }

    private Result runWithTimeout(Algorithm algo, KnapsackInstance instance) {
        ExecutorService executor = Executors.newSingleThreadExecutor();
        try {
            Future<Result> future = executor.submit(() -> algo.solve(instance));
            return future.get(timeoutSeconds, java.util.concurrent.TimeUnit.SECONDS);
        } catch (java.util.concurrent.TimeoutException e) {
            System.err.println("Timeout: " + algo.getName() + " on instance " + instance.getId());
            return Result.builder()
                    .algorithm(algo.getName())
                    .datasetType(instance.getFamilyName())
                    .n(instance.getN())
                    .capacity(instance.getCapacity())
                    .instanceId(instance.getId())
                    .seed(instance.getId())
                    .timeNanos(timeoutSeconds * 1_000_000_000L)
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