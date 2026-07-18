import dataset.*;
import model.*;
import algorithms.*;
import java.util.*;

public class TestNodeCount {
    public static void main(String[] args) {
        InstanceFactory factory = new InstanceFactory(1468);
        Instance instance = factory.generateAlmostEqualRatios(100);
        
        // Run HEAD BranchAndBound
        // I need the actual old code and new code. I'll just use the current BranchAndBound, which is the R1+R2 version.
        BranchAndBound bb = new BranchAndBound();
        Result r = bb.solve(instance);
        System.out.println("New B&B nodes: " + r.getNodesExplored());
    }
}
