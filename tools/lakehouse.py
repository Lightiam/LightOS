#!/usr/bin/env python3
"""
LightOS AI Lakehouse
Unified data platform for AI/ML workflows combining data lake and data warehouse

Features:
- Feature Store: Manage and serve ML features
- Model Registry: Version control for models with lineage tracking
- Vector Store: Semantic search and RAG (Retrieval-Augmented Generation)
- Data Catalog: Unified metadata for all AI assets
- Real-time Feature Pipelines: Stream processing for fresh features
- Model Serving: Deploy models with autoscaling
"""

import json
import time
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum
import hashlib


class FeatureType(Enum):
    """Feature data types"""
    CONTINUOUS = "continuous"
    CATEGORICAL = "categorical"
    EMBEDDING = "embedding"
    TEXT = "text"
    IMAGE = "image"


class ModelStatus(Enum):
    """Model lifecycle status"""
    TRAINING = "training"
    STAGING = "staging"
    PRODUCTION = "production"
    ARCHIVED = "archived"


class DataSource(Enum):
    """Data source types"""
    BATCH = "batch"
    STREAMING = "streaming"
    REALTIME = "realtime"


@dataclass
class Feature:
    """Feature definition in feature store"""
    name: str
    feature_type: FeatureType
    description: str
    entity: str  # e.g., "user", "product", "session"
    data_source: DataSource
    transformation: Optional[str] = None  # SQL or Python code
    refresh_interval_seconds: int = 3600
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())

    # Statistics
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    mean_value: Optional[float] = None
    null_percentage: float = 0.0


@dataclass
class FeatureGroup:
    """Group of related features"""
    name: str
    features: List[Feature]
    entity: str
    description: str
    version: int = 1
    tags: List[str] = field(default_factory=list)


@dataclass
class ModelMetadata:
    """Model metadata for registry"""
    name: str
    version: str
    framework: str  # "pytorch", "tensorflow", "onnx", "lightos"
    description: str
    status: ModelStatus

    # Model artifacts
    model_path: str
    config_path: Optional[str] = None

    # Training metadata
    training_features: List[str] = field(default_factory=list)
    training_dataset: Optional[str] = None
    training_metrics: Dict[str, float] = field(default_factory=dict)
    hyperparameters: Dict[str, Any] = field(default_factory=dict)

    # Performance
    inference_latency_ms: Optional[float] = None
    throughput_qps: Optional[float] = None
    memory_mb: Optional[float] = None

    # Lineage
    parent_model: Optional[str] = None
    derived_from_features: List[str] = field(default_factory=list)

    # Timestamps
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    deployed_at: Optional[str] = None

    # Hash for reproducibility
    model_hash: Optional[str] = None

    def compute_hash(self) -> str:
        """Compute hash of model artifacts for reproducibility"""
        content = f"{self.name}:{self.version}:{self.framework}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]


@dataclass
class VectorDocument:
    """Document with vector embedding for semantic search"""
    id: str
    text: str
    embedding: List[float]
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


