# Kaggle Dataset Setup for LightOS DCIM

Complete guide to downloading and using real datacenter datasets with your Kaggle API token.

## ⚡ Quick Start (30 seconds)

```bash
cd /opt/lightos/dcim-api

# Set your API token
export KAGGLE_API_TOKEN=KGAT_2a4e49d583b937d8c08c972945c4b110

# Install dependencies
pip install kagglehub pandas numpy

# Download datasets
python kaggle_downloader.py

# Start DCIM with real data
python main.py --use-kaggle
```

## 📋 Step-by-Step Guide

### Step 1: Set Your API Token

You have two options:

#### Option A: Environment Variable (Recommended)

```bash
export KAGGLE_API_TOKEN=KGAT_2a4e49d583b937d8c08c972945c4b110
```

To make it permanent, add to your shell profile:

```bash
echo 'export KAGGLE_API_TOKEN=KGAT_2a4e49d583b937d8c08c972945c4b110' >> ~/.bashrc
source ~/.bashrc
```

#### Option B: Command Line Argument

```bash
python kaggle_downloader.py --token KGAT_2a4e49d583b937d8c08c972945c4b110
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

Or manually:

```bash
pip install kagglehub pandas numpy
```

### Step 3: Download Datasets

```bash
python kaggle_downloader.py
```

**This will download:**

1. **Sustainable AI Model Efficiency Dataset**
   - CO2 emissions data
   - Energy consumption metrics
   - AI model efficiency stats

2. **Global Data Centre Energy Footprints Dataset**
   - Datacenter power consumption
   - Global energy usage
   - Efficiency metrics

**Download time:** 2-5 minutes depending on connection

### Step 4: Verify Downloads

```bash
ls -la data/kaggle/
```

You should see:
```
sustainable_ai/     -> Sustainable AI dataset
datacenter_energy/  -> Datacenter energy dataset
manifest.json       -> Download metadata
```

### Step 5: Load and Analyze Data

```bash
python -c "
from kaggle_integration import KaggleDataLoader

# Load data
loader = KaggleDataLoader()
sustainable_ai = loader.load_sustainable_ai_data()
datacenter = loader.load_datacenter_energy_data()

# Analyze
ai_analysis = loader.analyze_sustainable_ai_metrics()
dc_analysis = loader.analyze_datacenter_energy_metrics()

print('Sustainable AI records:', len(sustainable_ai))
print('Datacenter records:', len(datacenter))
"
```

### Step 6: Use with DCIM API

The downloaded datasets are automatically used by the DCIM system.

## 📊 Datasets Overview

### 1. Sustainable AI Model Efficiency

**Source:** `yldrmmahmud/sustainable-ai-model-efficiency-co2-and-energy`

**Contains:**
- AI model training energy consumption
- CO2 emissions per model
- Efficiency metrics (FLOPS/Watt)
- Model architecture impact on energy

**Use Cases:**
- Optimize AI workload energy usage
- Track carbon footprint
- Benchmark model efficiency
- Green AI compliance reporting

### 2. Global Data Centre Energy Footprints

**Source:** `thedevastator/global-data-centre-energy-footprints`

**Contains:**
- Datacenter power consumption
- Regional energy usage
- PUE (Power Usage Effectiveness)
- Cooling efficiency metrics

**Use Cases:**
- Benchmark against industry
- Identify optimization opportunities
- Track efficiency improvements
- Energy cost forecasting

## 🔧 Advanced Usage

### Load Specific CSV Files

```python
from kaggle_integration import KaggleDataLoader
from pathlib import Path

loader = KaggleDataLoader()

# Load specific file
ai_data = loader.load_sustainable_ai_data(
    Path('data/kaggle/sustainable_ai/model_efficiency.csv')
)

dc_data = loader.load_datacenter_energy_data(
    Path('data/kaggle/datacenter_energy/power_consumption.csv')
)
```

### Analyze Energy Metrics

```python
# Analyze Sustainable AI data
analysis = loader.analyze_sustainable_ai_metrics()

