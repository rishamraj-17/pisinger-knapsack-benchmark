package dataset;

import model.KnapsackInstance;

import java.util.ArrayList;
import java.util.List;
import java.util.Random;

public final class DatasetGenerator {

    public enum CapacityMode {
        FIXED,
        SCALED
    }

    private final List<InstanceGenerator> baseGenerators;
    private final List<Integer> sizes;
    private final int instancesPerConfig;
    private final long seed;
    private final CapacityMode capacityMode;

    private DatasetGenerator(Builder builder) {
        this.baseGenerators = builder.generators;
        this.sizes = builder.sizes;
        this.instancesPerConfig = builder.instancesPerConfig;
        this.seed = builder.seed;
        this.capacityMode = builder.capacityMode;
    }

    public List<KnapsackInstance> generate() {
        List<KnapsackInstance> instances = new ArrayList<>();
        int id = 0;
        
        for (int n : sizes) {
            Random rng = new Random(seed + n);
            for (InstanceGenerator baseGen : baseGenerators) {
                InstanceGenerator sizedGen = createSizedGenerator(baseGen, n);
                for (int i = 0; i < instancesPerConfig; i++) {
                    KnapsackInstance inst = sizedGen.generate(id++, rng);
                    if (capacityMode == CapacityMode.SCALED) {
                        int totalWeight = inst.getTotalWeight();
                        int scaledCapacity = (int) (totalWeight * 0.5);
                        inst = new KnapsackInstance(inst.getId(), inst.getN(), scaledCapacity,
                                inst.getItems(), inst.getFamilyName(), inst.getParams());
                    }
                    instances.add(inst);
                }
            }
        }
        return instances;
    }

    private InstanceGenerator createSizedGenerator(InstanceGenerator base, int n) {
        if (base instanceof UncorrelatedGenerator u) {
            return new UncorrelatedGenerator(n, u.capacity, u.maxWeight, u.maxValue);
        } else if (base instanceof WeaklyCorrelatedGenerator w) {
            return new WeaklyCorrelatedGenerator(n, w.capacity, w.maxWeight, w.delta);
        } else if (base instanceof StronglyCorrelatedGenerator s) {
            return new StronglyCorrelatedGenerator(n, s.capacity, s.maxWeight);
        } else if (base instanceof InverseCorrelatedGenerator inv) {
            return new InverseCorrelatedGenerator(n, inv.capacity, inv.maxWeight);
        } else if (base instanceof AlmostEqualRatiosGenerator a) {
            return new AlmostEqualRatiosGenerator(n, a.capacity, a.maxWeight, a.baseRatio);
        }
        throw new IllegalArgumentException("Unknown generator: " + base.getClass());
    }

    public static Builder builder() {
        return new Builder();
    }

    public static final class Builder {
        private final List<InstanceGenerator> generators = new ArrayList<>();
        private final List<Integer> sizes = new ArrayList<>();
        private int instancesPerConfig = 10;
        private long seed = System.currentTimeMillis();
        private CapacityMode capacityMode = CapacityMode.FIXED;

        public Builder addGenerator(InstanceGenerator gen) {
            generators.add(gen);
            return this;
        }

        public Builder sizes(int... ns) {
            for (int n : ns) sizes.add(n);
            return this;
        }

        public Builder instancesPerConfig(int n) {
            instancesPerConfig = n;
            return this;
        }

        public Builder seed(long seed) {
            this.seed = seed;
            return this;
        }

        public Builder capacityMode(CapacityMode mode) {
            this.capacityMode = mode;
            return this;
        }

        public DatasetGenerator build() {
            return new DatasetGenerator(this);
        }
    }
}