class FeatureStore:
    """
    Feature Store for managing ML features

    Provides:
    - Feature registration and versioning
    - Feature serving (batch and real-time)
    - Feature monitoring and drift detection
    - Point-in-time correctness for training
    """

    def __init__(self, storage_path: str = "./feature_store"):
        self.storage_path = storage_path
        self.features: Dict[str, Feature] = {}
        self.feature_groups: Dict[str, FeatureGroup] = {}

    def register_feature(self, feature: Feature):
        """Register a new feature"""
        print(f"📊 Registering feature: {feature.name}")
        self.features[feature.name] = feature

    def register_feature_group(self, group: FeatureGroup):
        """Register a group of related features"""
        print(f"📦 Registering feature group: {group.name} ({len(group.features)} features)")
        self.feature_groups[group.name] = group

        # Register individual features
        for feature in group.features:
            self.register_feature(feature)

    def get_feature(self, name: str) -> Optional[Feature]:
        """Get feature by name"""
        return self.features.get(name)

    def get_feature_group(self, name: str) -> Optional[FeatureGroup]:
        """Get feature group by name"""
        return self.feature_groups.get(name)

    def get_features_for_entity(self, entity: str) -> List[Feature]:
        """Get all features for a specific entity"""
        return [f for f in self.features.values() if f.entity == entity]

    def compute_features(
        self,
        entity_ids: List[str],
        feature_names: List[str],
        timestamp: Optional[datetime] = None
    ) -> Dict[str, Dict[str, Any]]:
        """
        Compute feature values for given entities

        Args:
            entity_ids: List of entity IDs
            feature_names: Features to compute
            timestamp: Point-in-time for historical features

        Returns:
            Dict mapping entity_id to feature values
        """
        print(f"🔄 Computing {len(feature_names)} features for {len(entity_ids)} entities")

        # In production, would query feature tables
        # For demo, return mock data
        results = {}
        for entity_id in entity_ids:
            results[entity_id] = {
                name: self._mock_feature_value(name)
                for name in feature_names
                if name in self.features
            }

        return results

    def _mock_feature_value(self, feature_name: str) -> Any:
        """Generate mock feature value"""
        feature = self.features.get(feature_name)
        if not feature:
            return None

        if feature.feature_type == FeatureType.CONTINUOUS:
            return 42.0
        elif feature.feature_type == FeatureType.CATEGORICAL:
            return "category_A"
        elif feature.feature_type == FeatureType.EMBEDDING:
            return [0.1, 0.2, 0.3, 0.4]
        else:
            return "value"

    def monitor_feature_drift(self, feature_name: str) -> Dict[str, float]:
        """
        Monitor feature drift over time

        Returns:
            Drift statistics (mean shift, distribution change, etc.)
        """
        print(f"📈 Monitoring drift for feature: {feature_name}")

        # In production, would compute statistical drift metrics
        return {
            "mean_shift": 0.02,
            "variance_change": 0.01,
            "drift_score": 0.15,
            "alert": False
        }


class ModelRegistry:
    """
    Model Registry for version control and lineage tracking

    Provides:
    - Model versioning
    - Lineage tracking (data, features, parent models)
    - Performance metrics tracking
    - Promotion workflow (staging -> production)
    """

    def __init__(self, storage_path: str = "./model_registry"):
        self.storage_path = storage_path
        self.models: Dict[Tuple[str, str], ModelMetadata] = {}  # (name, version) -> metadata

    def register_model(
        self,
        metadata: ModelMetadata,
        artifacts_path: str
    ) -> str:
        """
        Register a new model version

        Returns:
            Model identifier (name:version)
        """
        # Compute hash
        metadata.model_hash = metadata.compute_hash()

        key = (metadata.name, metadata.version)
        self.models[key] = metadata

        print(f"✅ Registered model: {metadata.name} v{metadata.version}")
        print(f"   Status: {metadata.status.value}")
        print(f"   Framework: {metadata.framework}")
        print(f"   Hash: {metadata.model_hash}")

        return f"{metadata.name}:{metadata.version}"

    def get_model(self, name: str, version: str) -> Optional[ModelMetadata]:
        """Get specific model version"""
        return self.models.get((name, version))

    def get_latest_version(self, name: str, status: Optional[ModelStatus] = None) -> Optional[ModelMetadata]:
        """Get latest model version, optionally filtered by status"""
        matching_models = [
            model for (model_name, _), model in self.models.items()
            if model_name == name and (status is None or model.status == status)
        ]

        if not matching_models:
            return None

        # Sort by version (assuming semantic versioning)
        return max(matching_models, key=lambda m: m.version)

    def promote_model(self, name: str, version: str, to_status: ModelStatus):
        """Promote model to new status (e.g., staging -> production)"""
        model = self.get_model(name, version)
        if not model:
            print(f"❌ Model not found: {name} v{version}")
            return

        old_status = model.status
        model.status = to_status

        if to_status == ModelStatus.PRODUCTION:
            model.deployed_at = datetime.now().isoformat()

        print(f"🚀 Promoted {name} v{version}: {old_status.value} -> {to_status.value}")

    def get_model_lineage(self, name: str, version: str) -> Dict[str, Any]:
        """Get full lineage of a model"""
        model = self.get_model(name, version)
        if not model:
            return {}

        lineage = {
            "model": f"{name}:{version}",
            "framework": model.framework,
            "training_dataset": model.training_dataset,
            "features": model.training_features,
            "parent_model": model.parent_model,
            "created_at": model.created_at,
            "deployed_at": model.deployed_at,
            "metrics": model.training_metrics
        }

        # Recursively get parent lineage
        if model.parent_model:
            parent_name, parent_version = model.parent_model.split(":")
            lineage["parent_lineage"] = self.get_model_lineage(parent_name, parent_version)

        return lineage

    def list_models(self, status: Optional[ModelStatus] = None) -> List[ModelMetadata]:
        """List all models, optionally filtered by status"""
        models = list(self.models.values())

        if status:
            models = [m for m in models if m.status == status]

        return sorted(models, key=lambda m: m.created_at, reverse=True)