print("Energy Statistics:")
for col, stats in analysis['energy_stats'].items():
    print(f"\n{col}:")
    print(f"  Mean: {stats['mean']:.2f}")
    print(f"  Median: {stats['median']:.2f}")
    print(f"  Range: {stats['min']:.2f} - {stats['max']:.2f}")

print("\nCO2 Statistics:")
for col, stats in analysis['co2_stats'].items():
    print(f"\n{col}:")
    print(f"  Mean: {stats['mean']:.2f}")
    print(f"  Median: {stats['median']:.2f}")
```

### Analyze Datacenter Metrics

```python
# Analyze Datacenter Energy data
analysis = loader.analyze_datacenter_energy_metrics()

print("Power Statistics:")
for col, stats in analysis['power_stats'].items():
    print(f"\n{col}:")
    print(f"  Mean: {stats['mean']:.2f} kW")
    print(f"  Peak: {stats['max']:.2f} kW")

print("\nEfficiency Statistics:")
for col, stats in analysis['efficiency_stats'].items():
    print(f"\n{col}:")
    print(f"  Mean: {stats['mean']:.2f}")
```

### Export to Dashboard

```python
import json

# Get statistics
loader = KaggleDataLoader()
loader.load_sustainable_ai_data()
loader.load_datacenter_energy_data()

ai_stats = loader.analyze_sustainable_ai_metrics()
dc_stats = loader.analyze_datacenter_energy_metrics()

# Save for dashboard
with open('dashboard_data.json', 'w') as f:
    json.dump({
        'sustainable_ai': ai_stats,
        'datacenter': dc_stats
    }, f, indent=2)
```

## 🎯 Integration with DCIM

### Option 1: Auto-load on Startup

Edit `main.py` to automatically load Kaggle data:

```python
# In main.py, add at startup:
from kaggle_integration import KaggleDataLoader

loader = KaggleDataLoader()
sustainable_ai = loader.load_sustainable_ai_data()
datacenter = loader.load_datacenter_energy_data()

# Use real data in endpoints
@app.get("/api/dcim/sustainable-ai")
async def get_sustainable_ai_metrics():
    return loader.analyze_sustainable_ai_metrics()

@app.get("/api/dcim/datacenter-energy")
async def get_datacenter_energy_metrics():
    return loader.analyze_datacenter_energy_metrics()
```

### Option 2: CLI Flag

Start API with real data:

```bash
python main.py --use-kaggle
```

### Option 3: Dashboard Integration

Add new dashboard sections showing real data:

```javascript
// In dcim.html
fetch('http://localhost:8001/api/dcim/sustainable-ai')
  .then(res => res.json())
  .then(data => {
    // Display AI efficiency metrics
    document.getElementById('ai-energy').textContent =
      data.energy_stats['energy_kwh'].mean.toFixed(2);
  });

fetch('http://localhost:8001/api/dcim/datacenter-energy')
  .then(res => res.json())
  .then(data => {
    // Display datacenter power metrics
    document.getElementById('dc-power').textContent =
      data.power_stats['power_kw'].mean.toFixed(2);
  });
```

## 🔄 Updating Datasets

Kaggle datasets are versioned. To get latest version:

```bash
# Re-download
python kaggle_downloader.py

# Or manually
import kagglehub

# Force latest version
path = kagglehub.dataset_download(
    "yldrmmahmud/sustainable-ai-model-efficiency-co2-and-energy",
    force_download=True
)
```

## 📦 Dataset Storage

Datasets are downloaded to:

```
~/.cache/kagglehub/datasets/
  └── yldrmmahmud/
      └── sustainable-ai-model-efficiency-co2-and-energy/
  └── thedevastator/
      └── global-data-centre-energy-footprints/
```

Symlinks created in:
```
dcim-api/data/kaggle/
  ├── sustainable_ai -> ~/.cache/kagglehub/...
  └── datacenter_energy -> ~/.cache/kagglehub/...
