package benchmark;

import org.apache.commons.csv.CSVFormat;
import org.apache.commons.csv.CSVParser;
import org.apache.commons.csv.CSVPrinter;
import org.apache.commons.csv.CSVRecord;

import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.io.Reader;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.*;

public final class DatasetIntegrationRunner {

    private static final Path INSTANCES_CSV = Paths.get("results", "instances.csv");
    private static final Path FULL_EXPERIMENT_CSV = Paths.get("out", "results", "full_experiment.csv");
    private static final Path BB_INSTRUMENTATION_CSV = Paths.get("results", "bb_instrumentation.csv");
    private static final Path DP_INSTRUMENTATION_CSV = Paths.get("results", "dp_instrumentation.csv");
    private static final Path GREEDY_INSTRUMENTATION_CSV = Paths.get("results", "greedy_instrumentation.csv");
    private static final Path OUTPUT_CSV = Paths.get("out", "results", "canonical_dataset.csv");

    private static final String KEY_SEPARATOR = "|";

    // Ordered list preserves column order in output
    private static final List<String> IDENTIFIER_COLUMNS = List.of(
        "algorithm", "instance_id", "n", "family", "capacity_mode", "capacity", "seed");

    private static final Set<String> BENCHMARK_CSV_IDENTIFIERS = Set.of(
        "algorithm", "dataset_type", "instance_id", "n", "capacity", "seed", "capacity_mode");

    private static final Set<String> INSTRUMENTATION_CSV_IDENTIFIERS = Set.of(
        "instance_id", "n", "family", "capacity_mode", "capacity", "seed");

    // Columns that exist in both benchmark and BB instrumentation (same data)
    private static final Set<String> BB_BENCHMARK_OVERLAP = Set.of(
        "nodes_explored", "max_queue_size");

    // DP columns that collide with BB columns (DIFFERENT data, must rename)
    private static final Set<String> DP_COLLISION_COLUMNS = Set.of(
        "sum_improvement_amount", "mean_improvement_amount");

    // Column name mapping for DP collision columns
    private static String dpCollisionName(String col) {
        return "dp_" + col;
    }

