"""
LightOS LLM Training Ground - Basic Example 2
Code Generation with Qwen2.5-Coder

This example demonstrates using the Qwen2.5-Coder agent to generate
code from natural language descriptions.

Requirements:
- 6GB+ VRAM for 7B model (or use 1.5B for 2GB)
- CUDA-capable GPU recommended (CPU also works)

Time: ~2 minutes (first run downloads model)
"""

import sys
sys.path.append('/opt/lightos/llm-training-ground')

from coding_agents.qwen3_coder import Qwen3CoderAgent

print("🤖 Initializing Qwen2.5-Coder...")
print("Model size: 7B (change to '1.5b' for lower memory)")
print()

# Initialize agent
agent = Qwen3CoderAgent(model_size="7b", load_in_4bit=True)
agent.load_model()

print("✅ Model loaded!")
print()

# Example 1: Generate a function
print("=" * 60)
print("Example 1: Generate Fibonacci Function")
print("=" * 60)

code = agent.generate_function(
    description="calculate fibonacci sequence up to n terms",
    language="python"
)

print(code)
print()

# Example 2: Generate REST API
print("=" * 60)
print("Example 2: Generate FastAPI REST API")
print("=" * 60)

api_code = agent.generate_code(
    prompt="Create a FastAPI REST API with authentication using JWT tokens",
    language="python",
    max_tokens=1024
)

print(api_code)
print()

# Example 3: Generate tests
print("=" * 60)
print("Example 3: Generate Unit Tests")
print("=" * 60)

test_code = agent.generate_tests(
    code="""
def add(a, b):
    return a + b

def multiply(a, b):
    return a * b
""",
    framework="pytest"
)

print(test_code)
print()

print("✅ All examples complete!")
