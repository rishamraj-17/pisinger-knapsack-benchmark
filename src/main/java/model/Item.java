package model;

public final class Item {
    private final int id;
    private final int weight;
    private final int value;
    private final double ratio;

    public Item(int id, int weight, int value) {
        this.id = id;
        this.weight = weight;
        this.value = value;
        this.ratio = (double) value / weight;
    }

    public int getId() { return id; }
    public int getWeight() { return weight; }
    public int getValue() { return value; }
    public double getRatio() { return ratio; }

    @Override
    public String toString() {
        return String.format("Item{id=%d, w=%d, v=%d, ratio=%.3f}", id, weight, value, ratio);
    }
}