    public static void main(String[] args) {
        System.out.println("=== Dataset Integration Runner (Phase 2.5) ===");
        System.out.println();

        Map<Path, Boolean> filesExist = checkInputFiles();
        boolean allExist = filesExist.values().stream().allMatch(v -> v);

        if (!allExist) {
            System.out.println("WARNING: Some input files are missing:");
            for (Map.Entry<Path, Boolean> entry : filesExist.entrySet()) {
                System.out.println("  " + (entry.getValue() ? "  OK" : "MISS") + "  " + entry.getKey());
            }
            System.out.println();
            if (!filesExist.get(GREEDY_INSTRUMENTATION_CSV)) {
                System.out.println("Greedy instrumentation CSV not found. Greedy metrics excluded.");
                System.out.println("To generate: run benchmark.GreedyInstrumentationRunner first.");
                System.out.println();
            }
        }

        try {
            System.out.println("Reading input CSVs...");
            CsvData instancesData = readCsv(INSTANCES_CSV);
            CsvData fullExpData = readCsv(FULL_EXPERIMENT_CSV);
            CsvData bbData = readCsv(BB_INSTRUMENTATION_CSV);
            CsvData dpData = readCsv(DP_INSTRUMENTATION_CSV);
            CsvData greedyData = filesExist.get(GREEDY_INSTRUMENTATION_CSV)
                ? readCsv(GREEDY_INSTRUMENTATION_CSV) : null;

            System.out.println("  instances.csv:              " + instancesData.records.size() + " records, "
                + instancesData.headers.length + " columns");
            System.out.println("  full_experiment.csv:        " + fullExpData.records.size() + " records, "
                + fullExpData.headers.length + " columns");
            System.out.println("  bb_instrumentation.csv:     " + bbData.records.size() + " records, "
                + bbData.headers.length + " columns");
            System.out.println("  dp_instrumentation.csv:     " + dpData.records.size() + " records, "
                + dpData.headers.length + " columns");
            if (greedyData != null) {
                System.out.println("  greedy_instrumentation.csv: " + greedyData.records.size() + " records, "
                    + greedyData.headers.length + " columns");
            }
            System.out.println();

            System.out.println("Building lookup maps...");
            Map<String, CSVRecord> instanceMap = buildKeyedMap(instancesData.records, "instance_id", "capacity_mode");
            Map<String, CSVRecord> bbMap = buildKeyedMap(bbData.records, "instance_id", "capacity_mode");
            Map<String, CSVRecord> dpMap = buildKeyedMap(dpData.records, "instance_id", "capacity_mode");
            Map<String, CSVRecord> greedyMap = greedyData != null
                ? buildKeyedMap(greedyData.records, "instance_id", "capacity_mode") : null;

            System.out.println("  instance map: " + instanceMap.size());
            System.out.println("  bb map:       " + bbMap.size());
            System.out.println("  dp map:       " + dpMap.size());
            if (greedyMap != null) System.out.println("  greedy map:   " + greedyMap.size());
            System.out.println();

            System.out.println("Building output schema...");
            List<String> outputHeaders = buildOutputHeaders(
                instancesData.headers, fullExpData.headers,
                bbData.headers, dpData.headers,
                greedyData != null ? greedyData.headers : new String[0]);

            System.out.println("  Total columns: " + outputHeaders.size());
            System.out.println();

            System.out.println("Writing canonical dataset to " + OUTPUT_CSV + "...");
            OUTPUT_CSV.getParent().toFile().mkdirs();

            int missingInstanceCount = 0;
            int writtenCount = 0;

            try (FileWriter writer = new FileWriter(OUTPUT_CSV.toFile());
                 CSVPrinter printer = new CSVPrinter(writer,
                     CSVFormat.DEFAULT.builder().setHeader(outputHeaders.toArray(new String[0])).build())) {

                for (CSVRecord benchRecord : fullExpData.records) {
                    String algorithm = benchRecord.get("algorithm");
                    String instanceId = benchRecord.get("instance_id");
                    String capacityMode = benchRecord.get("capacity_mode");
                    String key = makeKey(instanceId, capacityMode);

                    Map<String, String> row = new LinkedHashMap<>();

                    // 1. Identifiers
                    row.put("algorithm", algorithm);
                    row.put("instance_id", instanceId);
                    row.put("n", benchRecord.get("n"));
                    row.put("family", benchRecord.isSet("dataset_type")
                        ? benchRecord.get("dataset_type") : benchRecord.get("family"));
                    row.put("capacity_mode", capacityMode);
                    row.put("capacity", benchRecord.get("capacity"));
                    row.put("seed", benchRecord.get("seed"));

                    // 2. Instance features
                    CSVRecord instRecord = instanceMap.get(key);
                    if (instRecord != null) {
                        for (String col : instancesData.headers) {
                            if (INSTRUMENTATION_CSV_IDENTIFIERS.contains(col)) continue;
                            if ("capacity".equals(col)) continue;
                            row.put(col, instRecord.get(col));
                        }
                    } else {
                        missingInstanceCount++;
                    }

                    // 3. Benchmark metrics
                    for (String col : fullExpData.headers) {
                        if (BENCHMARK_CSV_IDENTIFIERS.contains(col)) continue;
                        row.put(col, benchRecord.get(col));
                    }

                    // 4. BB instrumentation (skip overlap with benchmark)
                    CSVRecord bbRecord = bbMap != null ? bbMap.get(key) : null;
                    if (bbRecord != null) {
                        for (String col : bbData.headers) {
                            if (INSTRUMENTATION_CSV_IDENTIFIERS.contains(col)) continue;
                            if (BB_BENCHMARK_OVERLAP.contains(col)) continue;
                            row.putIfAbsent(col, bbRecord.get(col));
                        }
                    }

                    // 5. DP instrumentation (rename collisions)
                    CSVRecord dpRecord = dpMap != null ? dpMap.get(key) : null;
                    if (dpRecord != null) {
                        for (String col : dpData.headers) {
                            if (INSTRUMENTATION_CSV_IDENTIFIERS.contains(col)) continue;
                            if ("optimal_value".equals(col)) continue; // already in benchmark
                            String outputCol = DP_COLLISION_COLUMNS.contains(col)
                                ? dpCollisionName(col) : col;
                            row.putIfAbsent(outputCol, dpRecord.get(col));
                        }
                    }

                    // 6. Greedy instrumentation
                    CSVRecord greedyRec = greedyMap != null ? greedyMap.get(key) : null;
                    if (greedyRec != null) {
                        for (String col : greedyData.headers) {
                            if (INSTRUMENTATION_CSV_IDENTIFIERS.contains(col)) continue;
                            row.putIfAbsent(col, greedyRec.get(col));
                        }
                    }

                    // Write row
                    List<String> values = new ArrayList<>();
                    for (String col : outputHeaders) {
                        values.add(row.getOrDefault(col, ""));
                    }
                    printer.printRecord(values);
                    writtenCount++;
                }

                printer.flush();
            }

            System.out.println("  Written: " + writtenCount + " rows");
            if (missingInstanceCount > 0) {
                System.out.println("  WARNING: " + missingInstanceCount + " rows with missing instance data");
            }
            System.out.println("  Output: " + OUTPUT_CSV);

            System.out.println();
            System.out.println("Verifying output...");
            verifyOutput(OUTPUT_CSV, outputHeaders.size(), writtenCount);
            System.out.println();
            System.out.println("Done.");

        } catch (Exception e) {
            System.err.println("Fatal error: " + e.getMessage());
            e.printStackTrace();
            System.exit(1);
        }
    }

