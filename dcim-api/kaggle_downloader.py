#!/usr/bin/env python3
"""
Kaggle Dataset Downloader for LightOS DCIM
Downloads and processes real datacenter datasets using Kaggle API
"""

import os
import sys
from pathlib import Path
import json

try:
    import kagglehub
except ImportError:
    print("Error: kagglehub not installed")
    print("Install with: pip install kagglehub")
    sys.exit(1)


class KaggleDownloader:
    """Download and manage Kaggle datasets for DCIM"""

    def __init__(self, api_token: str = None):
        """
        Initialize with Kaggle API token

        Args:
            api_token: Kaggle API token (optional, will use env var if not provided)
        """
        self.data_dir = Path(__file__).parent / "data" / "kaggle"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Set API token if provided
        if api_token:
            os.environ['KAGGLE_API_TOKEN'] = api_token
            print("✓ Kaggle API token configured")
        elif 'KAGGLE_API_TOKEN' in os.environ:
            print("✓ Using KAGGLE_API_TOKEN from environment")
        else:
            print("⚠️  No Kaggle API token found")
            print("Set with: export KAGGLE_API_TOKEN=your_token")
            print("Or pass to constructor: KaggleDownloader(api_token='your_token')")

    def authenticate(self):
        """Authenticate with Kaggle"""
        try:
            kagglehub.login()
            print("✓ Authenticated with Kaggle")
            return True
        except Exception as e:
            print(f"✗ Authentication failed: {e}")
            print("\nTo authenticate:")
            print("1. Set environment variable: export KAGGLE_API_TOKEN=your_token")
            print("2. Or pass token to constructor")
            return False

    def download_sustainable_ai_dataset(self) -> Path:
        """
        Download Sustainable AI Model Efficiency dataset
        Dataset: yldrmmahmud/sustainable-ai-model-efficiency-co2-and-energy

        Contains:
        - AI model energy consumption
        - CO2 emissions
        - Efficiency metrics
        """
        print("\n" + "="*70)
        print("Downloading: Sustainable AI Model Efficiency Dataset")
        print("="*70)

        try:
            path = kagglehub.dataset_download(
                "yldrmmahmud/sustainable-ai-model-efficiency-co2-and-energy"
            )
            print(f"✓ Downloaded to: {path}")

            # Create symlink in our data directory
            target = self.data_dir / "sustainable_ai"
            if target.exists():
                target.unlink()
            target.symlink_to(path)

            print(f"✓ Linked to: {target}")

            # List files
            self._list_files(path)

            return Path(path)

        except Exception as e:
            print(f"✗ Download failed: {e}")
            return None

    def download_datacenter_energy_dataset(self) -> Path:
        """
        Download Global Data Centre Energy Footprints dataset
        Dataset: thedevastator/global-data-centre-energy-footprints

        Contains:
        - Data center energy consumption
        - Global footprint data
        - Power usage metrics
        """
        print("\n" + "="*70)
        print("Downloading: Global Data Centre Energy Footprints")
        print("="*70)

        try:
            path = kagglehub.dataset_download(
                "thedevastator/global-data-centre-energy-footprints"
            )
            print(f"✓ Downloaded to: {path}")

            # Create symlink in our data directory
            target = self.data_dir / "datacenter_energy"
            if target.exists():
                target.unlink()
            target.symlink_to(path)

            print(f"✓ Linked to: {target}")

            # List files
            self._list_files(path)

            return Path(path)

        except Exception as e:
            print(f"✗ Download failed: {e}")
            return None

    def download_all_datasets(self) -> dict:
        """Download all DCIM datasets"""
        print("\n" + "="*70)
        print("LightOS DCIM - Kaggle Dataset Downloader")
        print("="*70)

        results = {}

        # Authenticate
        if not self.authenticate():
            print("\n✗ Cannot download datasets without authentication")
            return results

        # Download datasets
        print("\nDownloading datasets...")

        results['sustainable_ai'] = self.download_sustainable_ai_dataset()
        results['datacenter_energy'] = self.download_datacenter_energy_dataset()

        # Summary
        print("\n" + "="*70)
        print("Download Summary")
        print("="*70)

        for name, path in results.items():
            if path:
                print(f"✓ {name}: {path}")
            else:
                print(f"✗ {name}: Failed")

        # Save manifest
        manifest = {
            'datasets': {
                name: str(path) if path else None
                for name, path in results.items()
            },
            'download_time': str(Path(list(results.values())[0]).stat().st_mtime) if any(results.values()) else None
        }

        manifest_path = self.data_dir / "manifest.json"
        with open(manifest_path, 'w') as f:
            json.dump(manifest, f, indent=2)

        print(f"\n✓ Manifest saved to: {manifest_path}")

        return results

    def _list_files(self, path: Path):
        """List files in downloaded dataset"""
        path = Path(path)
        if not path.exists():
            return

        print("\nDataset files:")
        for file in sorted(path.rglob('*')):
            if file.is_file():
                size_mb = file.stat().st_size / (1024 * 1024)
                print(f"  - {file.name} ({size_mb:.2f} MB)")

    def get_dataset_info(self) -> dict:
        """Get information about downloaded datasets"""
        manifest_path = self.data_dir / "manifest.json"

        if not manifest_path.exists():
            return {"status": "no_datasets", "message": "No datasets downloaded yet"}

        with open(manifest_path) as f:
            manifest = json.load(f)

        info = {
            "status": "ready",
            "datasets": []
        }

        for name, path in manifest['datasets'].items():
            if path and Path(path).exists():
                info['datasets'].append({
                    "name": name,
                    "path": path,
                    "files": len(list(Path(path).rglob('*'))),
                    "size_mb": sum(
                        f.stat().st_size for f in Path(path).rglob('*') if f.is_file()
                    ) / (1024 * 1024)
                })

        return info


def main():
    """Main entry point"""
    print("="*70)
    print("LightOS DCIM - Kaggle Dataset Downloader")
    print("="*70)
    print()

    # Check for API token
    api_token = os.environ.get('KAGGLE_API_TOKEN')

    if not api_token:
        print("⚠️  Kaggle API token not found in environment")
        print()
        print("To set your token:")
        print("  export KAGGLE_API_TOKEN=KGAT_2a4e49d583b937d8c08c972945c4b110")
        print()
        print("Or run:")
        print("  python kaggle_downloader.py --token KGAT_2a4e49d583b937d8c08c972945c4b110")
        print()

        # Check command line args
        if len(sys.argv) > 2 and sys.argv[1] == '--token':
            api_token = sys.argv[2]
            print(f"✓ Using token from command line")
        else:
            print("Continuing without authentication (may fail)...")

    # Create downloader
    downloader = KaggleDownloader(api_token=api_token)

    # Download all datasets
    results = downloader.download_all_datasets()

    # Show info
    print("\n" + "="*70)
    print("Dataset Information")
    print("="*70)

    info = downloader.get_dataset_info()
    print(json.dumps(info, indent=2))

    print("\n" + "="*70)
    print("Next Steps")
    print("="*70)
    print()
    print("1. Datasets are downloaded and ready to use")
    print("2. Start DCIM API with real data:")
    print("     python main.py --use-kaggle")
    print()
    print("3. Or load data in Python:")
    print("     from kaggle_integration import KaggleDataLoader")
    print("     loader = KaggleDataLoader()")
    print("     loader.load_sustainable_ai_data()")
    print()


if __name__ == "__main__":
    main()
