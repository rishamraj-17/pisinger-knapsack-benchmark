package dataset;

import model.Item;
import model.KnapsackInstance;

import java.util.Random;

public interface InstanceGenerator {
    KnapsackInstance generate(int id, Random rng);
    String getFamilyName();
    String getParams();
}