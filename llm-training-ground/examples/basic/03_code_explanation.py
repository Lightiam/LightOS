"""
LightOS LLM Training Ground - Basic Example 3
Code Explanation with GLM-4

This example shows how to use GLM-4 to explain existing code,
perfect for understanding complex codebases.

Requirements:
- 8GB+ VRAM for 9B model (or use 4-bit quantization for 6GB)
- CUDA-capable GPU recommended

Time: ~2 minutes (first run downloads model)
"""

import sys
sys.path.append('/opt/lightos/llm-training-ground')

from coding_agents.glm4_agent import GLM4CodingAgent

print("🤖 Initializing GLM-4 Coding Agent...")
print("Model: GLM-4 9B")
print()

# Initialize agent with 4-bit quantization
agent = GLM4CodingAgent(load_in_4bit=True)
agent.load_model()

print("✅ Model loaded!")
print()

# Example 1: Explain a complex algorithm
print("=" * 60)
print("Example 1: Explain QuickSort Algorithm")
print("=" * 60)

complex_code = """
def quicksort(arr):
    if len(arr) <= 1:
        return arr
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    return quicksort(left) + middle + quicksort(right)
"""

explanation = agent.explain_code(complex_code, detail_level="detailed")
print(explanation)
print()

# Example 2: Explain a decorator
print("=" * 60)
print("Example 2: Explain Python Decorator")
print("=" * 60)

decorator_code = """
from functools import wraps
import time

def timing_decorator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(f"{func.__name__} took {end-start:.2f}s")
        return result
    return wrapper
"""

explanation = agent.explain_code(decorator_code, detail_level="beginner")
print(explanation)
print()

# Example 3: Find bugs
print("=" * 60)
print("Example 3: Find and Fix Bugs")
print("=" * 60)

buggy_code = """
def calculate_average(numbers):
    total = 0
    for num in numbers:
        total += num
    return total / len(numbers)

# Test
print(calculate_average([]))  # This will crash!
"""

fixed_code = agent.fix_bug(buggy_code)
print("Fixed code:")
print(fixed_code)
print()

print("✅ All examples complete!")
