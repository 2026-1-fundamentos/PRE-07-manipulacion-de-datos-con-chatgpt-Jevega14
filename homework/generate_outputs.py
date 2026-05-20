import os
from pathlib import Path

import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def generate_outputs(
    input_dir: str = "files/input",
    output_dir: str = "files",
    drivers_filename: str = "drivers.csv",
    timesheet_filename: str = "timesheet.csv",
) -> None:
    project_root = Path(__file__).resolve().parents[1]
    input_path = project_root / input_dir
    output_summary_path = project_root / output_dir / "output" / "summary.csv"
    output_plot_path = project_root / output_dir / "plots" / "top10_drivers.png"

    output_summary_path.parent.mkdir(parents=True, exist_ok=True)
    output_plot_path.parent.mkdir(parents=True, exist_ok=True)

    drivers = pd.read_csv(input_path / drivers_filename)
    timesheet = pd.read_csv(input_path / timesheet_filename)

    drivers = drivers.copy()
    timesheet = timesheet.copy()
    timesheet["driverId"] = timesheet["driverId"].astype(int)

    summary = (
        timesheet.groupby("driverId")
        .agg(
            total_hours=("hours-logged", "sum"),
            total_miles=("miles-logged", "sum"),
            weeks_reported=("week", "count"),
            avg_hours=("hours-logged", "mean"),
            avg_miles=("miles-logged", "mean"),
            max_hours=("hours-logged", "max"),
            max_miles=("miles-logged", "max"),
        )
        .reset_index()
    )
    summary["avg_hours"] = summary["avg_hours"].round(2)
    summary["avg_miles"] = summary["avg_miles"].round(2)

    merged = drivers.merge(summary, on="driverId", how="inner")
    merged = merged.sort_values(["total_miles", "total_hours"], ascending=False)

    merged.to_csv(output_summary_path, index=False)

    top10 = merged.head(10)
    plt.figure(figsize=(12, 7))
    bars = plt.barh(top10["name"], top10["total_miles"], color="#2a7ac8")
    plt.gca().invert_yaxis()
    plt.title("Top 10 drivers by total miles logged")
    plt.xlabel("Total miles logged")
    plt.tight_layout()

    for bar in bars:
        width = bar.get_width()
        plt.text(width + 50, bar.get_y() + bar.get_height() / 2, f"{int(width):,}", va="center")

    plt.savefig(output_plot_path, dpi=150)
    plt.close()


if __name__ == "__main__":
    generate_outputs()
