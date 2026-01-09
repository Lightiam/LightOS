#!/usr/bin/env python3
"""
LightOS GLM-4 Coding Agent
Local coding assistant powered by GLM-4-9B-Chat

Features:
- Code generation and completion
- Code explanation and documentation
- Bug fixing and debugging
- Function calling support
- Multi-language support (Python, JavaScript, Java, C++, etc.)
"""

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from typing import Optional, List, Dict
import json

class GLM4CodingAgent:
    """
    GLM-4 Coding Assistant

    Example:
        agent = GLM4CodingAgent()
        agent.load_model()
        code = agent.generate_code("Write a Python function to calculate fibonacci")
        print(code)
    """

    def __init__(
        self,
        model_name: str = "THUDM/glm-4-9b-chat",
        device: str = "auto",
        load_in_4bit: bool = True
    ):
        self.model_name = model_name
        self.device = device
        self.load_in_4bit = load_in_4bit
        self.model = None
        self.tokenizer = None

    def load_model(self):
        """Load GLM-4 model for coding tasks"""
        print(f"Loading GLM-4 Coding Agent: {self.model_name}")

        self.tokenizer = AutoTokenizer.from_pretrained(
            self.model_name,
            trust_remote_code=True
        )

        if self.load_in_4bit:
            from transformers import BitsAndBytesConfig
            quantization_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_compute_dtype=torch.bfloat16,
                bnb_4bit_use_double_quant=True,
                bnb_4bit_quant_type="nf4"
            )

            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                quantization_config=quantization_config,
                device_map=self.device,
                trust_remote_code=True
            )
        else:
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                device_map=self.device,
                trust_remote_code=True,
                torch_dtype=torch.bfloat16
            )

        print("✓ GLM-4 Coding Agent loaded")
        print(f"  - Model: {self.model_name}")
        print(f"  - 4-bit quantization: {self.load_in_4bit}")
        print(f"  - Device: {self.device}")

    def generate_code(
        self,
        prompt: str,
        language: str = "python",
        max_length: int = 2048,
        temperature: float = 0.7,
        top_p: float = 0.95
    ) -> str:
        """
        Generate code based on natural language description

        Args:
            prompt: Description of what code should do
            language: Programming language (python, javascript, java, etc.)
            max_length: Maximum tokens to generate
            temperature: Sampling temperature (higher = more creative)
            top_p: Nucleus sampling parameter

        Returns:
            Generated code as string
        """
        system_prompt = f"""You are a helpful coding assistant. Generate clean, efficient {language} code.
Follow best practices and include comments where helpful."""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]

        inputs = self.tokenizer.apply_chat_template(
            messages,
            add_generation_prompt=True,
            return_tensors="pt"
        ).to(self.model.device)

        outputs = self.model.generate(
            inputs,
            max_new_tokens=max_length,
            temperature=temperature,
            top_p=top_p,
            do_sample=True,
        )

        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)

        # Extract just the code portion
        if "```" in response:
            code_blocks = response.split("```")
            if len(code_blocks) >= 3:
                code = code_blocks[1]
                # Remove language identifier if present
                if code.startswith(language):
                    code = code[len(language):].strip()
                return code.strip()

        return response

    def explain_code(self, code: str, language: str = "python") -> str:
        """
        Generate explanation for given code

        Args:
            code: Code to explain
            language: Programming language

        Returns:
            Explanation text
        """
        prompt = f"""Explain what this {language} code does:

```{language}
{code}
```

Provide a clear, step-by-step explanation."""

        messages = [
            {"role": "user", "content": prompt}
        ]

        inputs = self.tokenizer.apply_chat_template(
            messages,
            add_generation_prompt=True,
            return_tensors="pt"
        ).to(self.model.device)

        outputs = self.model.generate(
            inputs,
            max_new_tokens=1024,
            temperature=0.3,
            do_sample=True,
        )

        return self.tokenizer.decode(outputs[0], skip_special_tokens=True)

    def fix_bug(self, code: str, error: str, language: str = "python") -> str:
        """
        Fix bugs in code based on error message

        Args:
            code: Buggy code
            error: Error message or description
            language: Programming language

        Returns:
            Fixed code
        """
        prompt = f"""Fix this {language} code that's producing an error:

**Code:**
```{language}
{code}
```

**Error:**
{error}

Provide the corrected code."""

        messages = [
            {"role": "user", "content": prompt}
        ]

        inputs = self.tokenizer.apply_chat_template(
            messages,
            add_generation_prompt=True,
            return_tensors="pt"
        ).to(self.model.device)

        outputs = self.model.generate(
            inputs,
            max_new_tokens=2048,
            temperature=0.5,
            do_sample=True,
        )

        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)

        # Extract fixed code
        if "```" in response:
            code_blocks = response.split("```")
            if len(code_blocks) >= 3:
                return code_blocks[1].replace(language, "").strip()

        return response

    def add_documentation(self, code: str, language: str = "python") -> str:
        """
        Add docstrings/comments to code

        Args:
            code: Code to document
            language: Programming language

        Returns:
            Documented code
        """
        prompt = f"""Add comprehensive documentation to this {language} code:

```{language}
{code}
```

Include docstrings, type hints, and inline comments."""

        messages = [
            {"role": "user", "content": prompt}
        ]

        inputs = self.tokenizer.apply_chat_template(
            messages,
            add_generation_prompt=True,
            return_tensors="pt"
        ).to(self.model.device)

        outputs = self.model.generate(
            inputs,
            max_new_tokens=2048,
            temperature=0.3,
            do_sample=True,
        )

        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)

        if "```" in response:
            code_blocks = response.split("```")
            if len(code_blocks) >= 3:
                return code_blocks[1].replace(language, "").strip()

        return response

    def chat(self, message: str, history: Optional[List[Dict]] = None) -> str:
        """
        Chat with the coding agent

        Args:
            message: User message
            history: Conversation history

        Returns:
            Agent response
        """
        if history is None:
            history = []

        messages = history + [{"role": "user", "content": message}]

        inputs = self.tokenizer.apply_chat_template(
            messages,
            add_generation_prompt=True,
            return_tensors="pt"
        ).to(self.model.device)

        outputs = self.model.generate(
            inputs,
            max_new_tokens=2048,
            temperature=0.7,
            do_sample=True,
        )

        return self.tokenizer.decode(outputs[0], skip_special_tokens=True)

