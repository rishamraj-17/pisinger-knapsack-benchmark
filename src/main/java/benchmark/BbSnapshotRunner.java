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
import model.Result;

import org.apache.commons.csv.CSVFormat;
import org.apache.commons.csv.CSVPrinter;

import java.io.FileWriter;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.TimeoutException;

public final class BbSnapshotRunner {

    private static final int TIMEOUT_SECONDS = 30;

    public static void main(String[] args) {
        int[] ns = {20, 50, 100, 200, 500, 1000};
        int capacity = 1000;
        int instancesPerConfig = 100;
        long seed = 42L;

        System.out.println("=== B&B Snapshot Runner ===");
        Path outputPath = Paths.get("data", "instrumentation", "bb_snapshots.csv");
        outputPath.getParent().toFile().mkdirs();

        List<String> headerList = new ArrayList<>();
        headerList.add("snapshot_fraction");
        for (String h : BbInstrumentation.csvHeader()) {
            headerList.add(h);
        }

        try (FileWriter writer = new FileWriter(outputPath.toFile());
             CSVPrinter printer = new CSVPrinter(writer,
                 CSVFormat.DEFAULT.builder().setHeader(headerList.toArray(new String[0])).build())) {

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

            ExecutorService executor = Executors.newSingleThreadExecutor();

            double[] fractions = {0.01, 0.05, 0.10, 0.25, 0.50, 1.00};

            // Process fixed mode
            System.out.println("Running instrumented B&B snapshots (fixed mode)...");
            for (KnapsackInstance inst : fixedInstances) {
                processInstance(inst, bb, executor, printer, fractions, "fixed");
                done++;
                if (done % 10 == 0) {
                    System.out.println("  Progress: " + done + "/" + total);
                }
            }

            // Process scaled mode
            System.out.println("Running instrumented B&B snapshots (scaled mode)...");
            for (KnapsackInstance inst : scaledInstances) {
                processInstance(inst, bb, executor, printer, fractions, "scaled");
                done++;
                if (done % 10 == 0) {
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
            System.out.println("Exported instrumentation rows to " + outputPath);

        } catch (Exception e) {
            System.err.println("Fatal error: " + e.getMessage());
            e.printStackTrace();
            System.exit(1);
        }

        System.out.println("Done.");
    }

    private static void processInstance(KnapsackInstance inst, BranchAndBound bb, ExecutorService executor, CSVPrinter printer, double[] fractions, String capacityMode) {
        // Run without instrumentation to find total nodes
        Future<Result> future1 = executor.submit(() -> bb.solve(inst));
        Result result = null;
        try {
            result = future1.get(TIMEOUT_SECONDS, TimeUnit.SECONDS);
        } catch (TimeoutException e) {
            future1.cancel(true);
            System.err.println("  Timeout first run: instance " + inst.getId());
            return;
        } catch (Exception e) {
            return; // Failed
        }

        long totalNodes = result.getNodesExplored();
        if (totalNodes == 0) {
            return; 
        }

        long[] targets = new long[fractions.length];
        for (int i = 0; i < fractions.length; i++) {
            targets[i] = (long) Math.ceil(fractions[i] * totalNodes);
        }

        BbInstrumentation stats = new BbInstrumentation(targets);
        Future<?> future2 = executor.submit(() -> bb.solve(inst, stats));
        try {
            future2.get(TIMEOUT_SECONDS, TimeUnit.SECONDS);
        } catch (TimeoutException e) {
            future2.cancel(true);
            System.err.println("  Timeout second run: instance " + inst.getId());
        } catch (Exception e) {
            // ignore
        }

        List<BbInstrumentation> snapshots = stats.getSnapshots();
        try {
            for (int i = 0; i < snapshots.size(); i++) {
                BbInstrumentation snap = snapshots.get(i);
                Object[] snapRow = snap.toCsvRow(capacityMode);
                Object[] row = new Object[snapRow.length + 1];
                row[0] = String.format("%.2f", fractions[i]);
                System.arraycopy(snapRow, 0, row, 1, snapRow.length);
                printer.printRecord(row);
            }
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}
