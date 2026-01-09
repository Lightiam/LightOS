# Lovable Prompt: LLM Dev Tools - Complete Development Environment

## Project Overview
Create a comprehensive web application called "LLM Dev Tools" that provides an intuitive interface for AI-powered development tasks including fast LLM fine-tuning, code generation, and code analysis. This should be a production-ready tool similar to enterprise AI development platforms.

---

## Core Features Required

### 1. Main Navigation Menu: "LLM Dev Tools"

Create a main navigation section with three primary tools:

#### A. **Unsloth Fast Fine-Tuning** (⚡ 2-5x faster)
- Quick fine-tune interface for LLM models
- Support for: Llama 3.1, Mistral 7B, Qwen 2.5, GLM-4, Gemma
- Custom dataset upload (JSON/JSONL format)
- Real-time training progress
- Model export functionality

#### B. **GLM-4 Coding Agent** (🤖 71.8% HumanEval)
- Code generation from natural language
- Code explanation and documentation
- Bug detection and fixing
- Code refactoring suggestions
- Multi-language support (40+ languages)

#### C. **Qwen2.5-Coder** (🏆 74.5% HumanEval - Beats GPT-4)
- Advanced code generation
- Code completion
- Function generation
- Test generation (pytest, unittest)
- Debug assistance

---

## Detailed Component Structure

### Page 1: Dashboard / Home
**Layout:**
- Hero section with tagline: "Train Faster. Code Smarter. Build Better."
- Statistics cards:
  - "2-5x Faster Training"
  - "70% Less Memory"
  - "74.5% HumanEval Score"
  - "6+ Platforms Supported"
- Quick action cards for each tool
- Recent activity/history section
- Getting started guide

**Design:**
- Dark theme with indigo/teal accent colors
- Modern card-based layout
- Responsive grid system
- Smooth animations on hover

### Page 2: Unsloth Fine-Tuning Studio

**Components:**

1. **Model Selection Panel**
   - Dropdown with supported models:
     * Llama 3.1 8B
     * Mistral 7B v0.3
     * Qwen 2.5 7B
     * GLM-4 9B
     * Gemma 7B
   - Model info cards showing:
     * Parameters
     * Context length
     * VRAM requirements
     * Performance metrics

2. **Dataset Upload Section**
   - Drag-and-drop file upload
   - Support for .json and .jsonl
   - Dataset validation with preview
   - Example datasets available:
     * Alpaca (instruction following)
     * Code Alpaca
     * Custom upload
   - Dataset format validator showing expected structure:
   ```json
   {
     "instruction": "Task description",
     "input": "Optional context",
     "output": "Expected result"
   }
   ```

3. **Training Configuration Panel**
   - Advanced settings (collapsible):
     * Max steps (slider: 10-1000, default: 60)
     * Learning rate (input: default 2e-4)
     * Batch size (dropdown: 1, 2, 4, 8)
     * LoRA rank (slider: 8-64, default: 16)
     * Enable 4-bit quantization (toggle)
     * Enable Flash Attention (toggle)
     * Output directory (input field)
   - Quick presets:
     * "Fast Test" (30 steps)
     * "Balanced" (100 steps)
     * "High Quality" (500 steps)

4. **Training Progress Monitor**
   - Real-time progress bar
   - Training metrics visualization:
     * Loss curve (line chart)
     * Learning rate schedule
     * GPU utilization
     * ETA countdown
   - Log output (scrollable terminal-style)
   - Pause/Resume/Stop buttons

5. **Model Export Panel**
   - Download trained model
   - Export formats: PyTorch, GGUF, ONNX
   - Share model (generate shareable link)
   - Model card generation

**API Integration:**
```typescript
interface TrainingConfig {
  modelName: string;
  datasetPath: string;
  maxSteps: number;
  learningRate: number;
  batchSize: number;
  loraRank: number;
  use4bit: boolean;
  useFlashAttention: boolean;
  outputDir: string;
}

// POST /api/training/start
// POST /api/training/stop
// GET /api/training/status/:sessionId
// GET /api/training/logs/:sessionId
```

### Page 3: GLM-4 Coding Assistant

**Components:**

1. **Action Selection**
   - Tab navigation:
     * Generate Code
     * Explain Code
     * Fix Bugs
     * Add Documentation
     * Refactor Code

2. **Generate Code Tab**
   - Large text area for natural language description
   - Language selector dropdown (Python, JavaScript, TypeScript, Go, Rust, Java, C++, etc.)
   - "Generate" button
   - Output:
     * Syntax-highlighted code editor
     * Copy button
     * Download as file
     * Run code (optional, for Python/JS)

