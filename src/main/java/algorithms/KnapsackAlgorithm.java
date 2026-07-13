package algorithms;

import model.KnapsackInstance;
import model.Solution;

public interface KnapsackAlgorithm {
    String getName();

    Solution solve(KnapsackInstance instance);

    default Solution solveWithOptimalCheck(KnapsackInstance instance, int optimalValue) {
        Solution sol = solve(instance);
        return new Solution(
            sol.getInstanceId(),
            sol.getAlgorithm(),
            sol.getTimeNanos(),
            sol.getTotalValue(),
            sol.getTotalWeight(),
            sol.getIncluded(),
            sol.getTotalValue() == optimalValue
        );
    }
}