class VectorStore:
    """
    Vector Store for semantic search and RAG

    Provides:
    - Vector similarity search
    - Hybrid search (vector + keyword)
    - Nearest neighbor retrieval
    - Support for RAG workflows
    """

    def __init__(self, embedding_dim: int = 768):
        self.embedding_dim = embedding_dim
        self.documents: Dict[str, VectorDocument] = {}

    def add_document(self, doc: VectorDocument):
        """Add document with embedding"""
        if len(doc.embedding) != self.embedding_dim:
            raise ValueError(f"Embedding dim mismatch: expected {self.embedding_dim}, got {len(doc.embedding)}")

        self.documents[doc.id] = doc
        print(f"📄 Added document: {doc.id}")

    def search(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Tuple[VectorDocument, float]]:
        """
        Search for similar documents

        Args:
            query_embedding: Query vector
            top_k: Number of results to return
            filters: Metadata filters

        Returns:
            List of (document, similarity_score) tuples
        """
        print(f"🔍 Searching for top-{top_k} similar documents...")

        # Compute cosine similarity
        results = []
        for doc in self.documents.values():
            # Apply filters
            if filters:
                if not self._matches_filters(doc.metadata, filters):
                    continue

            similarity = self._cosine_similarity(query_embedding, doc.embedding)
            results.append((doc, similarity))

        # Sort by similarity
        results.sort(key=lambda x: x[1], reverse=True)

        return results[:top_k]

    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Compute cosine similarity between two vectors"""
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        norm1 = sum(a * a for a in vec1) ** 0.5
        norm2 = sum(b * b for b in vec2) ** 0.5

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return dot_product / (norm1 * norm2)

    def _matches_filters(self, metadata: Dict[str, Any], filters: Dict[str, Any]) -> bool:
        """Check if document metadata matches filters"""
        for key, value in filters.items():
            if key not in metadata or metadata[key] != value:
                return False
        return True


class AILakehouse:
    """
    Complete AI Lakehouse combining all components

    Orchestrates:
    - Feature engineering and serving
    - Model training and deployment
    - Vector search for RAG
    - Data lineage and governance
    """

    def __init__(self):
        self.feature_store = FeatureStore()
        self.model_registry = ModelRegistry()
        self.vector_store = VectorStore()

    def create_training_dataset(
        self,
        feature_group_name: str,
        entity_ids: List[str],
        target_feature: str,
        timestamp: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Create training dataset with point-in-time correct features

        Returns:
            Training dataset with features and target
        """
        print(f"\n🏗️  Creating training dataset from feature group: {feature_group_name}")

        feature_group = self.feature_store.get_feature_group(feature_group_name)
        if not feature_group:
            raise ValueError(f"Feature group not found: {feature_group_name}")

        feature_names = [f.name for f in feature_group.features if f.name != target_feature]

        # Compute features
        features = self.feature_store.compute_features(entity_ids, feature_names, timestamp)

        print(f"   ✅ Created dataset with {len(feature_names)} features, {len(entity_ids)} samples")

        return {
            "features": features,
            "feature_names": feature_names,
            "target": target_feature,
            "num_samples": len(entity_ids),
            "created_at": datetime.now().isoformat()
        }

    def train_and_register_model(
        self,
        model_name: str,
        version: str,
        framework: str,
        feature_group: str,
        training_config: Dict[str, Any]
    ) -> str:
        """
        Train model and register in model registry

        Returns:
            Model identifier
        """
        print(f"\n🏋️  Training model: {model_name} v{version}")

        # Create training dataset
        dataset = self.create_training_dataset(
            feature_group_name=feature_group,
            entity_ids=["entity_1", "entity_2", "entity_3"],
            target_feature="target"
        )

        # Simulate training
        print(f"   Training with {framework}...")
        time.sleep(0.5)  # Simulate training time

        # Create model metadata
        metadata = ModelMetadata(
            name=model_name,
            version=version,
            framework=framework,
            description=f"Model trained on {feature_group}",
            status=ModelStatus.STAGING,
            model_path=f"./models/{model_name}/{version}",
            training_features=dataset["feature_names"],
            training_dataset=feature_group,
            training_metrics={
                "accuracy": 0.95,
                "precision": 0.93,
                "recall": 0.92,
                "f1_score": 0.925
            },
            hyperparameters=training_config,
            inference_latency_ms=2.5,
            throughput_qps=400,
            memory_mb=512
        )

        # Register model
        model_id = self.model_registry.register_model(metadata, metadata.model_path)

        print(f"   ✅ Training complete!")
        print(f"   Accuracy: {metadata.training_metrics['accuracy']:.2%}")

        return model_id

    def deploy_model(self, name: str, version: str):
        """Deploy model to production"""
        print(f"\n🚀 Deploying model: {name} v{version}")

        # Promote to production
        self.model_registry.promote_model(name, version, ModelStatus.PRODUCTION)

        # Get model
        model = self.model_registry.get_model(name, version)

        print(f"   ✅ Model deployed successfully!")
        print(f"   Endpoint: /predict/{name}/{version}")
        print(f"   Latency: {model.inference_latency_ms}ms")
        print(f"   Throughput: {model.throughput_qps} QPS")


