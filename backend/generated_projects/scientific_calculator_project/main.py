from calculator import ScientificCalculator

def main():
    print("Scientific Calculator")
    calc = ScientificCalculator()
    print("5 + 3 =", calc.add(5, 3))
    print("sin(30°) =", calc.sin(30))

if __name__ == "__main__":
    main()