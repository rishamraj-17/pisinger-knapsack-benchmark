package dataset;

import model.KnapsackInstance;

import java.util.ArrayList;
import java.util.List;
import java.util.Random;

public final class DatasetBuilder {
    private final List<InstanceGenerator> generators;
    private final int instancesPerConfig;
    private final long seed;

    private DatasetBuilder(Builder builder) {
        this.generators = builder.generators;
        this.instancesPerConfig = builder.instancesPerConfig;
        this.seed = builder.seed;
    }

    public List<KnapsackInstance> build() {
        List<KnapsackInstance> instances = new ArrayList<>();
        Random rng = new Random(seed);
        int id = 0;
        for (InstanceGenerator gen : generators) {
            for (int i = 0; i < instancesPerConfig; i++) {
                instances.add(gen.generate(id++, rng));
            }
        }
        return instances;
    }

    public static Builder builder() {
        return new Builder();
    }

    public static final class Builder {
        private final List<InstanceGenerator> generators = new ArrayList<>();
        private int instancesPerConfig = 10;
        private long seed = System.currentTimeMillis();

        public Builder addGenerator(InstanceGenerator gen) {
            generators.add(gen);
            return this;
        }

        public Builder instancesPerConfig(int n) {
            this.instancesPerConfig = n;
            return this;
        }

        public Builder seed(long seed) {
            this.seed = seed;
            return this;
        }

        public DatasetBuilder build() {
            return new DatasetBuilder(this);
        }
    }
}