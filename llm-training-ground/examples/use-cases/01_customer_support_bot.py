"""
LightOS LLM Training Ground - Use Case Example 1
Build a Customer Support Chatbot

This example shows how to fine-tune a model for customer support,
then deploy it as an interactive chatbot.

Requirements:
- 8GB+ VRAM
- Customer support conversation dataset
- CUDA-capable GPU

Time: ~1 hour for training + deployment setup
"""

import sys
sys.path.append('/opt/lightos/llm-training-ground')

from unsloth_integration import quick_finetune
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
import json

print("🤖 Building Customer Support Chatbot")
print("=" * 60)
print()

# Step 1: Prepare customer support dataset
print("Step 1: Preparing customer support dataset...")

support_conversations = [
    {
        "instruction": "How do I reset my password?",
        "input": "",
        "output": "To reset your password, go to Settings > Account > Reset Password. You'll receive a verification email with instructions."
    },
    {
        "instruction": "My account is locked. What should I do?",
        "input": "",
        "output": "If your account is locked, please contact support at support@example.com with your username. We'll unlock it within 24 hours."
    },
    {
        "instruction": "How do I cancel my subscription?",
        "input": "",
        "output": "To cancel your subscription, go to Settings > Billing > Cancel Subscription. You'll retain access until the end of your billing period."
    },
    {
        "instruction": "I'm getting error code 500. Help!",
        "input": "",
        "output": "Error 500 indicates a server issue. Please try again in a few minutes. If the problem persists, contact support with the exact time the error occurred."
    },
    {
        "instruction": "Can I get a refund?",
        "input": "",
        "output": "We offer refunds within 30 days of purchase. Please email support@example.com with your order number and reason for the refund."
    },
    # Add 100+ more real examples for best results
]

# Save dataset
dataset_path = './datasets/customer_support.json'
with open(dataset_path, 'w') as f:
    json.dump(support_conversations, f, indent=2)

print(f"✅ Created dataset with {len(support_conversations)} conversations")
print()

# Step 2: Fine-tune model
print("Step 2: Fine-tuning model on customer support data...")
print("This will take ~30 minutes...")
print()

model_output_dir = './models/customer-support-bot'

quick_finetune(
    model_name="llama-3.1-8b",
    dataset_name=dataset_path,
    output_dir=model_output_dir,
    max_steps=200  # Increase for better quality
)

print("✅ Model fine-tuned!")
print()

# Step 3: Create chatbot interface
print("Step 3: Creating chatbot interface...")

class CustomerSupportBot:
    def __init__(self, model_path):
        print("Loading model...")
        self.model = AutoModelForCausalLM.from_pretrained(model_path)
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        self.chatbot = pipeline(
            "text-generation",
            model=self.model,
            tokenizer=self.tokenizer
        )
        print("✅ Chatbot ready!")

    def answer_question(self, question):
        """Answer a customer support question"""
        prompt = f"Question: {question}\nAnswer:"

        response = self.chatbot(
            prompt,
            max_new_tokens=150,
            temperature=0.7,
            do_sample=True,
            top_p=0.9
        )

        answer = response[0]['generated_text'].split("Answer:")[1].strip()
        return answer

    def chat(self):
        """Interactive chat interface"""
        print()
        print("=" * 60)
        print("Customer Support Chatbot")
        print("Type 'quit' to exit")
        print("=" * 60)
        print()

        while True:
            question = input("You: ")

            if question.lower() in ['quit', 'exit', 'q']:
                print("Goodbye!")
                break

            if not question.strip():
                continue

            answer = self.answer_question(question)
            print(f"Bot: {answer}")
            print()

# Step 4: Launch chatbot
print("Step 4: Launching chatbot...")
print()

bot = CustomerSupportBot(model_output_dir)
bot.chat()

# Alternative: Create a simple API
print()
print("=" * 60)
print("To deploy as an API, save this code:")
print("=" * 60)
print("""
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()
bot = CustomerSupportBot('./models/customer-support-bot')

class Question(BaseModel):
    text: str

@app.post("/ask")
async def ask_question(question: Question):
    answer = bot.answer_question(question.text)
    return {"answer": answer}

# Run with: uvicorn api:app --host 0.0.0.0 --port 8000
""")
print()

print("✅ Example complete!")
print()
print("Next steps:")
print("  1. Add more training examples (100+ recommended)")
print("  2. Fine-tune for more steps")
print("  3. Deploy as web service or API")
print("  4. Monitor and improve based on user feedback")
