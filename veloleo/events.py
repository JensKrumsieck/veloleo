from dataclasses import dataclass
from datetime import datetime
import logging
import os
from pathlib import Path
import pandas as pd
from tqdm import tqdm

logger = logging.getLogger(__name__)


@dataclass
class Event:
    type: str
    time: datetime
    bike_id: str
    lat: float
    lon: float
    station_id: int | None


def get_events(folder: Path) -> list[Event]:
    files = [f for f in os.listdir(folder) if f.endswith(".csv")]
    events = []
    for f in tqdm(files):
        events.extend(get_daily_events(folder / f))

    logger.info(f"Found {len(events)} Events in {len(files)} days")

    return events


def get_daily_events(file: Path) -> list[Event]:
    df = pd.read_csv(file)
    events: list[Event] = []

    snapshots = sorted(df["time"].unique())
    for i in range(1, len(snapshots)):
        t_prev = snapshots[i - 1]
        t_curr = snapshots[i]

        prev: pd.DataFrame = df[df["time"] == t_prev].set_index("bike_id")
        curr: pd.DataFrame = df[df["time"] == t_curr].set_index("bike_id")

        gone = prev.index.difference(curr.index)
        new = curr.index.difference(prev.index)

        for bike_id in gone:
            row = prev.loc[bike_id]
            events.append(
                Event(
                    "departure",
                    datetime.fromisoformat(t_curr),  # disappeared by this snapshot
                    bike_id,
                    row["lat"],
                    row["lon"],
                    row.get("station_id"),
                )
            )

        for bike_id in new:
            row = curr.loc[bike_id]
            events.append(
                Event(
                    "arrival",
                    datetime.fromisoformat(t_curr),  # reappeared by this snapshot
                    bike_id,
                    row["lat"],
                    row["lon"],
                    row.get("station_id"),
                )
            )

    return events
