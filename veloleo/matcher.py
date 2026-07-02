from dataclasses import dataclass
from datetime import datetime, timedelta
import logging
from typing import Tuple
from geopy.distance import geodesic
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import min_weight_full_bipartite_matching
import numpy as np
import pandas as pd
from tqdm import tqdm
from veloleo.events import Event

logger = logging.getLogger("veloleo")


### CONSTANTS
MAX_TRIP_DURATION = timedelta(hours=4)
MIN_TRIP_DURATION = timedelta(seconds=25)

MIN_TRIP_DISTANCE = 250  # meters, to prevent GPS jitter

MAX_SPEED_MS = 25 / 3.6
PREFERABLE_SPEED_MS = 15 / 3.6

SPEED_PENALTY_WEIGHT_PER_MS = 0.3 / 3.6
REJECT_PENALTY_MINUTES = 45

### /CONSTANTS


@dataclass
class Trip:
    bike_id_start: str
    bike_id_end: str
    start_time: datetime
    end_time: datetime
    start_pos: Tuple[float, float]
    end_pos: Tuple[float, float]
    start_station: int
    end_station: int

    @property
    def duration(self) -> timedelta:
        return self.end_time - self.start_time

    @property
    def distance_m(self) -> float:
        return geodesic((self.start_pos), (self.end_pos)).meters

    @property
    def avg_speed_ms(self) -> float:
        secs = self.duration.total_seconds()
        return self.distance_m / secs if secs > 0 else float("inf")


def haversine_distance_np(
    lon1: np.ndarray, lat1: np.ndarray, lon2: np.ndarray, lat2: np.ndarray
) -> np.ndarray:
    """Vectorized Haversine distance calculation in meters."""
    # Convert degrees to radians
    lon1, lat1, lon2, lat2 = map(np.radians, [lon1, lat1, lon2, lat2])

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = np.sin(dlat / 2.0) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2.0) ** 2
    c = 2 * np.arcsin(np.sqrt(a))
    r = 6371000  # Radius of Earth in meters
    return c * r


def _clean_spatial_density_anomalies(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df

    df_approx = df.copy()
    df_approx["lat_bucket"] = df_approx["lat"].round(3)
    df_approx["lon_bucket"] = df_approx["lon"].round(3)

    exact_glitch = df.groupby(["time", "lat", "lon"])["bike_id"].transform("size") > 3
    bulk_drop_local = (
        df_approx.groupby(["time", "lat_bucket", "lon_bucket"])["bike_id"].transform(
            "size"
        )
        > 12
    )
    bulk_drop_global = df.groupby("time")["bike_id"].transform("size") > 100

    anomalies = exact_glitch | bulk_drop_local | bulk_drop_global

    clean_df = df[~anomalies].copy()
    logger.warning(f"Filtering out {anomalies.sum()} anomalous events from dataset.")

    return clean_df.reset_index(drop=True)


def _events_to_df(events: list[Event]) -> pd.DataFrame:
    df = pd.DataFrame([e.__dict__ for e in events])
    return df.sort_values("time").reset_index(drop=True)


def _build_cost_matrix(dep: pd.DataFrame, arr: pd.DataFrame):
    n_dep = len(dep)
    n_arr = len(arr)

    logger.info("Building cost matrix...")

    # Extract underlying NumPy arrays for fast access
    dep_times = dep["time"].to_numpy()
    dep_lats = dep["lat"].to_numpy()
    dep_lons = dep["lon"].to_numpy()

    arr_times = arr["time"].to_numpy()
    arr_lats = arr["lat"].to_numpy()
    arr_lons = arr["lon"].to_numpy()

    # Pre-calculate search boundaries
    min_delta = np.timedelta64(int(MIN_TRIP_DURATION.total_seconds()), "s")
    max_delta = np.timedelta64(int(MAX_TRIP_DURATION.total_seconds()), "s")

    rows, cols, costs = [], [], []

    for i in tqdm(range(n_dep)):
        d_time = dep_times[i]

        lo = np.searchsorted(arr_times, d_time + min_delta, side="left")
        hi = np.searchsorted(arr_times, d_time + max_delta, side="right")
        if lo < hi:
            sub_times = arr_times[lo:hi]
            sub_lats = arr_lats[lo:hi]
            sub_lons = arr_lons[lo:hi]

            dt = (sub_times - d_time) / np.timedelta64(1, "s")
            dist = haversine_distance_np(
                dep_lons[i], dep_lats[i], sub_lons, sub_lats
            )  # fast distance

            valid_dt = np.where(dt > 0, dt, 150)
            speed = dist / valid_dt

            mask = (dt >= 0) & (dist > MIN_TRIP_DISTANCE) & (speed <= MAX_SPEED_MS)

            valid_indices = np.where(mask)[0]

            if len(valid_indices) > 0:
                dt_valid = dt[valid_indices]
                dt_minutes = dt_valid / 60.0

                speed_valid = speed[valid_indices]
                overspeed = np.clip(speed_valid - PREFERABLE_SPEED_MS, 0, None) * 3.6
                trip_cost = dt_minutes + SPEED_PENALTY_WEIGHT_PER_MS * overspeed

                rows.extend([i] * len(valid_indices))
                cols.extend(lo + valid_indices)
                costs.extend(trip_cost)

        rows.append(i)
        cols.append(n_arr + i)
        costs.append(REJECT_PENALTY_MINUTES)

    return coo_matrix((costs, (rows, cols)), shape=(n_dep, n_arr + n_dep))


def match_trips(departures: list[Event], arrivals: list[Event]):
    logger.info("Matching trips...")

    dep = _events_to_df(departures)
    dep = _clean_spatial_density_anomalies(dep)

    arr = _events_to_df(arrivals)
    arr = _clean_spatial_density_anomalies(arr)

    n_arr = len(arr)

    cost = _build_cost_matrix(dep, arr).tocsr()
    dep_idx, col_idx = min_weight_full_bipartite_matching(cost)

    trips: list[Trip] = []
    n_rejected = 0

    for i, j in zip(dep_idx, col_idx):
        if j >= n_arr:
            n_rejected += 1
            continue

        d, a = dep.iloc[i], arr.iloc[j]
        trips.append(
            Trip(
                bike_id_start=d["bike_id"],
                bike_id_end=a["bike_id"],
                start_time=d["time"],
                end_time=a["time"],
                start_pos=(d["lat"], d["lon"]),
                end_pos=(a["lat"], a["lon"]),
                start_station=d.get("station_id"),
                end_station=a.get("station_id"),
            )
        )

    matched_arr_ids = {j for j in col_idx if j < n_arr}
    unmatched_times = [
        dep.iloc[i]["time"] for i, j in zip(dep_idx, col_idx) if j >= n_arr
    ]

    stats = {
        "n_departures": len(dep),
        "n_arrivals": n_arr,
        "n_trips_matched": len(trips),
        "n_unmatched_departures": n_rejected,
        "n_unmatched_arrivals": n_arr - len(matched_arr_ids),
        "unmatched_times": unmatched_times,
    }

    return trips, stats
