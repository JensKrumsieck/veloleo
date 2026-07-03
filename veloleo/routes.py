import logging
import numpy as np
import osmnx as ox
import networkx as nx
from pyproj import Transformer
from tqdm import tqdm
from matcher import Trip
from collections import Counter
from bike_map import get_graph

logger = logging.getLogger("veloleo")


def find_routes(trips: list[Trip]):
    G = get_graph()

    # WGS84 (lat, lon) to EPSG:4326
    transformer = Transformer.from_crs(
        "EPSG:4326",
        G.graph["crs"],
        always_xy=True,
    )

    start_lons = [t.start_pos[1] for t in trips]
    start_lats = [t.start_pos[0] for t in trips]
    end_lons = [t.end_pos[1] for t in trips]
    end_lats = [t.end_pos[0] for t in trips]

    sx, sy = transformer.transform(start_lons, start_lats)
    ex, ey = transformer.transform(end_lons, end_lats)

    logger.info("Finding nearest network nodes in bulk...")
    u_nodes = ox.distance.nearest_nodes(G, sx, sy)
    v_nodes = ox.distance.nearest_nodes(G, ex, ey)

    edge_counts = Counter()

    logger.info("Routing %d trips...", len(trips))
    for u, v in tqdm(zip(u_nodes, v_nodes), total=len(trips)):
        try:
            route = nx.shortest_path(G, u, v, weight="length")
            edge_counts.update(zip(route[:-1], route[1:]))
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            continue

    logger.info(f"Trips: {len(trips)}")
    logger.info(f"Used unique node segments: {len(edge_counts)}")

    logger.info("Creating visualization...")
    for u, v, k in G.edges(keys=True):
        G[u][v][k]["count"] = edge_counts.get((u, v), 0)

    _nodes, edges = ox.graph_to_gdfs(
        G,
        nodes=True,
        edges=True,
    )
    edges_active = edges[edges["count"] > 0].copy()
    edges_active["linewidth"] = 0.5 + np.log1p(edges_active["count"])

    edges["linewidth"] = 0.5 + np.log1p(edges["count"])

    return edges, edges_active
