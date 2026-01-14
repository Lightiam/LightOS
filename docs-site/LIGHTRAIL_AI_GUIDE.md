# 🚄 LightRail AI - Workload Orchestration Platform

> Intelligent AI workload orchestration with automated GPU scheduling, cost optimization, and workflow management.

## Overview

LightRail AI is an advanced orchestration platform that sits on top of your GPU compute infrastructure (like the Shadeform marketplace) and provides intelligent workload management, automated scheduling, and cost optimization for AI/ML workloads.

## Key Features

### 🔄 Workflow Builder
- **Visual Pipeline Designer**: Drag-and-drop interface for building AI pipelines
- **5-Stage Rail Track**: Data Ingestion → Training → Validation → Deployment → Monitoring
- **Reusable Templates**: Save and share workflow configurations
- **Multi-step Automation**: Chain multiple AI tasks together

### 📊 Active Workload Management
- **Real-time Monitoring**: Track all running jobs with live metrics
- **GPU Allocation Tracking**: See which GPUs are assigned to which workloads
- **Progress Visualization**: Animated progress bars with shimmer effects
- **Performance Metrics**: Throughput, cost, runtime, and utilization per job

### 🎮 GPU Resource Pool
- **Unified GPU Dashboard**: Manage all your GPUs from one interface
- **Multi-vendor Support**: NVIDIA (H100, A100, RTX6000), AMD, TPU
- **Real-time Utilization**: Live GPU metrics with animated bars
- **Status Indicators**: Glowing dots show available/allocated/error states
- **Auto-discovery**: Automatically detects new GPUs added to the pool

### ⚙️ Orchestration Rules Engine
- **Auto-scaling**: Scale up when queue depth exceeds threshold
- **Cost Optimization**: Migrate low-utilization jobs to spot instances
- **Preemptive Checkpointing**: Save state before spot interruptions
- **Priority Scheduling**: Deadline-aware job prioritization
- **Health Monitoring**: Auto-evacuate workloads from unhealthy GPUs
- **Smart Batching**: Group similar inference jobs for efficiency

### 📈 Analytics Dashboard
- **Performance Metrics**: Total compute hours, utilization, cost savings
- **Trend Analysis**: Week-over-week comparisons with up/down indicators
- **Cost Tracking**: Real-time spend tracking and optimization savings
- **Visual Charts**: Animated bar charts for historical data
- **Export Reports**: Download analytics as CSV/PDF

## Design Theme

### Color Palette
```css
Primary:    #6366f1 (Indigo)
Secondary:  #8b5cf6 (Purple)
Accent:     #06b6d4 (Cyan)
Success:    #10b981 (Green)
Warning:    #f59e0b (Amber)
Danger:     #ef4444 (Red)
```

### Visual Style
- **Rail/Transit Metaphor**: Workflows visualized as train stations
- **Gradient Accents**: Smooth color transitions for depth
- **Glowing Effects**: Animated glows on active elements
- **Dark Theme**: Easy on eyes during long monitoring sessions
- **Smooth Animations**: Shimmer effects on progress bars, pulse on active jobs

## Integration with GPU Marketplace

LightRail AI works seamlessly with GPU marketplaces like Shadeform:

1. **GPU Discovery**: Automatically imports available GPUs from marketplace API
2. **Dynamic Provisioning**: Spins up new GPUs when workload queue grows
3. **Cost Optimization**: Switches between on-demand and spot instances
4. **Multi-provider**: Can orchestrate across Shadeform, RunPod, Lambda Labs, etc.

### Integration Flow
```
User → LightRail AI → Orchestration Rules → GPU Marketplace API → GPU Allocation
                    ↓
              Workload Scheduler
                    ↓
              Monitor & Optimize
```

## Use Cases

### 1. Large Language Model Training
```
Workflow: Data Prep → Training (8× H100) → Validation → Deployment
Duration: 8.3 days
Cost: $6,384
Auto-features: Checkpointing every 1hr, auto-scale on OOM
```

### 2. Inference Serving (Stable Diffusion)
```
Workflow: Model Load → Inference Serving (4× A100)
Throughput: 180 requests/min
Auto-features: Auto-scale on queue depth, load balancing
```

