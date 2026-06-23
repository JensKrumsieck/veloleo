from pathlib import Path
import logging
from veloleo.events import get_events

DATA_DIRECTORY = Path("veloleo-harvester/data")
LOG_FORMAT = "[%(asctime)s] " "%(levelname)-8s " "%(message)s"

logger = logging.getLogger("veloleo")


def main():
    logging.basicConfig(
        level=logging.INFO,
        format=LOG_FORMAT,
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # get departure and arrival events
    events = get_events(DATA_DIRECTORY)
    departures = [ev for ev in events if ev.type == "departure"]
    arrivals = [ev for ev in events if ev.type == "arrival"]

    logger.info(f"Found {len(departures)} depature and {len(arrivals)} arrival events")


if __name__ == "__main__":
    main()
