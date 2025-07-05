#!/usr/bin/env python3

def hello_world():
    print("Hello, World!")
    print("This is a simple example")

def calculate(a, b):
    print(f"Calculating {a} + {b}")
    result = a + b
    print(f"Result: {result}")
    return result

if __name__ == "__main__":
    hello_world()
    total = calculate(5, 3)
    print(f"Final total: {total}")
