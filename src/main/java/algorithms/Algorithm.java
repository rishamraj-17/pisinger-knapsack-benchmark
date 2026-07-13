package algorithms;

import model.KnapsackInstance;
import model.Result;

public interface Algorithm {
    String getName();
    Result solve(KnapsackInstance instance);
}