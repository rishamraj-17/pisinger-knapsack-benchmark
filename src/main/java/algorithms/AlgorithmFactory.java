package algorithms;

public enum AlgorithmFactory {
    GREEDY("Greedy", Greedy::new),
    DYNAMIC_PROGRAMMING("DynamicProgramming", DynamicProgramming::new),
    BRANCH_AND_BOUND("BranchAndBound", BranchAndBound::new);

    private final String name;
    private final java.util.function.Supplier<Algorithm> supplier;

    AlgorithmFactory(String name, java.util.function.Supplier<Algorithm> supplier) {
        this.name = name;
        this.supplier = supplier;
    }

    public String getName() {
        return name;
    }

    public Algorithm create() {
        return supplier.get();
    }

    public static AlgorithmFactory fromName(String name) {
        for (AlgorithmFactory f : values()) {
            if (f.name.equalsIgnoreCase(name)) return f;
        }
        throw new IllegalArgumentException("Unknown algorithm: " + name);
    }
}