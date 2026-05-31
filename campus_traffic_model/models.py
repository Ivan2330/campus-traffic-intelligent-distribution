from dataclasses import dataclass, field
from typing import Optional


@dataclass
class NetworkSegment:
    id: str
    name: str
    segment_type: str  # wifi або ethernet
    zone: str
    capacity_mbps: float
    base_delay_ms: float
    base_loss_percent: float
    current_load_mbps: float = 0.0

    @property
    def load_ratio(self) -> float:
        if self.capacity_mbps <= 0:
            return 1.0
        return min(self.current_load_mbps / self.capacity_mbps, 1.5)

    @property
    def available_bandwidth_mbps(self) -> float:
        return max(self.capacity_mbps - self.current_load_mbps, 0.0)

    def estimated_delay_ms(self, additional_mbps: float = 0.0) -> float:
        projected_load = min((self.current_load_mbps + additional_mbps) / self.capacity_mbps, 1.5)
        congestion_factor = 1 + 3 * max(projected_load - 0.65, 0) ** 2
        return self.base_delay_ms * congestion_factor

    def estimated_loss_percent(self, additional_mbps: float = 0.0) -> float:
        projected_load = min((self.current_load_mbps + additional_mbps) / self.capacity_mbps, 1.5)
        congestion_loss = 0.0
        if projected_load > 0.75:
            congestion_loss = (projected_load - 0.75) * 8
        return min(self.base_loss_percent + congestion_loss, 20.0)

    def can_accept(self, required_bandwidth_mbps: float) -> bool:
        return self.current_load_mbps + required_bandwidth_mbps <= self.capacity_mbps * 1.10

    def add_flow(self, bandwidth_mbps: float) -> None:
        self.current_load_mbps += bandwidth_mbps

    def reset(self) -> None:
        self.current_load_mbps = 0.0


@dataclass(frozen=True)
class TrafficFlow:
    id: int
    source_zone: str
    traffic_type: str
    priority: int
    required_bandwidth_mbps: float
    max_delay_ms: float
    max_loss_percent: float


@dataclass
class FlowAssignment:
    flow_id: int
    scenario: str
    algorithm: str
    traffic_type: str
    priority: int
    source_zone: str
    segment_id: Optional[str]
    segment_type: Optional[str]
    segment_zone: Optional[str]
    required_bandwidth_mbps: float
    estimated_delay_ms: float
    estimated_loss_percent: float
    qos_satisfied: bool


@dataclass
class SimulationResult:
    scenario: str
    algorithm: str
    avg_delay_ms: float
    avg_loss_percent: float
    avg_wifi_load_percent: float
    avg_ethernet_load_percent: float
    max_segment_load_percent: float
    overloaded_segments: int
    qos_satisfaction_percent: float
    accepted_flows_percent: float
    efficiency_index: float
    assignments: list[FlowAssignment] = field(default_factory=list)
