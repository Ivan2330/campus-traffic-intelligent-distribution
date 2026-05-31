from __future__ import annotations

from typing import Dict, List
import networkx as nx

from models import NetworkSegment


def create_segments() -> Dict[str, NetworkSegment]:
    """Створює набір Wi-Fi та Ethernet-сегментів кампусної мережі."""
    segments = {
        "wifi_ap_1": NetworkSegment(
            id="wifi_ap_1",
            name="AP-1 Навчальний корпус",
            segment_type="wifi",
            zone="academic_building",
            capacity_mbps=180,
            base_delay_ms=18,
            base_loss_percent=0.7,
        ),
        "wifi_ap_2": NetworkSegment(
            id="wifi_ap_2",
            name="AP-2 Бібліотека",
            segment_type="wifi",
            zone="library",
            capacity_mbps=140,
            base_delay_ms=22,
            base_loss_percent=0.9,
        ),
        "wifi_ap_3": NetworkSegment(
            id="wifi_ap_3",
            name="AP-3 Студентська зона",
            segment_type="wifi",
            zone="student_area",
            capacity_mbps=120,
            base_delay_ms=26,
            base_loss_percent=1.1,
        ),
        "wifi_ap_4": NetworkSegment(
            id="wifi_ap_4",
            name="AP-4 Гуртожиток",
            segment_type="wifi",
            zone="dormitory",
            capacity_mbps=160,
            base_delay_ms=28,
            base_loss_percent=1.3,
        ),
        "eth_lab": NetworkSegment(
            id="eth_lab",
            name="Ethernet комп'ютерного класу",
            segment_type="ethernet",
            zone="computer_lab",
            capacity_mbps=950,
            base_delay_ms=4,
            base_loss_percent=0.05,
        ),
        "eth_admin": NetworkSegment(
            id="eth_admin",
            name="Ethernet адміністративного корпусу",
            segment_type="ethernet",
            zone="administration",
            capacity_mbps=800,
            base_delay_ms=5,
            base_loss_percent=0.05,
        ),
        "eth_academic": NetworkSegment(
            id="eth_academic",
            name="Ethernet навчального корпусу",
            segment_type="ethernet",
            zone="academic_building",
            capacity_mbps=900,
            base_delay_ms=5,
            base_loss_percent=0.05,
        ),
        "eth_server": NetworkSegment(
            id="eth_server",
            name="Ethernet серверного сегмента",
            segment_type="ethernet",
            zone="server_room",
            capacity_mbps=1200,
            base_delay_ms=3,
            base_loss_percent=0.03,
        ),
    }
    return segments


def reset_segments(segments: Dict[str, NetworkSegment]) -> None:
    for segment in segments.values():
        segment.reset()


def build_topology_graph(segments: Dict[str, NetworkSegment]) -> nx.Graph:
    """Будує графову модель для візуалізації топології."""
    graph = nx.Graph()
    graph.add_node("Core Router", layer="core")
    graph.add_node("Main Switch", layer="distribution")
    graph.add_edge("Core Router", "Main Switch")

    for segment in segments.values():
        zone_name = segment.zone.replace("_", " ").title()
        graph.add_node(zone_name, layer="zone")
        graph.add_node(segment.name, layer=segment.segment_type)
        graph.add_edge("Main Switch", zone_name)
        graph.add_edge(zone_name, segment.name)

    return graph


def candidate_segments_for_zone(
    source_zone: str,
    segments: Dict[str, NetworkSegment],
    allow_cross_zone: bool = True,
) -> List[NetworkSegment]:
    same_zone = [s for s in segments.values() if s.zone == source_zone]

    if not allow_cross_zone:
        return same_zone if same_zone else list(segments.values())

    ethernet_segments = [s for s in segments.values() if s.segment_type == "ethernet"]
    wifi_segments = [s for s in segments.values() if s.segment_type == "wifi"]

    candidates = []
    candidates.extend(same_zone)
    candidates.extend([s for s in ethernet_segments if s not in candidates])
    candidates.extend([s for s in wifi_segments if s not in candidates])
    return candidates
