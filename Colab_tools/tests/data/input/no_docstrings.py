class Calculator:
    def __init__(self, precision=2):
        self.precision = precision
    
    def add(self, x, y):
        return round(x + y, self.precision)
    
    def multiply(self, x, y):
        return round(x * y, self.precision)

def process_numbers(numbers):
    total = 0
    for num in numbers:
        total += num
    return total

def test_function():
    calc = Calculator()
    return calc.add(1.1, 2.2)
