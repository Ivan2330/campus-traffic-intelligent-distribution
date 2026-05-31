from pathlib import Path

from config import RESULTS_DIR
from experiment import run_all_experiments
from visualization import ensure_results_dir, save_all_charts, save_topology_image


def main() -> None:
    results_path = ensure_results_dir(RESULTS_DIR)

    summary_df, flows_df, _ = run_all_experiments(profile_name="balanced")

    summary_file = Path(results_path) / "summary_results.csv"
    flows_file = Path(results_path) / "flows_distribution.csv"

    summary_df.to_csv(summary_file, index=False, encoding="utf-8-sig")
    flows_df.to_csv(flows_file, index=False, encoding="utf-8-sig")

    save_all_charts(summary_df, RESULTS_DIR)
    save_topology_image(RESULTS_DIR)

    print("Моделювання завершено.")
    print(f"Зведені результати: {summary_file}")
    print(f"Розподіл потоків: {flows_file}")
    print(f"Графіки збережено у папці: {results_path}")
    print()
    print("Короткий підсумок:")
    print(summary_df.to_string(index=False))


if __name__ == "__main__":
    main()
