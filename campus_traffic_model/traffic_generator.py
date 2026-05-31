from __future__ import annotations

import random
from typing import Dict, List

from config import TRAFFIC_CLASSES
from models import TrafficFlow

ZONES = [
    "academic_building",
    "library",
    "student_area",
    "dormitory",
    "computer_lab",
    "administration",
]


def weighted_choice(weights: Dict[str, float]) -> str:
    items = list(weights.keys())
    probabilities = list(weights.values())
    return random.choices(items, weights=probabilities, k=1)[0]


def generate_traffic_flows(scenario_name: str, scenario_config: dict) -> List[TrafficFlow]:
    flow_count = scenario_config["flow_count"]
    traffic_mix = scenario_config["traffic_mix"]
    preferred_zones = scenario_config.get("preferred_zones")

    flows: List[TrafficFlow] = []
    for i in range(1, flow_count + 1):
        traffic_type = weighted_choice(traffic_mix)
        traffic_meta = TRAFFIC_CLASSES[traffic_type]

        source_zone = random.choice(preferred_zones) if preferred_zones else random.choice(ZONES)

        # Невелика випадкова варіація робить модель менш штучною.
        bandwidth_noise = random.uniform(0.75, 1.25)
        required_bandwidth = round(
            traffic_meta["required_bandwidth_mbps"] * bandwidth_noise,
            3,
        )

        flows.append(
            TrafficFlow(
                id=i,
                source_zone=source_zone,
                traffic_type=traffic_type,
                priority=traffic_meta["priority"],
                required_bandwidth_mbps=required_bandwidth,
                max_delay_ms=traffic_meta["max_delay_ms"],
                max_loss_percent=traffic_meta["max_loss_percent"],
            )
        )

    return flows
