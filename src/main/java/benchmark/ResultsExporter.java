package benchmark;

import model.Result;

import org.apache.commons.csv.CSVFormat;
import org.apache.commons.csv.CSVPrinter;

import java.io.FileWriter;
import java.io.IOException;
import java.nio.file.Path;
import java.util.List;

public final class ResultsExporter {
    public static void export(List<Result> results, Path outputPath) throws IOException {
        export(results, outputPath, "fixed");
    }

    public static void export(List<Result> results, Path outputPath, String capacityMode) throws IOException {
        String[] header = Result.csvHeader();
        String[] fullHeader = new String[header.length + 1];
        System.arraycopy(header, 0, fullHeader, 0, header.length);
        fullHeader[header.length] = "capacity_mode";

        try (FileWriter writer = new FileWriter(outputPath.toFile());
             CSVPrinter printer = new CSVPrinter(writer, CSVFormat.DEFAULT.builder().setHeader(fullHeader).build())) {

            for (Result r : results) {
                String[] row = r.toCsvRow();
                String[] fullRow = new String[row.length + 1];
                System.arraycopy(row, 0, fullRow, 0, row.length);
                fullRow[row.length] = capacityMode;
                printer.printRecord((Object[]) fullRow);
            }
            printer.flush();
        }
        System.out.println("Exported " + results.size() + " results to " + outputPath);
    }
}