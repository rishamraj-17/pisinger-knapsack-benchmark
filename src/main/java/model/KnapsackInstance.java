package model;

public final class KnapsackInstance {
    private final int id;
    private final int n;
    private final int capacity;
    private final Item[] items;
    private final String familyName;
    private final String params;
    private final int baseSeed;

    public KnapsackInstance(int id, int n, int capacity, Item[] items, String familyName, String params) {
        this(id, n, capacity, items, familyName, params, 0);
    }

    public KnapsackInstance(int id, int n, int capacity, Item[] items, String familyName, String params, int baseSeed) {
        this.id = id;
        this.n = n;
        this.capacity = capacity;
        this.items = items;
        this.familyName = familyName;
        this.params = params;
        this.baseSeed = baseSeed;
    }

    public int getId() { return id; }
    public int getN() { return n; }
    public int getCapacity() { return capacity; }
    public Item[] getItems() { return items.clone(); }
    public String getFamilyName() { return familyName; }
    public String getParams() { return params; }
    public int getBaseSeed() { return baseSeed; }

    public int getTotalWeight() {
        int sum = 0;
        for (Item item : items) sum += item.getWeight();
        return sum;
    }

    public int getTotalValue() {
        int sum = 0;
        for (Item item : items) sum += item.getValue();
        return sum;
    }

    @Override
    public String toString() {
        return String.format("Instance{id=%d, n=%d, C=%d, family=%s, params=%s}",
                id, n, capacity, familyName, params);
    }
}