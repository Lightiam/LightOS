
import React, { useState, useRef, useEffect } from 'react';
import { GoogleGenAI } from "@google/genai";
import { Sparkles, Send, X, Bot, User, Loader2, BrainCircuit, Terminal } from 'lucide-react';
import { INITIAL_PROVIDERS, INITIAL_JOBS, INITIAL_SITES } from '../services/mockData';

const AIAssistant: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<{ role: 'user' | 'assistant', content: string }[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, isLoading]);

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage = input.trim();
    setInput('');
    setMessages(prev => [...prev, { role: 'user', content: userMessage }]);
    setIsLoading(true);

    try {
      // Create a new GoogleGenAI instance right before making an API call to ensure current key is used
      const ai = new GoogleGenAI({ apiKey: process.env.API_KEY });
      
      // Construct context for the AI
      const context = {
        providers: INITIAL_PROVIDERS,
        jobs: INITIAL_JOBS,
        sites: INITIAL_SITES,
        systemStatus: "US-West Fabric Operational, PUE 1.12 avg"
      };

      // Correctly call generateContent with model name and prompt string as per guidelines
      const response = await ai.models.generateContent({
        model: 'gemini-3-pro-preview',
        contents: `
              Context about current fleet: ${JSON.stringify(context)}
              
              User query: ${userMessage}
            `,
        config: {
          systemInstruction: `You are the Aurora AI Strategist, a world-class expert in GPU/TPU orchestration, data center efficiency, and multi-cloud AI infrastructure. 
          Use your deep reasoning capabilities to provide precise, technical, and actionable advice. 
          Focus on:
          - Cost optimization across AWS, GCP, Azure, and LightRail native fabric.
          - Hardware efficiency (PUE, thermal management).
          - Workload scheduling for LLM training and inference.
          Always maintain the persona of a high-performance system assistant. Use markdown for lists and code blocks.`,
          thinkingConfig: { thinkingBudget: 32768 }
        },
      });

      // Extract generated text from the response using the .text property
      const aiResponse = response.text || "I'm sorry, I couldn't process that request.";
      setMessages(prev => [...prev, { role: 'assistant', content: aiResponse }]);
    } catch (error) {
      console.error("AI Error:", error);
      setMessages(prev => [...prev, { role: 'assistant', content: "Error: Failed to connect to the Aurora intelligence fabric. Please check your API configuration." }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <>
      {/* Floating Toggle Button */}
      <button 
        onClick={() => setIsOpen(!isOpen)}
        className={`fixed bottom-8 right-8 z-50 p-4 rounded-2xl shadow-2xl transition-all duration-300 hover:scale-110 active:scale-95 flex items-center gap-2 border ${
          isOpen 
            ? 'bg-slate-900 border-slate-700 text-slate-400' 
            : 'aurora-gradient text-black border-white/20'
        }`}
      >
        {isOpen ? <X className="w-6 h-6" /> : <BrainCircuit className="w-6 h-6" />}
        {!isOpen && <span className="font-bold text-sm pr-2">Aurora Intelligence</span>}
      </button>

      {/* Chat Window */}
      <div className={`fixed bottom-24 right-8 z-50 w-[450px] max-h-[700px] h-[80vh] glass-panel rounded-3xl flex flex-col shadow-2xl border-slate-700/50 transition-all duration-500 origin-bottom-right ${
        isOpen ? 'scale-100 opacity-100' : 'scale-0 opacity-0 pointer-events-none'
      }`}>
        {/* Header */}
        <div className="p-6 border-b border-slate-800 flex items-center justify-between bg-slate-900/50 rounded-t-3xl">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-green-500/10 border border-green-500/20 flex items-center justify-center">
              <Sparkles className="w-6 h-6 text-[#00FF41]" />
            </div>
            <div>
              <h3 className="font-bold text-white tracking-tight">Aurora Strategist</h3>
              <div className="flex items-center gap-2">
                <span className="w-1.5 h-1.5 rounded-full bg-green-500 animate-pulse"></span>
                <span className="text-[10px] text-slate-500 font-bold uppercase tracking-widest">Thinking Mode Active</span>
              </div>
            </div>
          </div>
          <div className="p-1.5 rounded-lg bg-slate-800/50 text-slate-500 border border-slate-700">
            <Terminal className="w-4 h-4" />
          </div>
        </div>

        {/* Messages */}
        <div 
          ref={scrollRef}
          className="flex-1 overflow-y-auto p-6 space-y-6 scrollbar-hide"
        >
          {messages.length === 0 && (
            <div className="h-full flex flex-col items-center justify-center text-center space-y-4 opacity-50">
              <div className="w-16 h-16 rounded-full bg-slate-800 flex items-center justify-center">
                <Bot className="w-8 h-8 text-slate-500" />
              </div>
              <div>
                <p className="text-sm font-bold text-slate-300">Deep Reasoning Hub</p>
                <p className="text-xs text-slate-500 max-w-[200px] mt-1">Ask complex questions about fleet optimization or cost projections.</p>
              </div>
            </div>
          )}
          
          {messages.map((msg, i) => (
            <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
              <div className={`max-w-[85%] rounded-2xl p-4 text-sm leading-relaxed ${
                msg.role === 'user' 
                  ? 'bg-slate-800 border border-slate-700 text-white' 
                  : 'bg-slate-950/50 border border-slate-800 text-slate-300'
              }`}>
                <div className="flex items-center gap-2 mb-2 opacity-50">
                  {msg.role === 'user' ? <User className="w-3 h-3" /> : <Bot className="w-3 h-3" />}
                  <span className="text-[10px] font-bold uppercase tracking-tighter">{msg.role}</span>
                </div>
                <div className="whitespace-pre-wrap">
                  {msg.content}
                </div>
              </div>
            </div>
          ))}

          {isLoading && (
            <div className="flex justify-start">
              <div className="bg-slate-950/50 border border-slate-800 rounded-2xl p-4 flex items-center gap-3">
                <Loader2 className="w-4 h-4 text-[#00FF41] animate-spin" />
                <span className="text-[10px] font-bold text-slate-500 uppercase tracking-widest animate-pulse">Strategist is thinking...</span>
              </div>
            </div>
          )}
        </div>

        {/* Input */}
        <div className="p-6 border-t border-slate-800 bg-slate-900/30 rounded-b-3xl">
          <div className="flex items-center gap-3 bg-slate-800/50 p-1.5 rounded-2xl border border-slate-700 focus-within:border-[#00FF41]/50 transition-all shadow-inner">
            <input 
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSend()}
              placeholder="Ask for optimization strategies..."
              className="flex-1 bg-transparent border-none outline-none px-4 text-sm text-white placeholder:text-slate-600"
            />
            <button 
              onClick={handleSend}
              disabled={isLoading || !input.trim()}
              className="p-2.5 rounded-xl aurora-gradient text-black transition-all hover:scale-105 active:scale-95 disabled:opacity-30 disabled:grayscale disabled:scale-100"
            >
              <Send className="w-4 h-4" />
            </button>
          </div>
          <p className="text-[9px] text-slate-600 mt-3 text-center uppercase font-bold tracking-widest">Gemini 3 Pro Intelligence • Deep Reasoning Enabled</p>
        </div>
      </div>
    </>
  );
};

export default AIAssistant;
