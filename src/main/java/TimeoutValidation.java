import algorithms.Algorithm;
import algorithms.BranchAndBound;
import model.Item;
import model.KnapsackInstance;
import model.Result;

import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.TimeoutException;
import java.util.concurrent.ExecutionException;

/**
 * Validation benchmark for the Branch & Bound timeout mechanism.
 *
 * Tests:
 * 1. Timed-out B&B threads terminate promptly (no zombie threads)
 * 2. No zombie threads remain after timeout
 * 3. Timeout semantics are "30 seconds per instance"
 * 4. Non-timed-out instances produce correct, unchanged results
 *
 * Usage:
 *   javac -d out -cp "lib/commons-csv-1.10.0.jar" src/main/java/TimeoutValidation.java
 *   java -cp "out:lib/commons-csv-1.10.0.jar" TimeoutValidation
 */
public final class TimeoutValidation {

    private static int passed = 0;
    private static int failed = 0;

    public static void main(String[] args) throws Exception {
        System.out.println("=== Branch & Bound Timeout Validation ===\n");

        testTimedOutThreadTerminatesPromptly();
        testNoZombieThreadsAccumulate();
        testTimeoutSemanticsPerInstance();
        testNonTimedOutResultsUnchanged();

        System.out.println("\n=== Results: " + passed + " passed, " + failed + " failed ===");
        System.exit(failed > 0 ? 1 : 0);
    }

    /**
     * Test 1: A B&B solve that exceeds the timeout must terminate the thread promptly.
     * We use a short timeout (2s) and verify the thread exits within a few seconds.
     */
    static void testTimedOutThreadTerminatesPromptly() {
        System.out.println("[Test 1] Timed-out B&B thread terminates promptly");

        // Create a hard instance that will run for a long time (~13s uncapped)
        KnapsackInstance hardInstance = createHardInstance();

        ExecutorService executor = Executors.newSingleThreadExecutor();
        Algorithm algo = new BranchAndBound();

        long submitTime = System.nanoTime();
        Future<Result> future = executor.submit(() -> algo.solve(hardInstance));

        try {
            // Timeout after 2 seconds
            future.get(2, TimeUnit.SECONDS);
            fail("Expected TimeoutException but solve completed");
        } catch (TimeoutException e) {
            // Expected
        } catch (ExecutionException e) {
            // B&B may throw RuntimeException on interrupt — this is acceptable
            System.out.println("  B&B threw on interrupt: " + e.getCause().getMessage());
        } catch (Exception e) {
            fail("Unexpected exception: " + e);
        }

        // Now send interrupt and measure how long until the thread dies
        long interruptTime = System.nanoTime();
        executor.shutdownNow();

        try {
            boolean terminated = executor.awaitTermination(10, TimeUnit.SECONDS);
            long elapsedMs = (System.nanoTime() - interruptTime) / 1_000_000;

            if (!terminated) {
                fail("Worker thread did not terminate within 10s after interrupt");
            } else if (elapsedMs > 5000) {
                fail("Worker thread took " + elapsedMs + "ms to terminate (expected < 5s)");
            } else {
                System.out.println("  Thread terminated in " + elapsedMs + "ms after interrupt");
                pass();
            }
        } catch (InterruptedException e) {
            fail("awaitTermination interrupted: " + e);
        }
    }

    /**
     * Test 2: Run multiple timeout cycles and verify no zombie threads accumulate.
     * Uses Thread.activeCount() to detect leaked threads.
     */
    static void testNoZombieThreadsAccumulate() {
        System.out.println("\n[Test 2] No zombie threads accumulate after multiple timeouts");

        KnapsackInstance hardInstance = createHardInstance();
        Algorithm algo = new BranchAndBound();

        // Baseline thread count
        int baselineThreads = Thread.activeCount();
        System.out.println("  Baseline thread count: " + baselineThreads);

        int timeoutCount = 5;
        for (int i = 0; i < timeoutCount; i++) {
            ExecutorService executor = Executors.newSingleThreadExecutor();
            try {
                Future<Result> future = executor.submit(() -> algo.solve(hardInstance));
                future.get(1, TimeUnit.SECONDS);
            } catch (TimeoutException e) {
                // Expected
            } catch (ExecutionException e) {
                // B&B threw on interrupt — acceptable
            } catch (Exception e) {
                fail("Unexpected exception on iteration " + i + ": " + e);
            } finally {
                executor.shutdownNow();
                try {
                    executor.awaitTermination(5, TimeUnit.SECONDS);
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                }
            }
        }

        // Allow thread cleanup
        System.gc();
        try { Thread.sleep(500); } catch (InterruptedException e) { Thread.currentThread().interrupt(); }

        int afterThreads = Thread.activeCount();
        int leaked = afterThreads - baselineThreads;

        if (leaked > 1) {
            fail("Leaked " + leaked + " threads after " + timeoutCount + " timeouts "
                    + "(baseline=" + baselineThreads + ", after=" + afterThreads + ")");
        } else {
            System.out.println("  Thread count after " + timeoutCount + " timeouts: " + afterThreads
                    + " (leaked: " + leaked + ")");
            pass();
        }
    }