```

## 🐛 Troubleshooting

### Authentication Failed

```
Error: Authentication failed
```

**Solution:**
```bash
# Verify token is set
echo $KAGGLE_API_TOKEN

# Re-set if needed
export KAGGLE_API_TOKEN=KGAT_2a4e49d583b937d8c08c972945c4b110
```

### Dataset Not Found

```
Error: Dataset not found
```

**Solution:**
```bash
# Check internet connection
ping kaggle.com

# Verify dataset names
# Visit: https://www.kaggle.com/datasets

# Re-download
python kaggle_downloader.py
```

### Import Error

```
ModuleNotFoundError: No module named 'kagglehub'
```

**Solution:**
```bash
pip install kagglehub pandas numpy
```

### Permission Denied

```
PermissionError: Cannot create symlink
```

**Solution:**
```bash
# Run with appropriate permissions
sudo python kaggle_downloader.py

# Or change data directory ownership
sudo chown -R $USER:$USER data/
```

### CSV Not Found

```
Error: No CSV files found in directory
```

**Solution:**
```bash
# Check downloaded files
ls ~/.cache/kagglehub/datasets/*/*/versions/*/

# If empty, re-download
rm -rf ~/.cache/kagglehub/
python kaggle_downloader.py
```

## 📊 Data Analysis Examples

### Example 1: Find Most Efficient AI Models

```python
from kaggle_integration import KaggleDataLoader

loader = KaggleDataLoader()
df = loader.load_sustainable_ai_data()

# Sort by energy efficiency
if 'energy_kwh' in df.columns and 'flops' in df.columns:
    df['efficiency'] = df['flops'] / df['energy_kwh']
    most_efficient = df.nlargest(10, 'efficiency')
    print(most_efficient[['model_name', 'efficiency']])
```

### Example 2: Calculate Carbon Footprint

```python
# Assuming dataset has CO2 emissions
if 'co2_kg' in df.columns:
    total_co2 = df['co2_kg'].sum()
    avg_co2 = df['co2_kg'].mean()

    print(f"Total CO2: {total_co2:.2f} kg")
    print(f"Average per model: {avg_co2:.2f} kg")
```

### Example 3: Benchmark Datacenter PUE

```python
loader = KaggleDataLoader()
df = loader.load_datacenter_energy_data()

# Find PUE column
pue_cols = [col for col in df.columns if 'pue' in col.lower()]

if pue_cols:
    pue_col = pue_cols[0]
    avg_pue = df[pue_col].mean()
    best_pue = df[pue_col].min()

    print(f"Industry Average PUE: {avg_pue:.2f}")
    print(f"Best in Class PUE: {best_pue:.2f}")
    print(f"LightOS Target PUE: 1.10")
```

## 🎯 Next Steps

After setting up Kaggle datasets:

1. **Run Full Demo:**
   ```bash
   ./start_demo.sh
   ```

2. **Start API with Real Data:**
   ```bash
   python main.py --use-kaggle
   ```

3. **View Dashboard:**
   ```
   http://localhost:8000/dcim.html
   ```

4. **Explore Data:**
   ```bash
   python -i kaggle_integration.py
   ```

## 📚 Additional Resources

- **Kaggle API Docs:** https://github.com/Kaggle/kagglehub
- **Dataset 1:** https://www.kaggle.com/datasets/yldrmmahmud/sustainable-ai-model-efficiency-co2-and-energy
- **Dataset 2:** https://www.kaggle.com/datasets/thedevastator/global-data-centre-energy-footprints
- **DCIM API Docs:** http://localhost:8001/docs

## 🔐 Security Notes

- **Never commit your API token** to version control
- Store token in environment variables only
- Use `.gitignore` to exclude `kaggle.json` if using file-based auth
- Rotate token periodically on Kaggle settings page

---

**Ready to go!** Run `python kaggle_downloader.py` to get started.