### 3. Batch Processing (Whisper Transcription)
```
Workflow: Audio Ingestion → Transcription (2× RTX6000) → Export
Files: 340 audio files
Auto-features: Smart batching, priority scheduling
```

## Orchestration Rules Examples

### Auto-Scale Rule
```javascript
IF queue_depth > 10 THEN
  scale_up(gpu_count=2, gpu_type='A100')
END
```

### Cost Optimization Rule
```javascript
IF utilization < 30% FOR 1hr THEN
  migrate_to_spot_instance()
  save_checkpoint()
END
```

### Preemptive Checkpoint Rule
```javascript
IF spot_interruption_warning THEN
  save_checkpoint()
  migrate(destination='on_demand')
END
```

### Priority Scheduling Rule
```javascript
PRIORITIZE jobs WHERE
  priority='high' AND
  deadline < 24hrs
ORDER BY deadline ASC
```

## API Integration

### Start a Workflow
```bash
curl -X POST https://lightrail.ai/api/workflows \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "name": "llama-70b-training",
    "steps": [
      {"type": "data_prep", "dataset": "s3://my-bucket/data"},
      {"type": "training", "gpus": 8, "gpu_type": "H100"},
      {"type": "validation", "metric": "accuracy"}
    ],
    "rules": ["auto-scale", "checkpoint-1hr"]
  }'
```

### Monitor Workload
```bash
curl https://lightrail.ai/api/workloads/llama-70b-training \
  -H "Authorization: Bearer $TOKEN"
```

### Get GPU Pool Status
```bash
curl https://lightrail.ai/api/gpu-pool \
  -H "Authorization: Bearer $TOKEN"
```

## Tech Stack

### Frontend
- **HTML5** with semantic markup
- **CSS3** with custom properties and animations
- **Vanilla JavaScript** for interactivity (no framework dependencies)

### Design Principles
- **Mobile-responsive**: Works on all screen sizes
- **Accessible**: WCAG 2.1 AA compliant
- **Performance**: < 100ms page load, 60fps animations
- **Progressive Enhancement**: Works without JS for basic functionality

## Comparison with Other Tools

| Feature | LightRail AI | Kubernetes | Ray | Slurm |
|---------|-------------|------------|-----|-------|
| Visual Workflow Builder | ✅ | ❌ | ❌ | ❌ |
| GPU Orchestration | ✅ | 🟡 | ✅ | ✅ |
| Cost Optimization | ✅ | ❌ | 🟡 | ❌ |
| Multi-provider Support | ✅ | 🟡 | ❌ | ❌ |
| Real-time Analytics | ✅ | 🟡 | ✅ | ❌ |
| No Setup Required | ✅ | ❌ | ❌ | ❌ |

## Roadmap

### Q1 2026
- [ ] Add Jupyter notebook integration
- [ ] Support for custom metrics
- [ ] Slack/Discord notifications
- [ ] Cost budget alerts

### Q2 2026
- [ ] Multi-tenancy support
- [ ] Advanced scheduling policies
- [ ] Integration with MLflow/W&B
- [ ] GPU power capping controls

### Q3 2026
- [ ] Predictive scaling with ML
- [ ] Carbon-aware scheduling
- [ ] Multi-region orchestration
- [ ] Custom rule DSL editor

## Getting Started

1. **Open the Interface**
   ```bash
   # If running locally
   open docs-site/lightrail-orchestration.html

   # Or deploy to web server
   cp lightrail-orchestration.html /var/www/html/
   ```

2. **Connect GPU Pool**
   - Click "Add GPUs" in the GPU Pool tab
   - Enter your GPU marketplace API credentials
   - Auto-discover will find available GPUs

3. **Create Your First Workflow**
   - Click "New Workflow" button
   - Select pipeline stages
   - Configure GPU requirements
   - Add orchestration rules
   - Launch!

4. **Monitor and Optimize**
   - View active workloads in real-time
   - Check analytics for cost optimization opportunities
   - Adjust rules based on usage patterns

## Support

- **Documentation**: https://github.com/Lightiam/LightOS/tree/main/docs-site
- **Issues**: https://github.com/Lightiam/LightOS/issues
- **Email**: support@lightos.ai

## License

MIT License - See LICENSE file for details

---

**Built with ⚡ by the LightOS Team**

*Inspired by modern AI orchestration needs and the simplicity of rail transportation systems.*
