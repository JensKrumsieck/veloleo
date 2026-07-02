from pathlib import Path
import logging
import numpy as np
from veloleo.events import get_events
from veloleo.map import (
    find_routes,
    plot_heatmap_data,
    save_geojson,
    save_geopkg,
)
from veloleo.matcher import match_trips
from veloleo.plot import plot_diagnostics

DATA_DIRECTORY = Path("veloleo-harvester/data")
LOG_FORMAT = "[%(asctime)s] " "%(levelname)-8s " "%(message)s"

logger = logging.getLogger("veloleo")


def main():
    logging.basicConfig(
        level=logging.INFO,
        format=LOG_FORMAT,
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    logger.info("Collecting events...")

    # get departure and arrival events
    events = get_events(DATA_DIRECTORY)
    departures = [ev for ev in events if ev.type == "departure"]
    arrivals = [ev for ev in events if ev.type == "arrival"]

    logger.info(f"Found {len(departures)} depature and {len(arrivals)} arrival events")

    trips, stats = match_trips(departures, arrivals)
    durations = [t.duration.total_seconds() / 60 for t in trips]
    speeds = [t.avg_speed_ms for t in trips]
    logger.info(f"Found {len(trips)}")
    logger.info(f"median trip duration: {np.median(durations):.1f} min")
    logger.info(f"median avg speed:     {np.median(speeds):.2f} m/s")
    logger.info(f"{stats["n_unmatched_departures"]} unmatched departures")

    plot_diagnostics(trips)

    edges, edges_active = find_routes(trips)
    save_geojson(edges_active)
    save_geopkg(edges_active)
    plot_heatmap_data(edges, edges_active)


if __name__ == "__main__":
    main()
