# 🚀 UltraScale Benchboard

Interactive LLM benchmark comparison tool for ML engineers to design, run, and compare training runs across GPUs, TPUs, and other accelerators.

## 📋 Overview

UltraScale Benchboard helps ML engineers:
- Compare hardware (NVIDIA GPUs, Google TPUs, AWS Trainium/Inferentia)
- Design benchmark scenarios with model configs and parallelism strategies
- Estimate performance metrics (MFU, tokens/sec, cost)
- Get playbook-style guidance inspired by Hugging Face Nanotron Ultrascale
- Ask an AI assistant powered by Gemini for optimization advice

## 🏗️ Architecture

```
ultrascale-benchboard/
├── app/
│   ├── page.tsx           # Main dashboard page
│   ├── layout.tsx         # Root layout
│   └── globals.css        # Global styles
├── components/
│   ├── HardwarePanel.tsx  # Hardware catalog
│   ├── BenchmarkBuilder.tsx # Scenario configuration
│   ├── ResultsTable.tsx   # Comparison table
│   ├── PlaybookPanel.tsx  # Guidance sidebar
│   └── AIAssistant.tsx    # Gemini-powered chat
├── lib/
│   ├── types.ts           # TypeScript interfaces
│   └── estimator.ts       # Performance estimation logic
├── data/
│   ├── hardware.ts        # Default hardware profiles
│   ├── examples.ts        # Example scenarios
│   └── playbook.ts        # Guidance content
└── package.json
```

## 🚀 Getting Started

### Prerequisites

- Node.js 18+ and npm
- (Optional) Gemini API key for AI assistant

### Installation

```bash
cd /home/user/LightOS/ultrascale-benchboard

# Install dependencies
npm install

# Run development server
npm run dev

# Visit http://localhost:3001
```

### Production Build

```bash
npm run build
npm start
```

## 🎯 Key Features

### 1. Hardware Catalog (Left Panel)

Pre-loaded profiles for:
- **NVIDIA GPUs:** A100 80GB, H100 80GB, V100 32GB
- **Google TPUs:** v4, v5p (Trillium), v5e (Ironwood)
- **AWS:** Trainium, Inferentia2

Each profile includes:
- Compute specs (TFLOPS, SM count)
- Memory (HBM bandwidth, VRAM size)
- Interconnect (NVLink, ICI, EFA)
- Cost per hour
- Framework support

### 2. Benchmark Scenario Builder (Center)

Configure:
- **Model:** Parameters, architecture (dense/MoE), context length, precision
- **Parallelism:** Data/Tensor/Pipeline parallel degrees, gradient accumulation, activation checkpointing
- **Workload:** Training vs inference, batch sizes, target metrics

### 3. Results & Comparison

Automatic estimation of:
- **Performance:** Tokens/sec, MFU (Model FLOPs Utilization), step time
- **Memory:** Model, activation, optimizer memory breakdown
- **Cost:** Per million tokens, per hour
- **Communication:** AllReduce time, overhead percentage
- **Bottleneck Analysis:** Compute, memory bandwidth, network, or balanced

### 4. Playbook Guidance (Right Panel)

Context-aware guidance on:
- Data/Tensor/Pipeline parallelism strategies
- Memory optimization (activation checkpointing, mixed precision)
- Hardware-specific best practices (NVLink for GPUs, ICI for TPUs)
- Communication-compute overlap
- Achieving high MFU (50-60% target)
- 3D parallelism for 100B+ models

### 5. AI Assistant (Gemini-powered)

Chat interface that:
- Takes current benchmark config as context
- Answers questions like "How can I increase MFU on TPU v5p?"
- Provides optimization suggestions
- Uses multi-accelerator best practices

## 📊 Example Scenarios

Pre-loaded examples:
1. **LLaMA 7B Training** - DP=8, standard config
2. **LLaMA 70B Training** - 3D parallelism (DP=16, TP=4, PP=2)
3. **Mixtral 8x7B (MoE) Training** - Expert parallelism

## 🧮 Estimation Logic

### FLOPs Calculation
Based on Nanotron/Megatron-LM formula:
```
FLOPs ≈ 6 * params * tokens + 12 * layers * hidden_size² * tokens
```

### Memory Model
```
Total = Model + Gradients + Optimizer States + Activations
Model = params * bytes_per_param / TP
Optimizer = Model * 2 (for Adam)
Activations = batch * seq * hidden * layers * 12 / √layers (with checkpointing)
```

### MFU (Model FLOPs Utilization)
```
MFU = Achieved TFLOPS / Theoretical TFLOPS
Target: 40-50% (GPUs), 55-65% (TPUs)
```

### Communication Time
```
AllReduce = (2 * model_size * (DP-1) / DP) / bandwidth
```

