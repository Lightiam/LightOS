#!/usr/bin/env python3
"""
LightOS Qwen3-Coder Agent
Fast, efficient coding assistant powered by Qwen2.5-Coder

Features:
- Excellent coding capabilities across 40+ languages
- Fast inference (optimized for local deployment)
- Multiple model sizes (0.5B to 32B parameters)
- Code generation, completion, and explanation
- Repository-level understanding
"""

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from typing import Optional, List, Dict, Tuple
import os

class Qwen3CoderAgent:
    """
    Qwen2.5-Coder Coding Assistant

    Supported Models:
    - qwen2.5-coder-0.5b (fastest, lightweight)
    - qwen2.5-coder-1.5b (balanced)
    - qwen2.5-coder-7b (recommended)
    - qwen2.5-coder-14b (high quality)
    - qwen2.5-coder-32b (best quality)

    Example:
        agent = Qwen3CoderAgent(model_size="7b")
        agent.load_model()
        code = agent.complete_code("def fibonacci(n):\\n    ")
        print(code)
    """

    MODEL_SIZES = {
        "0.5b": "Qwen/Qwen2.5-Coder-0.5B-Instruct",
        "1.5b": "Qwen/Qwen2.5-Coder-1.5B-Instruct",
        "7b": "Qwen/Qwen2.5-Coder-7B-Instruct",
        "14b": "Qwen/Qwen2.5-Coder-14B-Instruct",
        "32b": "Qwen/Qwen2.5-Coder-32B-Instruct",
    }

    def __init__(
        self,
        model_size: str = "7b",
        device: str = "auto",
        load_in_4bit: bool = True,
        flash_attention: bool = True
    ):
        if model_size not in self.MODEL_SIZES:
            raise ValueError(f"Invalid model size. Choose from: {list(self.MODEL_SIZES.keys())}")

        self.model_size = model_size
        self.model_name = self.MODEL_SIZES[model_size]
        self.device = device
        self.load_in_4bit = load_in_4bit
        self.flash_attention = flash_attention
        self.model = None
        self.tokenizer = None

    def load_model(self):
        """Load Qwen2.5-Coder model"""
        print(f"Loading Qwen2.5-Coder ({self.model_size}): {self.model_name}")

        self.tokenizer = AutoTokenizer.from_pretrained(
            self.model_name,
            trust_remote_code=True
        )

        model_kwargs = {
            "trust_remote_code": True,
            "device_map": self.device,
        }

        if self.load_in_4bit and self.model_size != "0.5b":
            from transformers import BitsAndBytesConfig
            model_kwargs["quantization_config"] = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_compute_dtype=torch.bfloat16,
                bnb_4bit_use_double_quant=True,
                bnb_4bit_quant_type="nf4"
            )
        else:
            model_kwargs["torch_dtype"] = torch.bfloat16

        if self.flash_attention:
            model_kwargs["attn_implementation"] = "flash_attention_2"

        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            **model_kwargs
        )

        print("✓ Qwen2.5-Coder loaded")
        print(f"  - Model: {self.model_size}")
        print(f"  - 4-bit quantization: {self.load_in_4bit}")
        print(f"  - Flash Attention: {self.flash_attention}")

    def complete_code(
        self,
        code_prefix: str,
        max_tokens: int = 512,
        temperature: float = 0.2,
        stop_tokens: Optional[List[str]] = None
    ) -> str:
        """
        Complete code from prefix

        Args:
            code_prefix: Beginning of code to complete
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            stop_tokens: List of tokens that stop generation

        Returns:
            Completed code
        """
        if stop_tokens is None:
            stop_tokens = ["\n\n", "```", "def ", "class ", "if __name__"]

        inputs = self.tokenizer(code_prefix, return_tensors="pt").to(self.model.device)

        outputs = self.model.generate(
            **inputs,
            max_new_tokens=max_tokens,
            temperature=temperature,
            do_sample=temperature > 0,
            pad_token_id=self.tokenizer.eos_token_id,
        )

        completion = self.tokenizer.decode(outputs[0], skip_special_tokens=True)

        # Remove the input prefix
        completion = completion[len(code_prefix):]

        # Stop at first stop token
        for stop in stop_tokens:
            if stop in completion:
                completion = completion[:completion.index(stop)]

        return completion.strip()

    def generate_function(
        self,
        description: str,
        language: str = "python",
        function_name: Optional[str] = None
    ) -> str:
        """
        Generate a function based on description

        Args:
            description: What the function should do
            language: Programming language
            function_name: Specific function name (optional)

        Returns:
            Generated function code
        """
        prompt = f"""Write a {language} function that {description}.
"""
        if function_name:
            prompt += f"Function name: {function_name}\n"

        prompt += f"\n```{language}\n"

        messages = [
            {"role": "system", "content": f"You are an expert {language} programmer."},
            {"role": "user", "content": prompt}
        ]

        text = self.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True
        )

        inputs = self.tokenizer([text], return_tensors="pt").to(self.model.device)

        outputs = self.model.generate(
            **inputs,
            max_new_tokens=1024,
            temperature=0.3,
            do_sample=True,
        )

        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)

        # Extract code from markdown
        if "```" in response:
            parts = response.split("```")
            if len(parts) >= 3:
                code = parts[1]
                if code.startswith(language):
                    code = code[len(language):].strip()
                return code.strip()

        return response

    def explain_code(
        self,
        code: str,
        language: str = "python",
        detailed: bool = True
    ) -> str:
        """
        Explain code in natural language

        Args:
            code: Code to explain
            language: Programming language
            detailed: Whether to provide detailed explanation

        Returns:
            Code explanation
        """
        detail_level = "detailed" if detailed else "concise"
        prompt = f"""Provide a {detail_level} explanation of this {language} code:

```{language}
{code}
```
"""

        messages = [
            {"role": "user", "content": prompt}
        ]

        text = self.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True
        )

        inputs = self.tokenizer([text], return_tensors="pt").to(self.model.device)

        outputs = self.model.generate(
            **inputs,
            max_new_tokens=1024,
            temperature=0.3,
            do_sample=True,
        )

        return self.tokenizer.decode(outputs[0], skip_special_tokens=True)

    def refactor_code(
        self,
        code: str,
        language: str = "python",
        improvements: Optional[List[str]] = None
    ) -> str:
        """
        Refactor code for better quality

        Args:
            code: Code to refactor
            language: Programming language
            improvements: Specific improvements to make

        Returns:
            Refactored code
        """
        prompt = f"""Refactor this {language} code to improve:
- Readability
- Performance
- Best practices
"""
        if improvements:
            for improvement in improvements:
                prompt += f"- {improvement}\n"

        prompt += f"\nOriginal code:\n```{language}\n{code}\n```\n"

        messages = [
            {"role": "user", "content": prompt}
        ]

        text = self.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True
        )

        inputs = self.tokenizer([text], return_tensors="pt").to(self.model.device)

        outputs = self.model.generate(
            **inputs,
            max_new_tokens=2048,
            temperature=0.3,
            do_sample=True,
        )

        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)

        # Extract refactored code
        if "```" in response:
            parts = response.split("```")
            if len(parts) >= 3:
                code = parts[1]
                if code.startswith(language):
                    code = code[len(language):].strip()
                return code.strip()

        return response

    def debug_code(
        self,
        code: str,
        error_message: str,
        language: str = "python"
    ) -> Tuple[str, str]:
        """
        Debug code and provide fix

        Args:
            code: Buggy code
            error_message: Error message or description
            language: Programming language

        Returns:
            Tuple of (fixed_code, explanation)
        """
        prompt = f"""Debug this {language} code that produces an error:

**Code:**
```{language}
{code}
```

**Error:**
{error_message}

Provide:
1. Explanation of the bug
2. Fixed code
"""

        messages = [
            {"role": "user", "content": prompt}
        ]

        text = self.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True
        )

        inputs = self.tokenizer([text], return_tensors="pt").to(self.model.device)

        outputs = self.model.generate(
            **inputs,
            max_new_tokens=2048,
            temperature=0.3,
            do_sample=True,
        )

        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)

        # Extract explanation and fixed code
        explanation = response
        fixed_code = code  # fallback

        if "```" in response:
            parts = response.split("```")
            if len(parts) >= 3:
                fixed_code = parts[1]
                if fixed_code.startswith(language):
                    fixed_code = fixed_code[len(language):].strip()
                fixed_code = fixed_code.strip()

                # Explanation is before the code block
                explanation = parts[0].strip()

        return fixed_code, explanation

    def generate_tests(
        self,
        code: str,
        language: str = "python",
        framework: str = "pytest"
    ) -> str:
        """
        Generate unit tests for code

        Args:
            code: Code to test
            language: Programming language
            framework: Testing framework (pytest, unittest, jest, etc.)

        Returns:
            Test code
        """
        prompt = f"""Generate comprehensive unit tests for this {language} code using {framework}:

```{language}
{code}
```

Include:
- Normal cases
- Edge cases
- Error cases
"""

        messages = [
            {"role": "user", "content": prompt}
        ]

        text = self.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True
        )

        inputs = self.tokenizer([text], return_tensors="pt").to(self.model.device)

        outputs = self.model.generate(
            **inputs,
            max_new_tokens=2048,
            temperature=0.3,
            do_sample=True,
        )

        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)

        # Extract test code
        if "```" in response:
            parts = response.split("```")
            if len(parts) >= 3:
                tests = parts[1]
                if tests.startswith(language):
                    tests = tests[len(language):].strip()
                return tests.strip()

        return response

    def chat(
        self,
        message: str,
        history: Optional[List[Dict]] = None,
        system_prompt: Optional[str] = None
    ) -> str:
        """
        Interactive chat with the coding agent

        Args:
            message: User message
            history: Conversation history
            system_prompt: Custom system prompt

        Returns:
            Agent response
        """
        if history is None:
            history = []

        if system_prompt is None:
            system_prompt = "You are Qwen2.5-Coder, an expert programming assistant."

        messages = [{"role": "system", "content": system_prompt}]
        messages.extend(history)
        messages.append({"role": "user", "content": message})

        text = self.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True
        )

        inputs = self.tokenizer([text], return_tensors="pt").to(self.model.device)

        outputs = self.model.generate(
            **inputs,
            max_new_tokens=2048,
            temperature=0.7,
            do_sample=True,
        )

        return self.tokenizer.decode(outputs[0], skip_special_tokens=True)

