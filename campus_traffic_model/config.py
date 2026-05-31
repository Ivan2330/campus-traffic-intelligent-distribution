from dataclasses import dataclass
from typing import Dict


@dataclass(frozen=True)
class Weights:
    bandwidth: float
    delay: float
    loss: float
    load: float
    priority: float
    wifi_penalty: float


WEIGHT_PROFILES: Dict[str, Weights] = {
    "balanced": Weights(
        bandwidth=0.25,
        delay=0.20,
        loss=0.15,
        load=0.25,
        priority=0.10,
        wifi_penalty=0.05,
    ),
    "low_latency": Weights(
        bandwidth=0.15,
        delay=0.35,
        loss=0.15,
        load=0.20,
        priority=0.10,
        wifi_penalty=0.05,
    ),
    "high_throughput": Weights(
        bandwidth=0.40,
        delay=0.15,
        loss=0.10,
        load=0.20,
        priority=0.10,
        wifi_penalty=0.05,
    ),
    "qos_priority": Weights(
        bandwidth=0.20,
        delay=0.20,
        loss=0.15,
        load=0.15,
        priority=0.25,
        wifi_penalty=0.05,
    ),
}

TRAFFIC_CLASSES = {
    "voice": {
        "priority": 5,
        "required_bandwidth_mbps": 0.2,
        "max_delay_ms": 80,
        "max_loss_percent": 1.0,
    },
    "video": {
        "priority": 5,
        "required_bandwidth_mbps": 4.0,
        "max_delay_ms": 120,
        "max_loss_percent": 2.0,
    },
    "lms": {
        "priority": 4,
        "required_bandwidth_mbps": 1.0,
        "max_delay_ms": 180,
        "max_loss_percent": 3.0,
    },
    "web": {
        "priority": 3,
        "required_bandwidth_mbps": 1.5,
        "max_delay_ms": 250,
        "max_loss_percent": 4.0,
    },
    "file_download": {
        "priority": 2,
        "required_bandwidth_mbps": 8.0,
        "max_delay_ms": 500,
        "max_loss_percent": 5.0,
    },
    "background_update": {
        "priority": 1,
        "required_bandwidth_mbps": 3.0,
        "max_delay_ms": 900,
        "max_loss_percent": 8.0,
    },
}

SCENARIOS = {
    "normal_load": {
        "description": "Нормальне денне навантаження кампусної мережі",
        "flow_count": 80,
        "traffic_mix": {
            "voice": 0.05,
            "video": 0.15,
            "lms": 0.25,
            "web": 0.30,
            "file_download": 0.15,
            "background_update": 0.10,
        },
    },
    "peak_load": {
        "description": "Пікове навантаження під час перерви та масового підключення студентів",
        "flow_count": 220,
        "traffic_mix": {
            "voice": 0.05,
            "video": 0.20,
            "lms": 0.20,
            "web": 0.25,
            "file_download": 0.20,
            "background_update": 0.10,
        },
    },
    "video_dominant": {
        "description": "Домінування відеотрафіку під час онлайн-лекцій",
        "flow_count": 150,
        "traffic_mix": {
            "voice": 0.05,
            "video": 0.50,
            "lms": 0.15,
            "web": 0.15,
            "file_download": 0.10,
            "background_update": 0.05,
        },
    },
    "wifi_overload": {
        "description": "Нерівномірне навантаження з перевантаженням Wi-Fi точок доступу",
        "flow_count": 180,
        "traffic_mix": {
            "voice": 0.05,
            "video": 0.25,
            "lms": 0.20,
            "web": 0.25,
            "file_download": 0.15,
            "background_update": 0.10,
        },
        "preferred_zones": ["library", "student_area", "dormitory"],
    },
    "qos_stress": {
        "description": "Сценарій перевірки якості обслуговування критичного трафіку",
        "flow_count": 200,
        "traffic_mix": {
            "voice": 0.15,
            "video": 0.35,
            "lms": 0.25,
            "web": 0.10,
            "file_download": 0.10,
            "background_update": 0.05,
        },
    },
}

RANDOM_SEED = 42
OVERLOAD_THRESHOLD = 0.85
RESULTS_DIR = "results"
