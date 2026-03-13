"""
Policy Engine — evaluates routing rules from config.yaml.
Supports hot-reload via update_rules().
"""
from typing import Dict, Any
import yaml
import random


class PolicyEngine:
    def __init__(self, config_path: str):
        self.config_path = config_path
        self._load(config_path)

    def _load(self, path: str):
        with open(path, "r") as f:
            self._config = yaml.safe_load(f)
        self._rules = self._config.get("routing_rules", [])
        self._default = self._config.get("default", {"model_tier": "lightbase", "context_budget": 4096, "cache_strategy": "exact"})
        self._tiers = self._config.get("model_tiers", {})
        self._topology = self._config.get("topology", {}).get("domains", [])

    def rules_count(self) -> int:
        return len(self._rules)

    def get_full_policy(self) -> Dict[str, Any]:
        return {
            "routing_rules": self._rules,
            "model_tiers": self._tiers,
            "default": self._default,
            "topology_domains": self._topology
        }

    def update_rules(self, new_rules: Any, config_path: str):
        """Hot-reload: replace routing_rules in config and persist."""
        if isinstance(new_rules, list):
            self._config["routing_rules"] = new_rules
        elif isinstance(new_rules, dict) and "routing_rules" in new_rules:
            self._config["routing_rules"] = new_rules["routing_rules"]
        else:
            raise ValueError("Expected a list of rules or dict with 'routing_rules' key")

        with open(config_path, "w") as f:
            yaml.dump(self._config, f, default_flow_style=False)
        self._load(config_path)

    def evaluate(
        self,
        prompt_length: int,
        context_tokens: int,
        user_tier: str,
        latency_slo_ms: int,
        task_type: str
    ) -> Dict[str, Any]:
        """Match the first applicable rule, fall through to default."""
        matched_rule = "default"

        for rule in self._rules:
            cond = rule.get("condition", {})
            if self._matches(cond, prompt_length, context_tokens, user_tier, latency_slo_ms):
                matched_rule = rule.get("name", "unnamed")
                result = rule["result"]
                return self._build_response(result, matched_rule)

        return self._build_response(self._default, matched_rule)

    def _matches(self, cond: Dict, prompt_length: int, context_tokens: int, user_tier: str, latency_slo_ms: int) -> bool:
        for key, val in cond.items():
            if key == "latency_slo_ms_lt" and not (latency_slo_ms < val):
                return False
            if key == "latency_slo_ms_lte" and not (latency_slo_ms <= val):
                return False
            if key == "context_tokens_lt" and not (context_tokens < val):
                return False
            if key == "context_tokens_gte" and not (context_tokens >= val):
                return False
            if key == "user_tier_eq" and not (user_tier == val):
                return False
        return True

    def _build_response(self, result: Dict, matched_rule: str) -> Dict[str, Any]:
        tier_id = result.get("model_tier", "lightbase")
        tier_info = self._tiers.get(tier_id, {})

        # Pick a random topology domain for telemetry
        domain = random.choice(self._topology)["id"] if self._topology else "dc-1-rack-a"

        return {
            "model_tier": tier_id,
            "model_display_name": tier_info.get("display_name", tier_id.capitalize()),
            "context_budget": result.get("context_budget", 4096),
            "cache_strategy": result.get("cache_strategy", "exact"),
            "matched_rule": matched_rule,
            "estimated_latency_ms": tier_info.get("avg_latency_ms", 200),
            "estimated_cost_per_1k": tier_info.get("cost_per_1k_tokens", 0.001),
            "topology_domain": domain
        }
