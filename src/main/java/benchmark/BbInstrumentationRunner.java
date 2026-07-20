package benchmark;

import algorithms.BbInstrumentation;
import algorithms.BranchAndBound;
import dataset.DatasetGenerator;
import dataset.UncorrelatedGenerator;
import dataset.WeaklyCorrelatedGenerator;
import dataset.StronglyCorrelatedGenerator;
import dataset.InverseCorrelatedGenerator;
import dataset.AlmostEqualRatiosGenerator;
import model.KnapsackInstance;

import org.apache.commons.csv.CSVFormat;
import org.apache.commons.csv.CSVPrinter;

import java.io.FileWriter;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.List;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.TimeoutException;

/**
 * Generates results/bb_instrumentation.csv by running instrumented
 * Branch & Bound on all instances under both capacity modes.
 *
 * This runner is independent of the benchmark pipeline. It does not
 * modify any benchmark outputs, CSV schemas, tables, or figures.
 *
 * Usage:
 *   java -cp target/knapsack-comparison-2.0.0.jar benchmark.BbInstrumentationRunner
 */
public final class BbInstrumentationRunner {

    private static final int TIMEOUT_SECONDS = 30;

    public static void main(String[] args) {
        int[] ns = {20, 50, 100, 200, 500, 1000};
        int capacity = 1000;
        int instancesPerConfig = 100;
        long seed = 42L;

        System.out.println("=== B&B Instrumentation Runner ===");
        Path outputPath = Paths.get("results", "bb_instrumentation.csv");
        outputPath.getParent().toFile().mkdirs();

        try (FileWriter writer = new FileWriter(outputPath.toFile());
             CSVPrinter printer = new CSVPrinter(writer,
                 CSVFormat.DEFAULT.builder().setHeader(BbInstrumentation.csvHeader()).build())) {

            // Fixed capacity mode
            System.out.println("Generating instances (fixed mode)...");
            DatasetGenerator fixedGen = DatasetGenerator.builder()
                    .addGenerator(new UncorrelatedGenerator(0, capacity, 1000, 1000))
                    .addGenerator(new WeaklyCorrelatedGenerator(0, capacity, 1000, 100))
                    .addGenerator(new StronglyCorrelatedGenerator(0, capacity, 1000))
                    .addGenerator(new InverseCorrelatedGenerator(0, capacity, 1000))
                    .addGenerator(new AlmostEqualRatiosGenerator(0, capacity, 1000, 1.0))
                    .sizes(ns)
                    .instancesPerConfig(instancesPerConfig)
                    .seed(seed)
                    .capacityMode(DatasetGenerator.CapacityMode.FIXED)
                    .build();
            List<KnapsackInstance> fixedInstances = fixedGen.generate();
            System.out.println("  " + fixedInstances.size() + " instances");

            // Scaled capacity mode
            System.out.println("Generating instances (scaled mode)...");
            DatasetGenerator scaledGen = DatasetGenerator.builder()
                    .addGenerator(new UncorrelatedGenerator(0, 0, 1000, 1000))
                    .addGenerator(new WeaklyCorrelatedGenerator(0, 0, 1000, 100))
                    .addGenerator(new StronglyCorrelatedGenerator(0, 0, 1000))
                    .addGenerator(new InverseCorrelatedGenerator(0, 0, 1000))
                    .addGenerator(new AlmostEqualRatiosGenerator(0, 0, 1000, 1.0))
                    .sizes(ns)
                    .instancesPerConfig(instancesPerConfig)
                    .seed(seed)
                    .capacityMode(DatasetGenerator.CapacityMode.SCALED)
                    .build();
            List<KnapsackInstance> scaledInstances = scaledGen.generate();
            System.out.println("  " + scaledInstances.size() + " instances");

            BranchAndBound bb = new BranchAndBound();
            long total = fixedInstances.size() + scaledInstances.size();
            long done = 0;

            java.util.concurrent.ExecutorService executor = java.util.concurrent.Executors.newSingleThreadExecutor();

            // Process fixed mode
            System.out.println("Running instrumented B&B (fixed mode)...");
            for (KnapsackInstance inst : fixedInstances) {
                BbInstrumentation stats = new BbInstrumentation();
                Future<?> future = executor.submit(() -> {
                    bb.solve(inst, stats);
                });
                try {
                    future.get(TIMEOUT_SECONDS, TimeUnit.SECONDS);
                } catch (TimeoutException e) {
                    future.cancel(true);
                    System.err.println("  Timeout: instance " + inst.getId()
                        + " (n=" + inst.getN() + ", family=" + inst.getFamilyName()
                        + ") — stats collected up to interruption");
                } catch (ExecutionException e) {
                    // B&B threw (interrupt, etc.) — stats populated up to failure point
                } catch (Exception e) {
                    // Other unexpected errors
                }
                printer.printRecord((Object[]) stats.toCsvRow("fixed"));
                done++;
                if (done % 500 == 0) {
                    System.out.println("  Progress: " + done + "/" + total);
                }
            }

            // Process scaled mode
            System.out.println("Running instrumented B&B (scaled mode)...");
            for (KnapsackInstance inst : scaledInstances) {
                BbInstrumentation stats = new BbInstrumentation();
                Future<?> future = executor.submit(() -> {
                    bb.solve(inst, stats);
                });
                try {
                    future.get(TIMEOUT_SECONDS, TimeUnit.SECONDS);
                } catch (TimeoutException e) {
                    future.cancel(true);
                    System.err.println("  Timeout: instance " + inst.getId()
                        + " (n=" + inst.getN() + ", family=" + inst.getFamilyName()
                        + ") — stats collected up to interruption");
                } catch (ExecutionException e) {
                    // B&B threw (interrupt, etc.) — stats populated up to failure point
                } catch (Exception e) {
                    // Other unexpected errors
                }
                printer.printRecord((Object[]) stats.toCsvRow("scaled"));
                done++;
                if (done % 500 == 0) {
                    System.out.println("  Progress: " + done + "/" + total);
                }
            }

            executor.shutdownNow();
            try {
                executor.awaitTermination(5, TimeUnit.SECONDS);
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }

            printer.flush();
            System.out.println("Exported " + done + " instrumentation rows to " + outputPath);

        } catch (Exception e) {
            System.err.println("Fatal error: " + e.getMessage());
            e.printStackTrace();
            System.exit(1);
        }

        System.out.println("Done.");
    }
}