3. **Explain Code Tab**
   - Code input editor (Monaco editor)
   - Detail level selector:
     * Beginner
     * Medium
     * Detailed
     * Expert
   - "Explain" button
   - Output:
     * Markdown-formatted explanation
     * Line-by-line breakdown
     * Complexity analysis

4. **Fix Bugs Tab**
   - Code input with line numbers
   - "Analyze" button
   - Output:
     * List of detected issues
     * Severity levels (Critical, Warning, Info)
     * Suggested fixes
     * Fixed code (side-by-side diff view)

5. **Settings Sidebar**
   - Model size: 9B (default)
   - Temperature (slider: 0-1)
   - Max tokens (input: default 2048)
   - Enable 4-bit quantization

**Features:**
- Code editor with syntax highlighting (Monaco Editor)
- Multi-language support indicator
- Copy to clipboard functionality
- Export code to file
- History of generations
- Save favorites

### Page 4: Qwen2.5-Coder Studio

**Components:**

1. **Model Size Selector**
   - Radio buttons or pills:
     * 0.5B (Lightweight)
     * 1.5B (Balanced)
     * 7B (Recommended) ⭐
     * 14B (High Quality)
     * 32B (Best Results)
   - VRAM requirements shown for each

2. **Task Selector**
   - Tab navigation:
     * Generate Function
     * Complete Code
     * Generate Tests
     * Debug Code
     * Refactor
     * Interactive Mode

3. **Generate Function Tab**
   - Input: Function description
   - Language selector
   - Optional: Signature/type hints
   - Output: Complete function with docstring

4. **Complete Code Tab**
   - Split view:
     * Left: Your partial code
     * Right: AI completions (live as you type)
   - Accept completion button
   - Multiple completion suggestions

5. **Generate Tests Tab**
   - Input: Code to test
   - Framework selector: pytest, unittest, jest, mocha
   - Output: Complete test suite
   - Coverage indicators

6. **Interactive Mode**
   - Chat-style interface
   - Conversation history
   - Code blocks in responses
   - Apply code button

**Advanced Features:**
- Real-time code completion (debounced)
- Context-aware suggestions
- Import auto-detection
- Code formatting (Prettier/Black integration)

### Page 5: Documentation Hub

**Structure:**

1. **Getting Started**
   - Installation guide
   - Quick start tutorial
   - System requirements
   - Video walkthrough

2. **User Guides**
   - Fine-tuning guide
     * Preparing datasets
     * Choosing hyperparameters
     * Best practices
     * Troubleshooting
   - Coding agents guide
     * When to use GLM-4 vs Qwen
     * Prompt engineering tips
     * Language-specific guides
   - Performance optimization
     * Memory management
     * Speed optimization
     * Multi-GPU setup

3. **API Reference**
   - Unsloth API
     * Quick fine-tune function
     * Training config options
     * Model export
   - GLM-4 API
     * Generate code
     * Explain code
     * Fix bugs
   - Qwen2.5-Coder API
     * All methods documented
     * Request/response examples
     * Error codes

4. **Examples**
   - Interactive code examples:
     * Fine-tune Llama 3.1
     * Build a chatbot
     * Generate REST API
     * Code review automation
   - Copy-paste ready snippets
   - Live demos

5. **FAQ**
   - Common questions
   - Troubleshooting
   - Performance tips
   - Pricing/limits

### Page 6: Settings & Account

**Sections:**

1. **API Configuration**
   - API key management
   - Rate limits display
   - Usage statistics

2. **Preferences**
   - Default model selections
   - Theme (dark/light)
   - Code editor settings
   - Auto-save toggle

3. **Storage**
   - Saved models
   - Training history
   - Generated code history
   - Clear data

---

## Technical Implementation Requirements

### Frontend Stack
```typescript
// Use these technologies:
- React 18+ with TypeScript
- Tailwind CSS for styling
- shadcn/ui for components
- Monaco Editor for code editing
- React Query for API calls
- Zustand for state management
- React Router for navigation
- Recharts for visualizations
```

### Key Components to Build

1. **CodeEditor Component**
```typescript
interface CodeEditorProps {
  value: string;
  onChange: (value: string) => void;
  language: string;
  readOnly?: boolean;
  height?: string;
}
```

2. **ModelSelector Component**
```typescript
interface ModelSelectorProps {
  models: Model[];
  selected: string;
  onSelect: (modelId: string) => void;
}
```

3. **TrainingProgress Component**
```typescript
interface TrainingProgressProps {
  sessionId: string;
  status: 'idle' | 'training' | 'completed' | 'error';
  progress: number;
  metrics: TrainingMetrics;
}
```

4. **DatasetUpload Component**
```typescript
interface DatasetUploadProps {
  onUpload: (file: File) => void;
  validation: ValidationResult;
}
```

### API Routes Structure

