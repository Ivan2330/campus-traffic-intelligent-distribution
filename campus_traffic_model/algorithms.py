from __future__ import annotations

from typing import Dict, Optional

from config import WEIGHT_PROFILES
from models import NetworkSegment, TrafficFlow
from topology import candidate_segments_for_zone


def normalize_positive(value: float, max_value: float) -> float:
    if max_value <= 0:
        return 0.0
    return max(0.0, min(value / max_value, 1.0))


def normalize_negative(value: float, max_value: float) -> float:
    """Для показників, де менше — краще."""
    if max_value <= 0:
        return 0.0
    return 1.0 - max(0.0, min(value / max_value, 1.0))


def choose_baseline(flow: TrafficFlow, segments: Dict[str, NetworkSegment]) -> Optional[NetworkSegment]:
    candidates = candidate_segments_for_zone(flow.source_zone, segments, allow_cross_zone=False)
    if not candidates:
        return None
    # Імітуємо типову поведінку: користувач залишається у своєму локальному сегменті.
    return min(candidates, key=lambda s: s.current_load_mbps)


def choose_least_loaded(flow: TrafficFlow, segments: Dict[str, NetworkSegment]) -> Optional[NetworkSegment]:
    candidates = candidate_segments_for_zone(flow.source_zone, segments, allow_cross_zone=True)
    feasible = [s for s in candidates if s.can_accept(flow.required_bandwidth_mbps)]
    if not feasible:
        feasible = candidates
    return min(feasible, key=lambda s: s.load_ratio)


def choose_qos_priority(flow: TrafficFlow, segments: Dict[str, NetworkSegment]) -> Optional[NetworkSegment]:
    candidates = candidate_segments_for_zone(flow.source_zone, segments, allow_cross_zone=True)
    feasible = [s for s in candidates if s.can_accept(flow.required_bandwidth_mbps)]
    if not feasible:
        feasible = candidates

    def score(segment: NetworkSegment) -> float:
        delay = segment.estimated_delay_ms(flow.required_bandwidth_mbps)
        loss = segment.estimated_loss_percent(flow.required_bandwidth_mbps)
        priority_factor = flow.priority / 5
        qos_fit = 0
        if delay <= flow.max_delay_ms:
            qos_fit += 0.5
        if loss <= flow.max_loss_percent:
            qos_fit += 0.5
        ethernet_bonus = 0.10 if segment.segment_type == "ethernet" and flow.priority >= 4 else 0
        return qos_fit + priority_factor * 0.3 - segment.load_ratio * 0.3 + ethernet_bonus

    return max(feasible, key=score)


def intelligent_score(
    flow: TrafficFlow,
    segment: NetworkSegment,
    profile_name: str = "balanced",
) -> float:
    weights = WEIGHT_PROFILES[profile_name]
    delay = segment.estimated_delay_ms(flow.required_bandwidth_mbps)
    loss = segment.estimated_loss_percent(flow.required_bandwidth_mbps)
    available = segment.available_bandwidth_mbps

    bandwidth_score = normalize_positive(available, segment.capacity_mbps)
    delay_score = normalize_negative(delay, max(flow.max_delay_ms * 2, 1))
    loss_score = normalize_negative(loss, max(flow.max_loss_percent * 2, 1))
    load_score = normalize_negative(segment.load_ratio, 1.2)
    priority_score = flow.priority / 5

    wifi_penalty = 0.0
    if segment.segment_type == "wifi" and segment.load_ratio > 0.65:
        wifi_penalty = min((segment.load_ratio - 0.65) / 0.55, 1.0)

    # Якщо пропускної здатності недостатньо, штрафуємо, але не забороняємо повністю.
    capacity_penalty = 0.25 if not segment.can_accept(flow.required_bandwidth_mbps) else 0.0

    return (
        weights.bandwidth * bandwidth_score
        + weights.delay * delay_score
        + weights.loss * loss_score
        + weights.load * load_score
        + weights.priority * priority_score
        - weights.wifi_penalty * wifi_penalty
        - capacity_penalty
    )


def choose_intelligent(
    flow: TrafficFlow,
    segments: Dict[str, NetworkSegment],
    profile_name: str = "balanced",
) -> Optional[NetworkSegment]:
    candidates = candidate_segments_for_zone(flow.source_zone, segments, allow_cross_zone=True)
    if not candidates:
        return None
    return max(candidates, key=lambda s: intelligent_score(flow, s, profile_name))


def choose_segment(
    algorithm: str,
    flow: TrafficFlow,
    segments: Dict[str, NetworkSegment],
    profile_name: str = "balanced",
) -> Optional[NetworkSegment]:
    if algorithm == "baseline":
        return choose_baseline(flow, segments)
    if algorithm == "least_loaded":
        return choose_least_loaded(flow, segments)
    if algorithm == "qos_priority":
        return choose_qos_priority(flow, segments)
    if algorithm == "intelligent":
        return choose_intelligent(flow, segments, profile_name)
    raise ValueError(f"Unknown algorithm: {algorithm}")
