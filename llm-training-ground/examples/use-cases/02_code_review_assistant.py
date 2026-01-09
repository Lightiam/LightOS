"""
LightOS LLM Training Ground - Use Case Example 2
Code Review Assistant

This example demonstrates building an automated code review system
that provides feedback on code quality, bugs, and best practices.

Requirements:
- 8GB+ VRAM for GLM-4 or Qwen
- Code samples for review
- CUDA-capable GPU

Time: ~5 minutes for setup
"""

import sys
sys.path.append('/opt/lightos/llm-training-ground')

from coding_agents.glm4_agent import GLM4CodingAgent
from coding_agents.qwen3_coder import Qwen3CoderAgent
import os
import glob

print("🔍 Automated Code Review Assistant")
print("=" * 60)
print()

class CodeReviewAssistant:
    def __init__(self, use_glm4=True):
        print("Initializing code review agent...")

        if use_glm4:
            self.agent = GLM4CodingAgent(load_in_4bit=True)
            self.agent_name = "GLM-4"
        else:
            self.agent = Qwen3CoderAgent(model_size="7b", load_in_4bit=True)
            self.agent_name = "Qwen2.5-Coder"

        self.agent.load_model()
        print(f"✅ {self.agent_name} loaded!")
        print()

    def review_code(self, code, filename="unknown"):
        """Perform comprehensive code review"""
        print(f"📝 Reviewing: {filename}")
        print("-" * 60)

        review = {
            "filename": filename,
            "issues": [],
            "suggestions": [],
            "security": [],
            "style": [],
            "score": 0
        }

        # 1. Check for bugs
        print("  Checking for bugs...")
        bug_check_prompt = f"""
Review this code for bugs and logical errors:

{code}

List any bugs found, or say "No bugs found" if the code is correct.
"""
        bugs = self.agent.explain_code(bug_check_prompt)
        if "no bugs found" not in bugs.lower():
            review["issues"].append(f"Potential bugs: {bugs}")

        # 2. Security review
        print("  Checking security...")
        security_prompt = f"""
Review this code for security vulnerabilities (SQL injection, XSS, command injection, etc.):

{code}

List any security issues found.
"""
        security = self.agent.explain_code(security_prompt)
        if "no security" not in security.lower() and "secure" not in security.lower():
            review["security"].append(security)

        # 3. Code style and best practices
        print("  Checking style and best practices...")
        style_prompt = f"""
Review this code for style issues and best practices:

{code}

Suggest improvements for:
- Variable naming
- Function length
- Code organization
- Documentation
"""
        style = self.agent.explain_code(style_prompt)
        review["style"].append(style)

        # 4. Suggest improvements
        print("  Generating improvement suggestions...")
        if hasattr(self.agent, 'refactor_code'):
            improved = self.agent.refactor_code(code)
            review["suggestions"].append(improved)

        # 5. Calculate quality score (simple heuristic)
        score = 100
        score -= len(review["issues"]) * 15
        score -= len(review["security"]) * 25
        score = max(0, min(100, score))
        review["score"] = score

        print(f"  Quality score: {score}/100")
        print()

        return review

    def review_file(self, filepath):
        """Review a single file"""
        with open(filepath, 'r') as f:
            code = f.read()

        return self.review_code(code, os.path.basename(filepath))

    def review_directory(self, directory, pattern="**/*.py"):
        """Review all files in a directory"""
        files = glob.glob(os.path.join(directory, pattern), recursive=True)

        print(f"Found {len(files)} files to review")
        print()

        reviews = []
        for filepath in files:
            review = self.review_file(filepath)
            reviews.append(review)

        return reviews

    def generate_report(self, reviews):
        """Generate markdown report"""
        report = "# Code Review Report\n\n"
        report += f"**Reviewer:** {self.agent_name}\n"
        report += f"**Files reviewed:** {len(reviews)}\n\n"

        # Summary
        avg_score = sum(r["score"] for r in reviews) / len(reviews)
        report += f"## Summary\n\n"
        report += f"Average quality score: **{avg_score:.1f}/100**\n\n"

        # Individual file reviews
        report += "## File Reviews\n\n"

        for review in reviews:
            report += f"### {review['filename']} (Score: {review['score']}/100)\n\n"

            if review["issues"]:
                report += "**Issues:**\n"
                for issue in review["issues"]:
                    report += f"- {issue}\n"
                report += "\n"

            if review["security"]:
                report += "**Security Concerns:**\n"
                for sec in review["security"]:
                    report += f"- ⚠️  {sec}\n"
                report += "\n"

            if review["style"]:
                report += "**Style Suggestions:**\n"
                for style in review["style"]:
                    report += f"- {style}\n"
                report += "\n"

            report += "---\n\n"

        return report

# Example usage
print("Example 1: Review a single file")
print("=" * 60)
print()

# Create example code to review
example_code = '''
def calculate_average(numbers):
    total = 0
    for num in numbers:
        total += num
    return total / len(numbers)

def process_user_input(user_data):
    # Potential SQL injection vulnerability
    query = f"SELECT * FROM users WHERE name = '{user_data}'"
    return execute_query(query)

def divide(a, b):
    # No error handling
    return a / b
'''

# Initialize reviewer
reviewer = CodeReviewAssistant(use_glm4=True)

# Review the code
review = reviewer.review_code(example_code, "example.py")

# Display results
print("Review Results:")
print(f"  Quality Score: {review['score']}/100")
print(f"  Issues found: {len(review['issues'])}")
print(f"  Security concerns: {len(review['security'])}")
print()

# Example 2: Review an entire project
print("Example 2: Review entire project")
print("=" * 60)
print()

# Review all Python files in current directory
reviews = reviewer.review_directory(".", "*.py")

# Generate report
report = reviewer.generate_report(reviews)

# Save report
with open('./code_review_report.md', 'w') as f:
    f.write(report)

print("✅ Report saved to: code_review_report.md")
print()

# Display summary
print("Summary:")
for review in reviews:
    status = "✅" if review["score"] >= 80 else "⚠️ " if review["score"] >= 60 else "❌"
    print(f"  {status} {review['filename']}: {review['score']}/100")
print()

print("✅ Code review complete!")
print()
print("Next steps:")
print("  1. Review the detailed report")
print("  2. Fix identified issues")
print("  3. Re-run review to verify improvements")
print("  4. Integrate into CI/CD pipeline")