```typescript
// Backend API endpoints
POST   /api/v1/training/start
POST   /api/v1/training/stop/:sessionId
GET    /api/v1/training/status/:sessionId
GET    /api/v1/training/logs/:sessionId
POST   /api/v1/training/export/:sessionId

POST   /api/v1/code/generate
POST   /api/v1/code/explain
POST   /api/v1/code/fix
POST   /api/v1/code/refactor
POST   /api/v1/code/document

POST   /api/v1/qwen/generate
POST   /api/v1/qwen/complete
POST   /api/v1/qwen/test
POST   /api/v1/qwen/debug
```

### Data Models

```typescript
interface TrainingSession {
  id: string;
  modelName: string;
  status: TrainingStatus;
  progress: number;
  metrics: {
    loss: number[];
    learningRate: number[];
    gpuUtil: number[];
  };
  config: TrainingConfig;
  startTime: Date;
  endTime?: Date;
}

interface CodeGenerationRequest {
  prompt: string;
  language: string;
  temperature: number;
  maxTokens: number;
}

interface CodeGenerationResponse {
  code: string;
  explanation?: string;
  tokens: number;
  duration: number;
}
```

---

## UI/UX Design Guidelines

### Color Scheme
```css
/* Primary Palette */
--primary: #4F46E5; /* Indigo */
--primary-dark: #4338CA;
--secondary: #10B981; /* Emerald */
--accent: #F59E0B; /* Amber */

/* Background */
--bg-primary: #0F172A; /* Slate 900 */
--bg-secondary: #1E293B; /* Slate 800 */
--bg-tertiary: #334155; /* Slate 700 */

/* Text */
--text-primary: #F1F5F9;
--text-secondary: #94A3B8;
--text-muted: #64748B;

/* Status Colors */
--success: #10B981;
--warning: #F59E0B;
--error: #EF4444;
--info: #3B82F6;
```

### Typography
```css
/* Headings */
h1: Inter Bold, 2.5rem
h2: Inter Semibold, 2rem
h3: Inter Semibold, 1.5rem

/* Body */
body: Inter Regular, 1rem
code: JetBrains Mono, 0.875rem
```

### Layout Patterns

1. **Dashboard Cards**
   - Rounded corners (0.5rem)
   - Subtle shadow
   - Hover effect (scale 1.02)
   - Border accent on active

2. **Code Editors**
   - Full height
   - Dark background
   - Line numbers
   - Syntax highlighting
   - Minimap (optional)

3. **Forms**
   - Inline validation
   - Clear error messages
   - Helpful placeholders
   - Auto-save indicators

---

## Feature Specifications

### 1. Unsloth Fine-Tuning

**User Flow:**
1. User selects model from dropdown
2. User uploads dataset or selects example
3. User configures training parameters
4. User clicks "Start Training"
5. Real-time progress shown
6. User downloads trained model

**Validations:**
- Dataset format validation
- VRAM requirements check
- Parameter range validation
- Disk space check

**Features:**
- Pause/resume training
- Save checkpoints
- Compare models
- Export to multiple formats

### 2. GLM-4 Coding Agent

**User Flow:**
1. User selects action (Generate/Explain/Fix)
2. User inputs code or description
3. User configures options
4. User clicks action button
5. Results shown with syntax highlighting
6. User can copy, edit, or re-generate

**Features:**
- Multi-language support (40+)
- Context preservation across sessions
- History of generations
- Favorite snippets
- Share generated code

### 3. Qwen2.5-Coder

**User Flow:**
1. User selects model size
2. User chooses task type
3. User provides input
4. Real-time/on-demand generation
5. User reviews and accepts

**Features:**
- Multiple completion suggestions
- Context-aware completions
- Import resolution
- Type inference
- Documentation generation

---

## Performance Requirements

### Speed Targets
- Page load: < 2 seconds
- API response: < 5 seconds
- Code generation: < 10 seconds
- Training start: < 30 seconds

### Optimization
- Code splitting by route
- Lazy loading components
- Image optimization
- API response caching
- WebSocket for real-time updates

---

## Responsive Design

### Breakpoints
```css
mobile: 0-640px
tablet: 641-1024px
desktop: 1025px+
```

### Mobile Adaptations
- Collapsible navigation
- Stacked layouts
- Touch-friendly buttons (44px min)
- Swipeable tabs
- Bottom navigation bar

---

## Accessibility Requirements

- WCAG 2.1 AA compliance
- Keyboard navigation
- Screen reader support
- High contrast mode
- Focus indicators
- Alt text for images
- ARIA labels

---

## Example Implementation: Training Page

