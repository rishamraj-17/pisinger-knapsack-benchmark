package benchmark;

import algorithms.Algorithm;
import algorithms.BranchAndBound;
import algorithms.BranchAndBoundDFS;
import algorithms.BbInstrumentation;
import model.KnapsackInstance;
import model.Result;

import java.io.File;
import java.io.PrintWriter;
import java.util.List;

import dataset.DatasetGenerator;
import dataset.UncorrelatedGenerator;
import dataset.WeaklyCorrelatedGenerator;
import dataset.StronglyCorrelatedGenerator;
import dataset.InverseCorrelatedGenerator;
import dataset.AlmostEqualRatiosGenerator;

public class DfsSensitivityRunner {
    public static void main(String[] args) throws Exception {
        System.out.println("Running DFS Sensitivity Analysis...");
        
        File outDir = new File("results/revision-2");
        outDir.mkdirs();
        
        try (PrintWriter writer = new PrintWriter(new File(outDir, "dfs_sensitivity.csv"))) {
            writer.println("instance_id,family,n,capacity,bb_nodes,dfs_nodes");
            
            Algorithm bb = new BranchAndBound();
            Algorithm dfs = new BranchAndBoundDFS();
            
            DatasetGenerator fixedGen = DatasetGenerator.builder()
                    .addGenerator(new UncorrelatedGenerator(0, 1000, 1000, 1000))
                    .addGenerator(new WeaklyCorrelatedGenerator(0, 1000, 1000, 100))
                    .addGenerator(new StronglyCorrelatedGenerator(0, 1000, 1000))
                    .addGenerator(new InverseCorrelatedGenerator(0, 1000, 1000))
                    .addGenerator(new AlmostEqualRatiosGenerator(0, 1000, 1000, 1.0))
                    .sizes(new int[]{50, 100})
                    .instancesPerConfig(10)
                    .seed(42L)
                    .capacityMode(DatasetGenerator.CapacityMode.FIXED)
                    .build();
                    
            List<KnapsackInstance> fixedInstances = fixedGen.generate();
            System.out.println("Total instances to test: " + fixedInstances.size());
            
            for (KnapsackInstance instance : fixedInstances) {
                Result resBB = bb.solve(instance);
                Result resDFS = dfs.solve(instance);
                
                writer.printf("%s,%s,%d,%d,%d,%d%n",
                        instance.getId(),
                        instance.getFamilyName(),
                        instance.getN(),
                        instance.getCapacity(),
                        resBB.getNodesExplored(),
                        resDFS.getNodesExplored());
            }
        }
        
        System.out.println("DFS Sensitivity Analysis completed.");
    }
}
