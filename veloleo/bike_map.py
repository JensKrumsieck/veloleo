import logging
from matplotlib import pyplot as plt
from matplotlib.colors import LogNorm
import numpy as np
import osmnx as ox
import networkx as nx
from pyproj import Transformer
from tqdm import tqdm
from matcher import Trip
from collections import Counter

logger = logging.getLogger("veloleo")


def save_geojson(edges_active, output_file: str = "data/bike_heatmap.geojson"):
    edges_active = edges_active.to_crs("EPSG:4326")
    columns_to_keep = ["count", "geometry"]
    geojson_df = edges_active[columns_to_keep]
    geojson_df.to_file(output_file, driver="GeoJSON")

    logger.info("Saved GeoJSON to %s", output_file)


def save_geopkg(edges_active, output_file: str = "data/bike_heatmap.gpkg"):
    edges_active.to_crs("EPSG:4326")
    columns_to_keep = ["count", "geometry"]
    geopkg_df = edges_active[columns_to_keep]
    geopkg_df.to_file(output_file, layer="trips", driver="GPKG")

    logger.info("Saved GeoPackage to %s", output_file)


def plot_heatmap_data(edges, edges_active, output_file: str = "data/bike_heatmap.png"):
    fig, ax = plt.subplots(figsize=(12, 12), facecolor="#111111")
    edges.plot(ax=ax, color="#2a2a2a", linewidth=0.5, zorder=1)
    if not edges_active.empty:
        edges_active.plot(
            ax=ax,
            column="count",
            cmap="inferno",
            linewidth=0.5,  # Use your dynamic log scaling!
            norm=LogNorm(vmin=1, vmax=edges_active["count"].max()),
            legend=True,
            zorder=2,
        )

    ax.set_axis_off()

    fig.savefig(
        output_file,
        dpi=300,
        bbox_inches="tight",
        facecolor=fig.get_facecolor(),
    )

    plt.close(fig)

    logger.info("Saved heatmap to %s", output_file)


def find_routes(trips: list[Trip]):
    logger.info("Downloading bike network...")

    G = ox.graph_from_place("Braunschweig, Germany", network_type="bike")
    G = ox.project_graph(G)

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