    // ---- Data holders ----

    private static class CsvData {
        final String[] headers;
        final List<CSVRecord> records;

        CsvData(String[] headers, List<CSVRecord> records) {
            this.headers = headers;
            this.records = records;
        }
    }

    // ---- CSV I/O ----

    private static Map<Path, Boolean> checkInputFiles() {
        Map<Path, Boolean> result = new LinkedHashMap<>();
        result.put(INSTANCES_CSV, Files.exists(INSTANCES_CSV));
        result.put(FULL_EXPERIMENT_CSV, Files.exists(FULL_EXPERIMENT_CSV));
        result.put(BB_INSTRUMENTATION_CSV, Files.exists(BB_INSTRUMENTATION_CSV));
        result.put(DP_INSTRUMENTATION_CSV, Files.exists(DP_INSTRUMENTATION_CSV));
        result.put(GREEDY_INSTRUMENTATION_CSV, Files.exists(GREEDY_INSTRUMENTATION_CSV));
        return result;
    }

    private static CsvData readCsv(Path path) throws IOException {
        if (!Files.exists(path)) {
            return new CsvData(new String[0], Collections.emptyList());
        }
        try (Reader reader = new FileReader(path.toFile());
             CSVParser parser = CSVFormat.DEFAULT.builder()
                 .setHeader()
                 .setSkipHeaderRecord(true)
                 .setTrim(true)
                 .build()
                 .parse(reader)) {
            String[] headers = parser.getHeaderNames().toArray(new String[0]);
            List<CSVRecord> records = parser.getRecords();
            return new CsvData(headers, records);
        }
    }

    private static String makeKey(String instanceId, String capacityMode) {
        return instanceId + KEY_SEPARATOR + capacityMode;
    }

    private static Map<String, CSVRecord> buildKeyedMap(
            List<CSVRecord> records, String keyCol1, String keyCol2) {
        Map<String, CSVRecord> map = new LinkedHashMap<>(records.size());
        for (CSVRecord record : records) {
            String key = makeKey(record.get(keyCol1), record.get(keyCol2));
            if (map.containsKey(key)) {
                System.err.println("Duplicate key: " + key);
            }
            map.put(key, record);
        }
        return map;
    }

    // ---- Schema construction ----

    private static List<String> buildOutputHeaders(
            String[] instHeader, String[] fullExpHeader,
            String[] bbHeader, String[] dpHeader, String[] greedyHeader) {

        List<String> headers = new ArrayList<>();
        Set<String> used = new HashSet<>();

        // 1. Identifiers (ordered)
        for (String col : IDENTIFIER_COLUMNS) {
            headers.add(col);
            used.add(col);
        }

        // 2. Instance features
        for (String col : instHeader) {
            if (INSTRUMENTATION_CSV_IDENTIFIERS.contains(col)) continue;
            if ("capacity".equals(col)) continue;
            if (used.add(col)) {
                headers.add(col);
            }
        }

        // 3. Benchmark metrics
        for (String col : fullExpHeader) {
            if (BENCHMARK_CSV_IDENTIFIERS.contains(col)) continue;
            if (used.add(col)) {
                headers.add(col);
            }
        }

        // 4. BB instrumentation (skip overlap with benchmark)
        for (String col : bbHeader) {
            if (INSTRUMENTATION_CSV_IDENTIFIERS.contains(col)) continue;
            if (BB_BENCHMARK_OVERLAP.contains(col)) continue;
            if (used.add(col)) {
                headers.add(col);
            }
        }

        // 5. DP instrumentation (rename collisions)
        for (String col : dpHeader) {
            if (INSTRUMENTATION_CSV_IDENTIFIERS.contains(col)) continue;
            if ("optimal_value".equals(col)) continue;
            String outputCol = DP_COLLISION_COLUMNS.contains(col)
                ? dpCollisionName(col) : col;
            if (used.add(outputCol)) {
                headers.add(outputCol);
            }
        }

        // 6. Greedy instrumentation
        for (String col : greedyHeader) {
            if (INSTRUMENTATION_CSV_IDENTIFIERS.contains(col)) continue;
            if (used.add(col)) {
                headers.add(col);
            }
        }

        return headers;
    }