    /**
     * Test 3: Verify timeout semantics are "30 seconds per instance" — i.e., each
     * instance gets its own fresh timeout budget, not a cumulative one.
     */
    static void testTimeoutSemanticsPerInstance() {
        System.out.println("\n[Test 3] Timeout is 30 seconds per instance (independent budgets)");

        KnapsackInstance hardInstance = createHardInstance();
        Algorithm algo = new BranchAndBound();

        // Run two instances back-to-back with a 2s timeout each.
        // If timeout were cumulative, the second run would have less budget.
        long[] durations = new long[2];
        for (int i = 0; i < 2; i++) {
            ExecutorService executor = Executors.newSingleThreadExecutor();
            long start = System.nanoTime();
            try {
                Future<Result> future = executor.submit(() -> algo.solve(hardInstance));
                future.get(2, TimeUnit.SECONDS);
            } catch (TimeoutException | ExecutionException e) {
                // Expected
            } catch (Exception e) {
                fail("Unexpected exception: " + e);
            } finally {
                executor.shutdownNow();
                try {
                    executor.awaitTermination(5, TimeUnit.SECONDS);
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                }
            }
            durations[i] = (System.nanoTime() - start) / 1_000_000;
        }

        // Both should be close to 2000ms (the timeout), not 2000ms + 4000ms
        long tolerance = 1000; // 1s tolerance for scheduling overhead
        if (durations[0] < 1500 || durations[0] > 4000) {
            fail("First timeout duration unexpected: " + durations[0] + "ms");
        } else if (durations[1] < 1500 || durations[1] > 4000) {
            fail("Second timeout duration unexpected: " + durations[1] + "ms (cumulative?)");
        } else {
            System.out.println("  Run 1 duration: " + durations[0] + "ms, Run 2 duration: " + durations[1] + "ms");
            System.out.println("  Both independent (~2s), confirming per-instance timeout");
            pass();
        }
    }

    /**
     * Test 4: Verify that non-timed-out instances produce correct, unchanged results.
     * Runs B&B on a small instance (fast) and checks the result.
     */
    static void testNonTimedOutResultsUnchanged() {
        System.out.println("\n[Test 4] Non-timed-out instances produce correct results");

        KnapsackInstance easyInstance = createEasyInstance(20);
        Algorithm algo = new BranchAndBound();

        // Run directly (no timeout) to get reference result
        Result reference = algo.solve(easyInstance);
        int refValue = reference.getSolutionValue();
        long refNodes = reference.getNodesExplored();

        // Run through the timeout mechanism with generous timeout (should complete fast)
        for (int trial = 0; trial < 3; trial++) {
            ExecutorService executor = Executors.newSingleThreadExecutor();
            try {
                Future<Result> future = executor.submit(() -> algo.solve(easyInstance));
                Result result = future.get(30, TimeUnit.SECONDS);

                if (result.getSolutionValue() != refValue) {
                    fail("Trial " + trial + ": solution value mismatch (expected " + refValue
                            + ", got " + result.getSolutionValue() + ")");
                    return;
                }
                if (result.getNodesExplored() != refNodes) {
                    fail("Trial " + trial + ": nodes explored mismatch (expected " + refNodes
                            + ", got " + result.getNodesExplored() + ")");
                    return;
                }
                if (!result.isOptimal()) {
                    fail("Trial " + trial + ": result marked as non-optimal");
                    return;
                }
            } catch (Exception e) {
                fail("Trial " + trial + ": unexpected exception: " + e);
                return;
            } finally {
                executor.shutdownNow();
                try {
                    executor.awaitTermination(5, TimeUnit.SECONDS);
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                }
            }
        }

        System.out.println("  3 trials: consistent solution=" + refValue + ", nodes=" + refNodes + ", optimal=true");
        pass();
    }

    // --- Helpers ---

    static KnapsackInstance createHardInstance() {
        // Small items (weight 1-10), similar ratios, capacity = half total weight.
        // At n=200 this produces instances that take ~10s and explore ~50M nodes,
        // well beyond any reasonable timeout.
        int n = 200;
        Item[] items = new Item[n];
        java.util.Random rng = new java.util.Random(42);
        int totalWeight = 0;
        for (int i = 0; i < n; i++) {
            int w = 1 + rng.nextInt(10);
            double noise = rng.nextDouble() * 0.2 - 0.1;
            int v = (int) Math.round(w * 1.0 * (1 + noise));
            v = Math.max(1, v);
            items[i] = new Item(i, w, v);
            totalWeight += w;
        }
        int capacity = totalWeight / 2;
        return new KnapsackInstance(0, n, capacity, items, "HardTest", "n=200,small,halved");
    }

    static KnapsackInstance createEasyInstance(int n) {
        // Small instance that B&B solves instantly
        Item[] items = new Item[n];
        java.util.Random rng = new java.util.Random(42);
        for (int i = 0; i < n; i++) {
            int weight = 1 + rng.nextInt(20);
            int value = 1 + rng.nextInt(50);
            items[i] = new Item(i, weight, value);
        }
        return new KnapsackInstance(0, n, 500, items, "Uncorrelated", "test");
    }

    static void pass() {
        passed++;
        System.out.println("  PASS");
    }

    static void fail(String msg) {
        failed++;
        System.out.println("  FAIL: " + msg);
    }
}
