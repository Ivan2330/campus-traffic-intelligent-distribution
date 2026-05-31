from __future__ import annotations

import copy
import random
from typing import Dict, List, Tuple

import pandas as pd

from algorithms import choose_segment
from config import RANDOM_SEED, SCENARIOS
from metrics import build_simulation_result
from models import FlowAssignment, NetworkSegment, SimulationResult, TrafficFlow
from topology import create_segments
from traffic_generator import generate_traffic_flows

ALGORITHMS = ["baseline", "least_loaded", "qos_priority", "intelligent"]


def assign_flow(
    scenario_name: str,
    algorithm: str,
    flow: TrafficFlow,
    segments: Dict[str, NetworkSegment],
    profile_name: str,
) -> FlowAssignment:
    segment = choose_segment(algorithm, flow, segments, profile_name=profile_name)

    if segment is None:
        return FlowAssignment(
            flow_id=flow.id,
            scenario=scenario_name,
            algorithm=algorithm,
            traffic_type=flow.traffic_type,
            priority=flow.priority,
            source_zone=flow.source_zone,
            segment_id=None,
            segment_type=None,
            segment_zone=None,
            required_bandwidth_mbps=flow.required_bandwidth_mbps,
            estimated_delay_ms=0.0,
            estimated_loss_percent=0.0,
            qos_satisfied=False,
        )

    estimated_delay = segment.estimated_delay_ms(flow.required_bandwidth_mbps)
    estimated_loss = segment.estimated_loss_percent(flow.required_bandwidth_mbps)
    qos_satisfied = estimated_delay <= flow.max_delay_ms and estimated_loss <= flow.max_loss_percent

    segment.add_flow(flow.required_bandwidth_mbps)

    return FlowAssignment(
        flow_id=flow.id,
        scenario=scenario_name,
        algorithm=algorithm,
        traffic_type=flow.traffic_type,
        priority=flow.priority,
        source_zone=flow.source_zone,
        segment_id=segment.id,
        segment_type=segment.segment_type,
        segment_zone=segment.zone,
        required_bandwidth_mbps=flow.required_bandwidth_mbps,
        estimated_delay_ms=round(estimated_delay, 2),
        estimated_loss_percent=round(estimated_loss, 3),
        qos_satisfied=qos_satisfied,
    )


def run_single_simulation(
    scenario_name: str,
    flows: List[TrafficFlow],
    algorithm: str,
    profile_name: str = "balanced",
) -> SimulationResult:
    segments = create_segments()
    assignments: List[FlowAssignment] = []

    # Високопріоритетні потоки обробляємо раніше для QoS/intelligent алгоритмів.
    if algorithm in {"qos_priority", "intelligent"}:
        processing_order = sorted(flows, key=lambda f: f.priority, reverse=True)
    else:
        processing_order = list(flows)

    for flow in processing_order:
        assignment = assign_flow(scenario_name, algorithm, flow, segments, profile_name)
        assignments.append(assignment)

    return build_simulation_result(scenario_name, algorithm, assignments, segments)


def run_all_experiments(profile_name: str = "balanced") -> Tuple[pd.DataFrame, pd.DataFrame, List[SimulationResult]]:
    random.seed(RANDOM_SEED)
    summary_rows = []
    assignment_rows = []
    results: List[SimulationResult] = []

    for scenario_name, scenario_config in SCENARIOS.items():
        flows = generate_traffic_flows(scenario_name, scenario_config)

        for algorithm in ALGORITHMS:
            # Для чесного порівняння кожен алгоритм отримує ті самі потоки.
            flows_copy = copy.deepcopy(flows)
            result = run_single_simulation(scenario_name, flows_copy, algorithm, profile_name)
            results.append(result)
            summary_rows.append(
                {
                    "scenario": result.scenario,
                    "algorithm": result.algorithm,
                    "avg_delay_ms": result.avg_delay_ms,
                    "avg_loss_percent": result.avg_loss_percent,
                    "avg_wifi_load_percent": result.avg_wifi_load_percent,
                    "avg_ethernet_load_percent": result.avg_ethernet_load_percent,
                    "max_segment_load_percent": result.max_segment_load_percent,
                    "overloaded_segments": result.overloaded_segments,
                    "qos_satisfaction_percent": result.qos_satisfaction_percent,
                    "accepted_flows_percent": result.accepted_flows_percent,
                    "efficiency_index": result.efficiency_index,
                }
            )
            for assignment in result.assignments:
                assignment_rows.append(assignment.__dict__)

    return pd.DataFrame(summary_rows), pd.DataFrame(assignment_rows), results
