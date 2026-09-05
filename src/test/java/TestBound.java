public class TestBound {
    public static void main(String[] args) {
        double b1 = 100.0;
        b1 += 10;
        b1 += 20;
        b1 += (5.0) * 1.23456789;
        
        double b2 = 100.0;
        b2 += (30);
        b2 += (5.0) * 1.23456789;
        
        System.out.println(b1 == b2);
        System.out.println(Double.doubleToLongBits(b1) == Double.doubleToLongBits(b2));
    }
}