## 🎨 UI/UX

- **Modern dark theme** with gradient backgrounds
- **Responsive layout** with 12-column grid
- **Real-time updates** as you change configurations
- **Sortable comparison table**
- **Visual indicators** for bottlenecks and warnings
- **Collapsible panels** for dense information
- **Keyboard shortcuts** (planned)

## 🔧 Tech Stack

- **Framework:** Next.js 14 (React 18)
- **Language:** TypeScript
- **Styling:** Tailwind CSS
- **Charts:** Recharts (for performance visualizations)
- **Icons:** Lucide React
- **AI:** Google Generative AI SDK (Gemini)

## 🚧 Current Status

**✅ Implemented:**
- Core type system
- Hardware catalog with 8 accelerators
- Estimation logic (FLOPs, memory, MFU, cost)
- Playbook guidance (10 best practices)
- Example scenarios (3 configs)
- Main layout structure
- Hardware panel component

**🚧 In Progress:**
- BenchmarkBuilder component
- ResultsTable component
- PlaybookPanel component
- AIAssistant component
- Charts and visualizations

**📅 Planned:**
- Export/import scenarios (JSON)
- Historical comparison
- Real benchmark integration (Kubernetes, Slurm)
- Custom hardware profiles UI
- Advanced filters and search
- Batch scenario comparison
- PDF report generation

## 🧪 Testing

To test the estimator logic:

```typescript
import { estimateBenchmark } from './lib/estimator';
import { defaultHardwareProfiles } from './data/hardware';
import { exampleScenarios } from './data/examples';

const scenario = exampleScenarios[0];
const hardware = defaultHardwareProfiles[0];

const result = estimateBenchmark(
  scenario.id,
  scenario.model,
  scenario.parallelism,
  scenario.workload,
  hardware
);

console.log(result);
// { tokensPerSecond: 12500, mfu: 0.42, costPerMillionTokens: 0.45, ... }
```

## 📚 References

- **Nanotron Ultrascale Playbook:** https://huggingface.co/spaces/nanotron/ultrascale-playbook
- **Megatron-LM:** NVIDIA's 3D parallelism implementation
- **JAX/Flax:** Google's TPU-optimized training
- **PaLM Paper:** Scaling Language Modeling with Pathways

## 🤝 Future Integration Points

The app is designed to plug into real backends:

```typescript
// Future: Run actual benchmarks
async function launchBenchmark(scenario: BenchmarkScenario, hardware: HardwareProfile) {
  // Submit to Kubernetes/Slurm
  const job = await k8sClient.submitJob({
    image: 'nvcr.io/nvidia/pytorch:24.01-py3',
    command: `torchrun --nproc_per_node=${hardware.gpuCount} train.py`,
    resources: { gpu: hardware.gpuCount }
  });

  return job.id;
}

// Future: Ingest real metrics
function ingestRealBenchmark(run: BenchmarkRun) {
  // Parse logs, extract metrics
  const metrics = parseTensorboardLogs(run.logs);
  return {
    actualTokensPerSecond: metrics.throughput,
    actualMfu: metrics.mfu,
    actualMemoryUsageGB: metrics.peak_memory
  };
}
```

## 🎯 Design Philosophy

1. **Playbook-first:** UI mirrors Nanotron's mental model (forward/backward/optimizer steps, 3D parallelism)
2. **Realistic estimates:** Use industry-standard formulas, not toy calculations
3. **Extensible:** Clean separation between UI and estimation logic
4. **Educational:** Teach best practices through playbook guidance
5. **Production-ready:** Structure scenarios as if running real jobs

## 💡 Usage Tips

### For Small Models (<7B params)
- Use high data parallelism (DP=16+)
- Avoid tensor parallelism (TP=1)
- Maximize batch size for MFU
- Choose: A100 or TPU v4 for cost

### For Medium Models (7B-70B params)
- Combine DP + TP (e.g., DP=8, TP=4)
- Enable activation checkpointing
- Use H100 or TPU v5p for speed
- Target: 45-55% MFU

### For Large Models (70B+ params)
- Use 3D parallelism (DP + TP + PP)
- Always enable activation checkpointing
- Use sequence parallelism for long contexts
- H100 with 900 GB/s NVLink recommended
- Target: 40-50% MFU

## 📄 License

MIT

## 🚀 Next Steps

To complete the application:

1. **Finish remaining components** (see status above)
2. **Add Gemini API key** for AI assistant
3. **Test estimation accuracy** against real benchmarks
4. **Deploy to Vercel/Netlify** for sharing
5. **Add export/import** for scenarios
6. **Integrate with real runners** (Kubernetes, Slurm)

---

**Built with ⚡ by LightOS Team**

**Inspired by:** Hugging Face Nanotron Ultrascale Playbook
