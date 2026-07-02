import numpy as np
from veloleo.matcher import MAX_SPEED_MS, Trip
import matplotlib.pyplot as plt


def plot_diagnostics(
    trips: list[Trip], output_path: str = "trip_diagnostics.png"
) -> None:
    distances_km = [t.distance_m / 1000 for t in trips]
    speeds_kmh = [t.avg_speed_ms * 3.6 for t in trips]

    fig, axes = plt.subplots(1, 2, figsize=(12, 4.5))

    axes[0].hist(distances_km, bins=60, color="#3b82f6", edgecolor="white")
    axes[0].set_xlabel("Distance (km)")
    axes[0].set_ylabel("Trips")
    axes[0].set_title("Trip distance")
    axes[0].axvline(
        np.median(distances_km),
        color="black",
        linestyle="--",
        linewidth=1,
        label=f"median = {np.median(distances_km):.2f} km",
    )
    axes[0].legend()

    axes[1].hist(speeds_kmh, bins=60, color="#f97316", edgecolor="white")
    axes[1].set_xlabel("Average speed (km/h)")
    axes[1].set_ylabel("Trips")
    axes[1].set_title("Trip average speed")
    axes[1].axvline(
        np.median(speeds_kmh),
        color="black",
        linestyle="--",
        linewidth=1,
        label=f"median = {np.median(speeds_kmh):.2f} km/h",
    )
    axes[1].axvline(
        MAX_SPEED_MS * 3.6,
        color="red",
        linestyle=":",
        linewidth=1,
        label=f"MAX_SPEED_MS cutoff = {MAX_SPEED_MS * 3.6:.1f} km/h",
    )
    axes[1].legend()

    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    print(f"saved diagnostics to {output_path}")