# CLI Interface
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("LightOS GLM-4 Coding Agent")
        print("=" * 60)
        print("\nUsage:")
        print("  python glm4_agent.py generate <prompt>")
        print("  python glm4_agent.py explain <file.py>")
        print("  python glm4_agent.py fix <file.py> '<error message>'")
        print("  python glm4_agent.py doc <file.py>")
        print("\nExamples:")
        print("  python glm4_agent.py generate 'fibonacci function in Python'")
        print("  python glm4_agent.py explain my_script.py")
        sys.exit(0)

    command = sys.argv[1]

    # Initialize agent
    agent = GLM4CodingAgent()
    agent.load_model()

    if command == "generate":
        prompt = " ".join(sys.argv[2:])
        code = agent.generate_code(prompt)
        print("\n" + "=" * 60)
        print("Generated Code:")
        print("=" * 60)
        print(code)

    elif command == "explain":
        file_path = sys.argv[2]
        with open(file_path, 'r') as f:
            code = f.read()
        explanation = agent.explain_code(code)
        print("\n" + "=" * 60)
        print("Code Explanation:")
        print("=" * 60)
        print(explanation)

    elif command == "fix":
        file_path = sys.argv[2]
        error = sys.argv[3] if len(sys.argv) > 3 else "Unknown error"
        with open(file_path, 'r') as f:
            code = f.read()
        fixed = agent.fix_bug(code, error)
        print("\n" + "=" * 60)
        print("Fixed Code:")
        print("=" * 60)
        print(fixed)

    elif command == "doc":
        file_path = sys.argv[2]
        with open(file_path, 'r') as f:
            code = f.read()
        documented = agent.add_documentation(code)
        print("\n" + "=" * 60)
        print("Documented Code:")
        print("=" * 60)
        print(documented)
