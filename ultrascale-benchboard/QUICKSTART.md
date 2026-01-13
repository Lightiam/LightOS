# 🚀 UltraScale Benchboard - Quick Start

Get your benchmark comparison tool running in 3 minutes!

## Prerequisites

- Node.js 18+ and npm
- (Optional) Google Gemini API key for AI assistant

## Installation & Setup

### 1. Navigate to the project directory

```bash
cd /home/user/LightOS/ultrascale-benchboard
```

### 2. Install dependencies

```bash
npm install
```

This will install:
- Next.js 14
- React 18
- TypeScript
- Tailwind CSS
- Recharts (for visualizations)
- Lucide React (for icons)
- Google Generative AI SDK (for Gemini)

### 3. (Optional) Configure AI Assistant

If you want to use the AI assistant feature:

```bash
# Copy the example environment file
cp .env.local.example .env.local

# Edit .env.local and add your Gemini API key
# Get your API key from: https://makersuite.google.com/app/apikey
```

Example `.env.local`:
```
GEMINI_API_KEY=AIzaSyC...your_actual_key_here
```

### 4. Start the development server

```bash
npm run dev
```

The app will start on **http://localhost:3001**

## First Steps

1. **Select Hardware** (Left Panel)
   - Click on hardware profiles to select them for comparison
   - Try selecting: H100, A100, and TPU v5p

2. **Configure Scenario** (Center Panel - Top)
   - Adjust model parameters (size, context length, precision)
   - Set parallelism strategy (DP, TP, PP)
   - Configure batch sizes
   - Or load an example scenario from the dropdown

3. **View Results** (Center Panel - Bottom)
   - See real-time performance estimates
   - Compare tokens/sec, MFU, cost, and memory
   - Click column headers to sort
   - Identify bottlenecks

4. **Read Playbook** (Right Panel)
   - Browse best practices by category
   - Click guidance cards to expand
   - See context-aware tips for your config

5. **Ask AI Assistant** (Top Right Button)
   - Click "AI Assistant" to open chat
   - Ask optimization questions
   - Get recommendations based on your scenario

## Example Scenarios

Try these pre-loaded examples:

1. **LLaMA 7B Training**
   - Standard DP=8 configuration
   - Good for learning basics

2. **LLaMA 70B Training (3D Parallelism)**
   - Complex DP=16, TP=4, PP=2 setup
   - Shows advanced parallelism strategies

3. **Mixtral 8x7B (MoE) Training**
   - Mixture of Experts architecture
   - Demonstrates expert parallelism

## Common Questions

### Q: The AI assistant says "unauthorized" or fails
**A:** You need to configure your Gemini API key in `.env.local`. Get a free key from https://makersuite.google.com/app/apikey

### Q: Can I add custom hardware profiles?
**A:** Yes! Click "Add Custom Profile" in the hardware panel (UI coming soon). For now, edit `data/hardware.ts` to add new profiles.

### Q: Are the estimates accurate?
**A:** The estimates use industry-standard formulas from Nanotron and Megatron-LM. They're realistic but simplified. For production planning, always validate with real benchmarks.

### Q: Can I export my scenarios?
**A:** Export/import feature is planned. For now, you can copy the scenario configuration from the browser console.

### Q: How do I deploy to production?
**A:** Build and start:
```bash
npm run build
npm start
```

Or deploy to Vercel/Netlify:
```bash
# Vercel
vercel

# Netlify
netlify deploy --prod
```

## Understanding the Results

### Tokens/Second
Higher is better. This is your raw throughput.

### MFU (Model FLOPs Utilization)
Efficiency metric. Target:
- GPUs (H100/A100): 40-50%
- TPUs (v5p): 55-65%

### Cost per Million Tokens
Lower is better. Includes hardware cost but not power/cooling.

### Memory (GB)
Total memory per accelerator including model, gradients, optimizer, and activations.

### Bottleneck
- **Compute Bound**: Limited by GPU/TPU compute (good!)
- **Memory BW Bound**: Limited by HBM bandwidth (increase batch size)
- **Network Bound**: Limited by interconnect (reduce TP, increase DP)
- **Balanced**: All resources well-utilized (ideal!)

## Tips for Optimization

1. **Low MFU (<40%)**
   - Increase batch size
   - Enable mixed precision (bf16)
   - Reduce tensor parallelism

2. **Out of Memory**
   - Enable activation checkpointing
   - Reduce batch size
   - Increase pipeline parallelism
   - Lower precision (fp16 → int8)

3. **High Cost**
   - Use cheaper accelerators (A100 instead of H100)
   - Increase batch size for better utilization
   - Enable spot instances (not shown in tool)

4. **Network Bottleneck**
   - Reduce TP (tensor parallelism)
   - Use NVLink-connected GPUs for TP
   - Increase DP across nodes

## Project Structure

```
ultrascale-benchboard/
├── app/                    # Next.js app directory
│   ├── page.tsx           # Main dashboard
│   ├── layout.tsx         # Root layout
│   └── api/               # API routes
│       └── ai-assistant/  # Gemini integration
├── components/            # React components
│   ├── HardwarePanel.tsx
│   ├── BenchmarkBuilder.tsx
│   ├── ResultsTable.tsx
│   ├── PlaybookPanel.tsx
│   └── AIAssistant.tsx
├── lib/                   # Core logic
│   ├── types.ts          # TypeScript types
│   └── estimator.ts      # Performance calculations
├── data/                  # Static data
│   ├── hardware.ts       # Hardware profiles
│   ├── examples.ts       # Example scenarios
│   └── playbook.ts       # Best practices
└── package.json          # Dependencies
```

## Next Steps

1. **Explore the hardware catalog** - Compare different accelerators
2. **Try example scenarios** - Learn different parallelism strategies
3. **Read the playbook** - Understand optimization techniques
4. **Experiment with configs** - Find the best setup for your use case
5. **Ask the AI assistant** - Get personalized recommendations

## Getting Help

- Check `README.md` for detailed documentation
- Review `data/playbook.ts` for best practices
- Read the code in `lib/estimator.ts` to understand calculations
- Ask the AI assistant in the app

## References

- **Nanotron Ultrascale Playbook**: https://huggingface.co/spaces/nanotron/ultrascale-playbook
- **Megatron-LM**: https://github.com/NVIDIA/Megatron-LM
- **JAX/Flax**: https://github.com/google/jax
- **PaLM Paper**: https://arxiv.org/abs/2204.02311

---

**Built with ⚡ by LightOS Team**

**Happy Benchmarking! 🚀**