    // ---- Verification ----

    private static void verifyOutput(Path path, int expectedColumns, int expectedRows) throws IOException {
        try (Reader reader = new FileReader(path.toFile());
             CSVParser parser = CSVFormat.DEFAULT.builder()
                 .setHeader()
                 .setSkipHeaderRecord(true)
                 .setTrim(true)
                 .build()
                 .parse(reader)) {

            List<CSVRecord> records = parser.getRecords();
            List<String> headerNames = parser.getHeaderNames();
            int actualRows = records.size();
            int actualCols = headerNames.size();

            System.out.println("  Rows:    " + actualRows + " (expected " + expectedRows + ")");
            System.out.println("  Columns: " + actualCols + " (expected " + expectedColumns + ")");

            // Missing values count
            long missingCount = 0;
            for (CSVRecord record : records) {
                for (String col : headerNames) {
                    if ("optimal_value".equals(col) || "optimality_gap".equals(col)) continue;
                    String val = record.get(col);
                    if (val == null || val.trim().isEmpty()) {
                        missingCount++;
                    }
                }
            }
            System.out.println("  Missing values (excluding expected-empty optimal columns): " + missingCount);

            // Duplicate keys
            Set<String> outputKeys = new HashSet<>();
            int dupes = 0;
            for (CSVRecord record : records) {
                String key = record.get("instance_id") + KEY_SEPARATOR
                    + record.get("capacity_mode") + KEY_SEPARATOR
                    + record.get("algorithm");
                if (!outputKeys.add(key)) {
                    dupes++;
                }
            }
            System.out.println("  Duplicate (instance_id, capacity_mode, algorithm): " + dupes);

            // Identifier completeness
            long missingIdCount = 0;
            for (CSVRecord record : records) {
                for (String idCol : IDENTIFIER_COLUMNS) {
                    String val = record.get(idCol);
                    if (val == null || val.trim().isEmpty()) {
                        missingIdCount++;
                    }
                }
            }
            System.out.println("  Missing identifier values: " + missingIdCount);

            // Column provenance sample
            System.out.println("  Column sample: ");
            for (int i = 0; i < Math.min(headerNames.size(), 14); i++) {
                System.out.println("    [" + i + "] " + headerNames.get(i));
            }
            if (headerNames.size() > 14) {
                System.out.println("    ... (" + (headerNames.size() - 14) + " more columns)");
            }

            // Check that BB columns exist
            boolean hasBbMarks = headerNames.contains("leaf_nodes") || headerNames.contains("bb_internal");
            boolean hasDpMarks = headerNames.contains("include_count") || headerNames.contains("dp_include");
            boolean hasGreedyMarks = headerNames.contains("selected_count");

            System.out.println("  Has BB instrumentation columns: " + hasBbMarks);
            System.out.println("  Has DP instrumentation columns: " + hasDpMarks);
            System.out.println("  Has Greedy instrumentation columns: " + hasGreedyMarks);

            // Verify DP collision columns are properly named
            boolean hasDpSumImprovement = headerNames.contains("dp_sum_improvement_amount");
            boolean hasBbSumImprovement = headerNames.contains("sum_improvement_amount");
            System.out.println("  DP collision fix (dp_sum_improvement_amount): " + hasDpSumImprovement);
            System.out.println("  BB original (sum_improvement_amount): " + hasBbSumImprovement);
        }
    }
}