# CLI Interface
if __name__ == "__main__":
    import sys
    import argparse

    parser = argparse.ArgumentParser(description="Qwen2.5-Coder Coding Agent")
    parser.add_argument("--model", default="7b", choices=list(Qwen3CoderAgent.MODEL_SIZES.keys()),
                       help="Model size to use")
    parser.add_argument("command", choices=["generate", "complete", "explain", "refactor", "debug", "test", "chat"],
                       help="Command to execute")
    parser.add_argument("args", nargs="*", help="Command arguments")

    args = parser.parse_args()

    # Initialize agent
    print(f"Loading Qwen2.5-Coder ({args.model})...")
    agent = Qwen3CoderAgent(model_size=args.model)
    agent.load_model()

    if args.command == "generate":
        description = " ".join(args.args)
        code = agent.generate_function(description)
        print("\n" + "=" * 60)
        print("Generated Code:")
        print("=" * 60)
        print(code)

    elif args.command == "complete":
        prefix = " ".join(args.args)
        completion = agent.complete_code(prefix)
        print("\n" + "=" * 60)
        print("Completed Code:")
        print("=" * 60)
        print(prefix + completion)

    elif args.command == "explain":
        if args.args:
            with open(args.args[0], 'r') as f:
                code = f.read()
        else:
            print("Reading from stdin (Ctrl+D when done):")
            code = sys.stdin.read()

        explanation = agent.explain_code(code)
        print("\n" + "=" * 60)
        print("Explanation:")
        print("=" * 60)
        print(explanation)

    elif args.command == "refactor":
        if args.args:
            with open(args.args[0], 'r') as f:
                code = f.read()
        else:
            code = sys.stdin.read()

        refactored = agent.refactor_code(code)
        print("\n" + "=" * 60)
        print("Refactored Code:")
        print("=" * 60)
        print(refactored)

    elif args.command == "debug":
        file_path = args.args[0]
        error = " ".join(args.args[1:]) if len(args.args) > 1 else "Unknown error"

        with open(file_path, 'r') as f:
            code = f.read()

        fixed, explanation = agent.debug_code(code, error)
        print("\n" + "=" * 60)
        print("Bug Analysis:")
        print("=" * 60)
        print(explanation)
        print("\n" + "=" * 60)
        print("Fixed Code:")
        print("=" * 60)
        print(fixed)

    elif args.command == "test":
        if args.args:
            with open(args.args[0], 'r') as f:
                code = f.read()
        else:
            code = sys.stdin.read()

        tests = agent.generate_tests(code)
        print("\n" + "=" * 60)
        print("Generated Tests:")
        print("=" * 60)
        print(tests)

    elif args.command == "chat":
        print("\nQwen2.5-Coder Interactive Chat")
        print("Type 'exit' to quit\n")

        history = []
        while True:
            user_input = input("You: ")
            if user_input.lower() in ['exit', 'quit']:
                break

            response = agent.chat(user_input, history)
            print(f"\nAssistant: {response}\n")

            history.append({"role": "user", "content": user_input})
            history.append({"role": "assistant", "content": response})
