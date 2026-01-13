'use client';

import { useState, useRef, useEffect } from 'react';
import { BenchmarkScenario, BenchmarkResult } from '../lib/types';
import { MessageSquare, Send, X, Sparkles, Loader2 } from 'lucide-react';

interface Message {
  role: 'user' | 'assistant';
  content: string;
}

interface Props {
  scenario: BenchmarkScenario;
  results: BenchmarkResult[];
  onClose: () => void;
}

export default function AIAssistant({ scenario, results, onClose }: Props) {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: 'assistant',
      content: `Hello! I'm your AI assistant powered by Gemini. I can help you optimize your benchmark configuration.\n\nI can see you're working with:\n• Model: ${scenario.model.name} (${scenario.model.parameters}B params)\n• Parallelism: DP=${scenario.parallelism.dataParallel}, TP=${scenario.parallelism.tensorParallel}, PP=${scenario.parallelism.pipelineParallel}\n• Batch Size: ${scenario.workload.batchSize}\n\nHow can I help you optimize this configuration?`
    }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMessage = input.trim();
    setInput('');
    setMessages(prev => [...prev, { role: 'user', content: userMessage }]);
    setIsLoading(true);

    try {
      // Build context for the AI
      const context = {
        scenario,
        results: results.map(r => ({
          hardware: r.hardwareId,
          tokensPerSecond: r.tokensPerSecond,
          mfu: r.mfu,
          cost: r.costPerMillionTokens,
          bottleneck: r.bottleneck
        }))
      };

      // Call Gemini API
      const response = await fetch('/api/ai-assistant', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: userMessage,
          context
        })
      });

      if (!response.ok) {
        throw new Error('Failed to get AI response');
      }

      const data = await response.json();
      setMessages(prev => [...prev, { role: 'assistant', content: data.response }]);
    } catch (error) {
      console.error('AI Assistant error:', error);
      setMessages(prev => [
        ...prev,
        {
          role: 'assistant',
          content: "I'm sorry, I encountered an error. Please make sure the Gemini API key is configured in your environment variables (.env.local with GEMINI_API_KEY).\n\nIn the meantime, here are some general optimization tips:\n\n1. **Increase MFU**: Try increasing batch size or enabling mixed precision (bf16/fp16)\n2. **Reduce Memory**: Enable activation checkpointing or increase pipeline parallelism\n3. **Reduce Communication**: Lower tensor parallelism or increase data parallelism\n4. **Balance Workload**: Ensure DP × TP × PP matches your total GPU/TPU count"
        }
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const exampleQuestions = [
    "How can I increase MFU for this configuration?",
    "What's the best parallelism strategy for this model?",
    "How do I reduce training cost?",
    "Should I use activation checkpointing?"
  ];

  return (
    <div className="bg-slate-800 border border-slate-700 rounded-xl shadow-2xl flex flex-col h-[600px]">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-slate-700">
        <div className="flex items-center space-x-2">
          <div className="p-2 bg-gradient-to-br from-purple-500 to-pink-600 rounded-lg">
            <Sparkles className="w-5 h-5 text-white" />
          </div>
          <div>
            <h3 className="text-lg font-semibold text-slate-200">AI Assistant</h3>
            <p className="text-xs text-slate-400">Powered by Gemini</p>
          </div>
        </div>
        <button
          onClick={onClose}
          className="p-2 hover:bg-slate-700 rounded-lg transition-colors"
        >
          <X className="w-5 h-5 text-slate-400" />
        </button>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((message, index) => (
          <div
            key={index}
            className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-[80%] rounded-lg p-3 ${
                message.role === 'user'
                  ? 'bg-blue-500/20 border border-blue-500/50 text-slate-200'
                  : 'bg-slate-700/50 border border-slate-600 text-slate-300'
              }`}
            >
              <div className="text-sm whitespace-pre-line">{message.content}</div>
            </div>
          </div>
        ))}

        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-slate-700/50 border border-slate-600 rounded-lg p-3">
              <div className="flex items-center space-x-2">
                <Loader2 className="w-4 h-4 text-blue-400 animate-spin" />
                <span className="text-sm text-slate-400">Thinking...</span>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Example Questions */}
      {messages.length === 1 && !isLoading && (
        <div className="px-4 pb-2">
          <div className="text-xs text-slate-400 mb-2">Try asking:</div>
          <div className="flex flex-wrap gap-2">
            {exampleQuestions.map((question, index) => (
              <button
                key={index}
                onClick={() => setInput(question)}
                className="text-xs px-3 py-1.5 bg-slate-700/50 hover:bg-slate-700 border border-slate-600 rounded-lg text-slate-300 transition-colors"
              >
                {question}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Input */}
      <form onSubmit={handleSubmit} className="p-4 border-t border-slate-700">
        <div className="flex space-x-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask about optimization, parallelism, hardware selection..."
            className="flex-1 px-4 py-2 bg-slate-700/50 border border-slate-600 rounded-lg text-sm text-slate-200 placeholder-slate-500 focus:outline-none focus:border-blue-500"
            disabled={isLoading}
          />
          <button
            type="submit"
            disabled={!input.trim() || isLoading}
            className="px-4 py-2 bg-blue-500 hover:bg-blue-600 disabled:bg-slate-700 disabled:text-slate-500 rounded-lg text-white transition-colors flex items-center space-x-2"
          >
            <Send className="w-4 h-4" />
          </button>
        </div>
      </form>
    </div>
  );
}
