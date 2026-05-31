from __future__ import annotations

from typing import Dict, List

from config import OVERLOAD_THRESHOLD
from models import FlowAssignment, NetworkSegment, SimulationResult


def calculate_efficiency_index(
    qos_satisfaction_percent: float,
    accepted_flows_percent: float,
    avg_delay_ms: float,
    avg_loss_percent: float,
    max_segment_load_percent: float,
    overloaded_segments: int,
) -> float:
    qos_component = qos_satisfaction_percent / 100
    accepted_component = accepted_flows_percent / 100
    delay_penalty = min(avg_delay_ms / 500, 1)
    loss_penalty = min(avg_loss_percent / 10, 1)
    overload_penalty = min(overloaded_segments / 8, 1)
    max_load_penalty = max(0, min((max_segment_load_percent - 85) / 50, 1))

    efficiency = (
        0.35 * qos_component
        + 0.20 * accepted_component
        + 0.15 * (1 - delay_penalty)
        + 0.10 * (1 - loss_penalty)
        + 0.10 * (1 - overload_penalty)
        + 0.10 * (1 - max_load_penalty)
    )
    return round(efficiency * 100, 2)


def build_simulation_result(
    scenario: str,
    algorithm: str,
    assignments: List[FlowAssignment],
    segments: Dict[str, NetworkSegment],
) -> SimulationResult:
    accepted = [a for a in assignments if a.segment_id is not None]
    total = len(assignments)

    if accepted:
        avg_delay = sum(a.estimated_delay_ms for a in accepted) / len(accepted)
        avg_loss = sum(a.estimated_loss_percent for a in accepted) / len(accepted)
        qos_satisfied = sum(1 for a in accepted if a.qos_satisfied)
        qos_percent = qos_satisfied / len(accepted) * 100
    else:
        avg_delay = 0.0
        avg_loss = 0.0
        qos_percent = 0.0

    wifi_segments = [s for s in segments.values() if s.segment_type == "wifi"]
    ethernet_segments = [s for s in segments.values() if s.segment_type == "ethernet"]

    avg_wifi_load = (
        sum(s.load_ratio for s in wifi_segments) / len(wifi_segments) * 100
        if wifi_segments
        else 0.0
    )
    avg_eth_load = (
        sum(s.load_ratio for s in ethernet_segments) / len(ethernet_segments) * 100
        if ethernet_segments
        else 0.0
    )
    max_load = max((s.load_ratio for s in segments.values()), default=0.0) * 100
    overloaded = sum(1 for s in segments.values() if s.load_ratio >= OVERLOAD_THRESHOLD)
    accepted_percent = len(accepted) / total * 100 if total else 0.0

    efficiency = calculate_efficiency_index(
        qos_satisfaction_percent=qos_percent,
        accepted_flows_percent=accepted_percent,
        avg_delay_ms=avg_delay,
        avg_loss_percent=avg_loss,
        max_segment_load_percent=max_load,
        overloaded_segments=overloaded,
    )

    return SimulationResult(
        scenario=scenario,
        algorithm=algorithm,
        avg_delay_ms=round(avg_delay, 2),
        avg_loss_percent=round(avg_loss, 3),
        avg_wifi_load_percent=round(avg_wifi_load, 2),
        avg_ethernet_load_percent=round(avg_eth_load, 2),
        max_segment_load_percent=round(max_load, 2),
        overloaded_segments=overloaded,
        qos_satisfaction_percent=round(qos_percent, 2),
        accepted_flows_percent=round(accepted_percent, 2),
        efficiency_index=efficiency,
        assignments=assignments,
    )
