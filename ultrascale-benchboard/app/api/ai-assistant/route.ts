import { NextRequest, NextResponse } from 'next/server';
import { GoogleGenerativeAI } from '@google/generative-ai';

export async function POST(request: NextRequest) {
  try {
    const { message, context } = await request.json();

    const apiKey = process.env.GEMINI_API_KEY;
    if (!apiKey) {
      return NextResponse.json(
        { error: 'GEMINI_API_KEY not configured' },
        { status: 500 }
      );
    }

    const genAI = new GoogleGenerativeAI(apiKey);
    const model = genAI.getGenerativeModel({ model: 'gemini-pro' });

    // Build context-aware prompt
    const contextPrompt = `You are an AI assistant helping optimize large language model training configurations for the UltraScale Benchboard tool.

Current Configuration:
- Model: ${context.scenario.model.name} (${context.scenario.model.parameters}B parameters)
- Architecture: ${context.scenario.model.architectureType}
- Precision: ${context.scenario.model.precision}
- Context Length: ${context.scenario.model.contextLength}
- Parallelism: Data Parallel=${context.scenario.parallelism.dataParallel}, Tensor Parallel=${context.scenario.parallelism.tensorParallel}, Pipeline Parallel=${context.scenario.parallelism.pipelineParallel}
- Activation Checkpointing: ${context.scenario.parallelism.activationCheckpointing ? 'Enabled' : 'Disabled'}
- Sequence Parallel: ${context.scenario.parallelism.sequenceParallel ? 'Enabled' : 'Disabled'}
- Gradient Accumulation Steps: ${context.scenario.parallelism.gradientAccumulationSteps}
- Workload: ${context.scenario.workload.type}
- Batch Size: ${context.scenario.workload.batchSize} (Micro-batch: ${context.scenario.workload.microBatchSize})

Benchmark Results:
${context.results.map((r: any) => `- ${r.hardware}: ${r.tokensPerSecond.toLocaleString()} tokens/sec, MFU: ${(r.mfu * 100).toFixed(1)}%, Cost: $${r.cost.toFixed(2)}/M tokens, Bottleneck: ${r.bottleneck}`).join('\n')}

User Question: ${message}

Provide specific, actionable advice based on industry best practices from Nanotron, Megatron-LM, and other state-of-the-art LLM training frameworks. Focus on:
1. Concrete configuration changes with numbers
2. Hardware-specific optimizations
3. Trade-offs between throughput, cost, and memory
4. Realistic MFU targets (40-50% for GPUs, 55-65% for TPUs)

Keep responses concise and practical.`;

    const result = await model.generateContent(contextPrompt);
    const response = result.response.text();

    return NextResponse.json({ response });
  } catch (error) {
    console.error('Gemini API error:', error);
    return NextResponse.json(
      { error: 'Failed to generate AI response' },
      { status: 500 }
    );
  }
}
