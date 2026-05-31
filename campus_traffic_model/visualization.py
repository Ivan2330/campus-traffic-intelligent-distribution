from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd

from topology import build_topology_graph, create_segments


def ensure_results_dir(results_dir: str) -> Path:
    path = Path(results_dir)
    path.mkdir(parents=True, exist_ok=True)
    return path


def save_grouped_bar(
    df: pd.DataFrame,
    metric: str,
    title: str,
    ylabel: str,
    filename: str,
    results_dir: str,
) -> None:
    pivot = df.pivot(index="scenario", columns="algorithm", values=metric)
    ax = pivot.plot(kind="bar", figsize=(12, 6))
    ax.set_title(title)
    ax.set_xlabel("Сценарій")
    ax.set_ylabel(ylabel)
    ax.tick_params(axis="x", rotation=25)
    ax.legend(title="Алгоритм")
    plt.tight_layout()
    plt.savefig(Path(results_dir) / filename, dpi=180)
    plt.close()


def save_all_charts(summary_df: pd.DataFrame, results_dir: str) -> None:
    ensure_results_dir(results_dir)
    save_grouped_bar(
        summary_df,
        metric="avg_delay_ms",
        title="Порівняння середньої затримки для різних алгоритмів",
        ylabel="Середня затримка, мс",
        filename="delay_comparison.png",
        results_dir=results_dir,
    )
    save_grouped_bar(
        summary_df,
        metric="qos_satisfaction_percent",
        title="Частка потоків, обслужених відповідно до вимог QoS",
        ylabel="QoS-задоволення, %",
        filename="qos_satisfaction.png",
        results_dir=results_dir,
    )
    save_grouped_bar(
        summary_df,
        metric="overloaded_segments",
        title="Кількість перевантажених сегментів мережі",
        ylabel="Кількість сегментів",
        filename="overloaded_segments.png",
        results_dir=results_dir,
    )
    save_grouped_bar(
        summary_df,
        metric="efficiency_index",
        title="Інтегральний індекс ефективності алгоритмів",
        ylabel="Індекс ефективності, %",
        filename="efficiency_index.png",
        results_dir=results_dir,
    )
    save_grouped_bar(
        summary_df,
        metric="avg_wifi_load_percent",
        title="Середнє завантаження Wi-Fi точок доступу",
        ylabel="Завантаження, %",
        filename="wifi_load_comparison.png",
        results_dir=results_dir,
    )
    save_grouped_bar(
        summary_df,
        metric="avg_ethernet_load_percent",
        title="Середнє завантаження Ethernet-сегментів",
        ylabel="Завантаження, %",
        filename="ethernet_load_comparison.png",
        results_dir=results_dir,
    )


def save_topology_image(results_dir: str) -> None:
    segments = create_segments()
    graph = build_topology_graph(segments)

    pos = nx.spring_layout(graph, seed=7, k=0.9)
    plt.figure(figsize=(13, 8))
    nx.draw_networkx_nodes(graph, pos, node_size=1600)
    nx.draw_networkx_edges(graph, pos, width=1.5)
    nx.draw_networkx_labels(graph, pos, font_size=8)
    plt.title("Графова модель кампусної Wi-Fi/Ethernet мережі")
    plt.axis("off")
    plt.tight_layout()
    plt.savefig(Path(results_dir) / "topology.png", dpi=180)
    plt.close()
