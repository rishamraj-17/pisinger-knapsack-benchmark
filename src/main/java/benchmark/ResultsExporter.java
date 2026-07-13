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
        try (FileWriter writer = new FileWriter(outputPath.toFile());
             CSVPrinter printer = new CSVPrinter(writer, CSVFormat.DEFAULT.withHeader(Result.csvHeader()))) {

            for (Result r : results) {
                printer.printRecord(r.toCsvRow());
            }
            printer.flush();
        }
        System.out.println("Exported " + results.size() + " results to " + outputPath);
    }
}