```typescript
// TrainingPage.tsx
import { useState } from 'react';
import { ModelSelector } from '@/components/ModelSelector';
import { DatasetUpload } from '@/components/DatasetUpload';
import { TrainingConfig } from '@/components/TrainingConfig';
import { TrainingProgress } from '@/components/TrainingProgress';
import { Button } from '@/components/ui/button';
import { useTraining } from '@/hooks/useTraining';

export default function TrainingPage() {
  const [selectedModel, setSelectedModel] = useState('llama-3.1-8b');
  const [dataset, setDataset] = useState<File | null>(null);
  const [config, setConfig] = useState<TrainingConfig>({
    maxSteps: 60,
    learningRate: 2e-4,
    batchSize: 2,
    loraRank: 16,
    use4bit: true,
    useFlashAttention: true,
  });

  const { startTraining, status, progress, metrics } = useTraining();

  const handleStartTraining = async () => {
    if (!dataset) return;
    await startTraining({
      modelName: selectedModel,
      dataset,
      config,
    });
  };

  return (
    <div className="container mx-auto p-6">
      <h1 className="text-4xl font-bold mb-8">
        ⚡ Unsloth Fast Fine-Tuning
      </h1>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Left Column */}
        <div className="space-y-6">
          <ModelSelector
            selected={selectedModel}
            onSelect={setSelectedModel}
          />

          <DatasetUpload
            onUpload={setDataset}
            file={dataset}
          />

          <TrainingConfig
            value={config}
            onChange={setConfig}
          />

          <Button
            onClick={handleStartTraining}
            disabled={!dataset || status === 'training'}
            size="lg"
            className="w-full"
          >
            {status === 'training' ? 'Training...' : 'Start Training'}
          </Button>
        </div>

        {/* Right Column */}
        <div>
          {status !== 'idle' && (
            <TrainingProgress
              status={status}
              progress={progress}
              metrics={metrics}
            />
          )}
        </div>
      </div>
    </div>
  );
}
```

---

## Documentation Structure

### 1. README.md
```markdown
# LLM Dev Tools

Train LLMs 2-5x faster and generate code with AI that beats GPT-4.

## Features
- ⚡ Fast fine-tuning with Unsloth
- 🤖 GLM-4 coding agent (71.8% HumanEval)
- 🏆 Qwen2.5-Coder (74.5% HumanEval)

## Quick Start
[Installation steps]
[First project]

## Documentation
- [User Guide](docs/user-guide.md)
- [API Reference](docs/api-reference.md)
- [Examples](docs/examples.md)
```

### 2. User Guide (docs/user-guide.md)
- Complete walkthrough of each feature
- Screenshots and GIFs
- Best practices
- Common workflows

### 3. API Reference (docs/api-reference.md)
- Every API endpoint documented
- Request/response examples
- Error codes
- Rate limits

### 4. Examples (docs/examples.md)
- Real-world use cases
- Code snippets
- Video tutorials

---

## Testing Requirements

### Unit Tests
- All components
- All hooks
- All utilities
- > 80% coverage

### Integration Tests
- API calls
- Form submissions
- File uploads
- Training flow

### E2E Tests
- Complete user flows
- Critical paths
- Cross-browser

---

## Deployment

### Environment Variables
```env
VITE_API_URL=https://api.example.com
VITE_WS_URL=wss://api.example.com
VITE_MAX_UPLOAD_SIZE=100MB
```

### Build Command
```bash
npm run build
# or
bun run build
```

### Hosting
- Deploy to Lovable built-in hosting
- Enable CDN
- Configure custom domain

---

## Success Metrics

### Key Performance Indicators
- User engagement (DAU/MAU)
- Training completions
- Code generations
- User satisfaction (NPS)

### Analytics Events
- Training started
- Training completed
- Code generated
- Documentation viewed
- Model exported

---

## Additional Features (Phase 2)

1. **Collaboration**
   - Share training sessions
   - Team workspaces
   - Code review

2. **Advanced Analytics**
   - Model performance comparison
   - Cost tracking
   - Usage insights

3. **Integrations**
   - GitHub integration
   - VS Code extension
   - Slack notifications
   - Webhook support

4. **Enterprise Features**
   - SSO authentication
   - Role-based access
   - Audit logs
   - Private model hosting

---

## Final Notes

**Priority**: Focus on core functionality first:
1. Unsloth fine-tuning (highest priority)
2. Qwen2.5-Coder (second priority)
3. GLM-4 coding agent (third priority)
4. Documentation
5. Additional features

**Quality Standards**:
- Clean, maintainable code
- Comprehensive error handling
- Loading states for all async operations
- Helpful error messages
- Smooth animations and transitions

**User Experience**:
- Intuitive navigation
- Clear call-to-actions
- Helpful tooltips
- Progress indicators
- Success confirmations

Build this as a production-ready, enterprise-grade tool that developers will love to use!