def main():
    """Example usage"""
    print("=" * 70)
    print("LightOS AI Lakehouse")
    print("=" * 70)
    print()

    lakehouse = AILakehouse()

    # 1. Register features
    print("📊 Step 1: Register features in Feature Store")
    print("-" * 70)

    user_features = FeatureGroup(
        name="user_features_v1",
        entity="user",
        description="User behavioral features",
        features=[
            Feature("user_age", FeatureType.CONTINUOUS, "User age in years", "user", DataSource.BATCH),
            Feature("user_lifetime_value", FeatureType.CONTINUOUS, "Total revenue from user", "user", DataSource.BATCH),
            Feature("user_activity_7d", FeatureType.CONTINUOUS, "Activity count last 7 days", "user", DataSource.STREAMING),
            Feature("user_segment", FeatureType.CATEGORICAL, "User segment (A/B/C)", "user", DataSource.BATCH),
        ]
    )

    lakehouse.feature_store.register_feature_group(user_features)
    print()

    # 2. Train and register model
    print("🏋️  Step 2: Train and register model")
    print("-" * 70)

    model_id = lakehouse.train_and_register_model(
        model_name="user_churn_predictor",
        version="1.0.0",
        framework="pytorch",
        feature_group="user_features_v1",
        training_config={
            "learning_rate": 0.001,
            "batch_size": 32,
            "epochs": 10
        }
    )
    print()

    # 3. Deploy model
    print("🚀 Step 3: Deploy model to production")
    print("-" * 70)
    lakehouse.deploy_model("user_churn_predictor", "1.0.0")
    print()

    # 4. Model lineage
    print("🔗 Step 4: Get model lineage")
    print("-" * 70)
    lineage = lakehouse.model_registry.get_model_lineage("user_churn_predictor", "1.0.0")
    print(json.dumps(lineage, indent=2))
    print()

    # 5. Vector store for RAG
    print("🔍 Step 5: Vector search for RAG")
    print("-" * 70)

    # Add documents
    lakehouse.vector_store.add_document(VectorDocument(
        id="doc1",
        text="LightOS is a high-performance AI inference platform",
        embedding=[0.1, 0.2, 0.3] + [0.0] * 765,
        metadata={"category": "documentation", "topic": "intro"}
    ))

    lakehouse.vector_store.add_document(VectorDocument(
        id="doc2",
        text="Thermal-aware scheduling prevents GPU throttling",
        embedding=[0.15, 0.25, 0.35] + [0.0] * 765,
        metadata={"category": "documentation", "topic": "features"}
    ))

    # Search
    query = [0.12, 0.22, 0.32] + [0.0] * 765
    results = lakehouse.vector_store.search(query, top_k=2)

    print("Search results:")
    for doc, score in results:
        print(f"  - {doc.id}: {doc.text[:50]}... (similarity: {score:.3f})")
    print()

    # 6. Feature drift monitoring
    print("📈 Step 6: Monitor feature drift")
    print("-" * 70)
    drift_stats = lakehouse.feature_store.monitor_feature_drift("user_activity_7d")
    print(f"Drift statistics for user_activity_7d:")
    for metric, value in drift_stats.items():
        print(f"  {metric}: {value}")
    print()

    print("✅ AI Lakehouse demo complete!")


if __name__ == "__main__":
    main()
