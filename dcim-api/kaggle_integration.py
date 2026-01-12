#!/usr/bin/env python3
"""
Kaggle Dataset Integration for LightOS DCIM
Loads real datacenter datasets from Kaggle for realistic simulation
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Optional, Dict, Any
import json


class KaggleDataLoader:
    """
    Loads and processes Kaggle datacenter datasets

    Supported datasets:
    - Data Center Power Consumption
    - GPU Performance Metrics
    - Server Room Environmental Data
    - Energy Management Systems Data
    """

    def __init__(self, dataset_path: Optional[Path] = None):
        """
        Initialize with dataset path

        Args:
            dataset_path: Path to Kaggle dataset CSV files
        """
        self.dataset_path = dataset_path or Path("data/kaggle")
        self.dataset_path.mkdir(parents=True, exist_ok=True)

        # Cache for loaded data
        self.power_data = None
        self.gpu_data = None
        self.thermal_data = None
        self.environmental_data = None

    def download_instructions(self) -> str:
        """
        Provide instructions for downloading Kaggle datasets
        """
        return """
        # Kaggle Dataset Integration Instructions

        ## Step 1: Install Kaggle CLI
        ```bash
        pip install kaggle
        ```

        ## Step 2: Configure Kaggle API
        1. Go to https://www.kaggle.com/account
        2. Click "Create New API Token"
        3. Save kaggle.json to ~/.kaggle/kaggle.json
        4. Set permissions: chmod 600 ~/.kaggle/kaggle.json

        ## Step 3: Download Recommended Datasets

        ### Data Center Power Consumption
        ```bash
        kaggle datasets download -d atechnoholic/data-center-power-consumption
        unzip data-center-power-consumption.zip -d dcim-api/data/kaggle/power/
        ```

        ### Server Room Environmental Data
        ```bash
        kaggle datasets download -d selfishgene/server-room-environmental-monitoring
        unzip server-room-environmental-monitoring.zip -d dcim-api/data/kaggle/environmental/
        ```

        ### Energy Management Systems
        ```bash
        kaggle datasets download -d atechnoholic/energy-management-system-dataset
        unzip energy-management-system-dataset.zip -d dcim-api/data/kaggle/energy/
        ```

        ## Step 4: Run DCIM API with Kaggle Data
        ```bash
        cd dcim-api
        python main.py --use-kaggle
        ```

        ## Supported File Formats
        - CSV files with timestamp columns
        - JSON files with time-series data
        - Parquet files for large datasets

        ## Required Columns
        - **Power Data**: timestamp, power_kw, voltage_v, current_a
        - **GPU Data**: timestamp, gpu_id, temperature_c, power_w, utilization_pct
        - **Thermal Data**: timestamp, temp_c, humidity_pct, airflow_cfm
        - **Environmental**: timestamp, ambient_temp_c, humidity_pct, pressure_kpa
        """

    def load_power_data(self, file_path: Optional[Path] = None) -> pd.DataFrame:
        """
        Load power consumption data from Kaggle dataset

        Args:
            file_path: Path to CSV file (optional)

        Returns:
            DataFrame with power metrics
        """
        if file_path is None:
            file_path = self.dataset_path / "power" / "power_consumption.csv"

        if not file_path.exists():
            print(f"Power data not found at {file_path}")
            print("Using simulated data. See download_instructions() for real data.")
            return self._generate_simulated_power_data()

        try:
            df = pd.read_csv(file_path)

            # Standardize column names
            column_mapping = {
                'timestamp': 'timestamp',
                'Timestamp': 'timestamp',
                'power': 'power_kw',
                'Power': 'power_kw',
                'power_consumption': 'power_kw',
                'voltage': 'voltage_v',
                'Voltage': 'voltage_v',
                'current': 'current_a',
                'Current': 'current_a'
            }

            df.rename(columns=column_mapping, inplace=True)

            # Ensure timestamp is datetime
            if 'timestamp' in df.columns:
                df['timestamp'] = pd.to_datetime(df['timestamp'])

            self.power_data = df
            print(f"Loaded {len(df)} power records from Kaggle dataset")
            return df

        except Exception as e:
            print(f"Error loading power data: {e}")
            return self._generate_simulated_power_data()

    def load_gpu_data(self, file_path: Optional[Path] = None) -> pd.DataFrame:
        """
        Load GPU metrics from Kaggle dataset

        Args:
            file_path: Path to CSV file (optional)

        Returns:
            DataFrame with GPU metrics
        """
        if file_path is None:
            file_path = self.dataset_path / "gpu" / "gpu_metrics.csv"

        if not file_path.exists():
            print(f"GPU data not found at {file_path}")
            return self._generate_simulated_gpu_data()

        try:
            df = pd.read_csv(file_path)

            column_mapping = {
                'timestamp': 'timestamp',
                'gpu_id': 'gpu_id',
                'temperature': 'temperature_c',
                'temp': 'temperature_c',
                'power': 'power_w',
                'utilization': 'utilization_pct',
                'util': 'utilization_pct'
            }

            df.rename(columns=column_mapping, inplace=True)

            if 'timestamp' in df.columns:
                df['timestamp'] = pd.to_datetime(df['timestamp'])

            self.gpu_data = df
            print(f"Loaded {len(df)} GPU records from Kaggle dataset")
            return df

        except Exception as e:
            print(f"Error loading GPU data: {e}")
            return self._generate_simulated_gpu_data()

    def load_thermal_data(self, file_path: Optional[Path] = None) -> pd.DataFrame:
        """
        Load thermal/cooling data from Kaggle dataset

        Args:
            file_path: Path to CSV file (optional)

        Returns:
            DataFrame with thermal metrics
        """
        if file_path is None:
            file_path = self.dataset_path / "environmental" / "thermal.csv"

        if not file_path.exists():
            print(f"Thermal data not found at {file_path}")
            return self._generate_simulated_thermal_data()

        try:
            df = pd.read_csv(file_path)

            column_mapping = {
                'timestamp': 'timestamp',
                'temperature': 'temp_c',
                'temp': 'temp_c',
                'humidity': 'humidity_pct',
                'airflow': 'airflow_cfm'
            }

            df.rename(columns=column_mapping, inplace=True)

            if 'timestamp' in df.columns:
                df['timestamp'] = pd.to_datetime(df['timestamp'])

            self.thermal_data = df
            print(f"Loaded {len(df)} thermal records from Kaggle dataset")
            return df

        except Exception as e:
            print(f"Error loading thermal data: {e}")
            return self._generate_simulated_thermal_data()

    def get_sample_at_time(self, dataset: str, timestamp: pd.Timestamp) -> Dict[str, Any]:
        """
        Get a sample from the dataset at specific time

        Args:
            dataset: 'power', 'gpu', or 'thermal'
            timestamp: Timestamp to sample

        Returns:
            Dictionary with metrics at that time
        """
        if dataset == 'power' and self.power_data is not None:
            nearest = self.power_data.iloc[
                (self.power_data['timestamp'] - timestamp).abs().argsort()[:1]
            ]
            return nearest.to_dict('records')[0]

        elif dataset == 'gpu' and self.gpu_data is not None:
            nearest = self.gpu_data.iloc[
                (self.gpu_data['timestamp'] - timestamp).abs().argsort()[:1]
            ]
            return nearest.to_dict('records')[0]

        elif dataset == 'thermal' and self.thermal_data is not None:
            nearest = self.thermal_data.iloc[
                (self.thermal_data['timestamp'] - timestamp).abs().argsort()[:1]
            ]
            return nearest.to_dict('records')[0]

        return {}

    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about loaded datasets"""
        stats = {
            "datasets_loaded": [],
            "total_records": 0,
            "time_range": {}
        }

        if self.power_data is not None:
            stats["datasets_loaded"].append("power")
            stats["total_records"] += len(self.power_data)
            stats["time_range"]["power"] = {
                "start": str(self.power_data['timestamp'].min()),
                "end": str(self.power_data['timestamp'].max()),
                "duration_hours": (
                    self.power_data['timestamp'].max() -
                    self.power_data['timestamp'].min()
                ).total_seconds() / 3600
            }

        if self.gpu_data is not None:
            stats["datasets_loaded"].append("gpu")
            stats["total_records"] += len(self.gpu_data)

        if self.thermal_data is not None:
            stats["datasets_loaded"].append("thermal")
            stats["total_records"] += len(self.thermal_data)

        return stats

    # Simulated data generators (fallback when Kaggle data not available)

    def _generate_simulated_power_data(self) -> pd.DataFrame:
        """Generate simulated power data"""
        hours = 24 * 7  # 1 week
        timestamps = pd.date_range(
            start=pd.Timestamp.now() - pd.Timedelta(hours=hours),
            periods=hours * 60,  # 1 minute intervals
            freq='1min'
        )

        # Simulate daily power pattern
        hour_of_day = timestamps.hour
        base_load = 150  # kW
        peak_factor = 1 + 0.3 * np.sin((hour_of_day - 6) * np.pi / 12)
        noise = np.random.normal(0, 5, len(timestamps))

        power_kw = base_load * peak_factor + noise

        df = pd.DataFrame({
            'timestamp': timestamps,
            'power_kw': power_kw,
            'voltage_v': 480 + np.random.normal(0, 2, len(timestamps)),
            'current_a': power_kw * 1000 / 480,
            'power_factor': 0.95 + np.random.normal(0, 0.02, len(timestamps))
        })

        print("Using simulated power data (1 week, 1-min intervals)")
        return df

    def _generate_simulated_gpu_data(self) -> pd.DataFrame:
        """Generate simulated GPU data"""
        hours = 24
        num_gpus = 8
        timestamps = pd.date_range(
            start=pd.Timestamp.now() - pd.Timedelta(hours=hours),
            periods=hours * 3600,  # 1 second intervals
            freq='1s'
        )

        data = []
        for gpu_id in range(num_gpus):
            for ts in timestamps:
                data.append({
                    'timestamp': ts,
                    'gpu_id': gpu_id,
                    'temperature_c': 65 + np.random.normal(0, 3),
                    'power_w': 350 + np.random.normal(0, 20),
                    'utilization_pct': 85 + np.random.normal(0, 10)
                })

        df = pd.DataFrame(data)
        print(f"Using simulated GPU data ({num_gpus} GPUs, 24 hours, 1-sec intervals)")
        return df

    def _generate_simulated_thermal_data(self) -> pd.DataFrame:
        """Generate simulated thermal data"""
        hours = 24 * 7
        timestamps = pd.date_range(
            start=pd.Timestamp.now() - pd.Timedelta(hours=hours),
            periods=hours * 60,
            freq='1min'
        )

        df = pd.DataFrame({
            'timestamp': timestamps,
            'temp_c': 22 + np.random.normal(0, 1, len(timestamps)),
            'humidity_pct': 50 + np.random.normal(0, 5, len(timestamps)),
            'airflow_cfm': 5000 + np.random.normal(0, 100, len(timestamps))
        })

        print("Using simulated thermal data (1 week, 1-min intervals)")
        return df


def main():
    """Demo usage"""
    print("="*70)
    print("LightOS DCIM - Kaggle Dataset Integration")
    print("="*70)
    print()

    loader = KaggleDataLoader()

    # Print download instructions
    print(loader.download_instructions())
    print()

    # Try loading data
    print("Attempting to load datasets...")
    print()

    power_df = loader.load_power_data()
    gpu_df = loader.load_gpu_data()
    thermal_df = loader.load_thermal_data()

    print()
    print("="*70)
    print("Dataset Statistics")
    print("="*70)

    stats = loader.get_statistics()
    print(json.dumps(stats, indent=2))

    print()
    print("Sample power data:")
    print(power_df.head())

    print()
    print("To use real Kaggle data, follow the download instructions above")


if __name__ == "__main__":
    main()
