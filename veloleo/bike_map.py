import json
import logging
from pathlib import Path
import geojsoncontour
from matplotlib import pyplot as plt
from matplotlib.colors import LogNorm
from events import Event
import osmnx as ox
import networkx as nx
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
from scipy.stats import gaussian_kde
import numpy as np

logger = logging.getLogger("veloleo")

_graph_cache: nx.MultiDiGraph | None = None


def get_graph() -> nx.MultiDiGraph:
    global _graph_cache

    if _graph_cache is None:
        logger.info("Downloading bike network...")

        G = ox.graph_from_place("Braunschweig, Germany", network_type="bike")
        G = ox.project_graph(G)
        _graph_cache = G

    return _graph_cache


def save_geojson(edges_active, output_file: str = "data/bike_heatmap.geojson"):
    edges_active = edges_active.to_crs("EPSG:4326")
    columns_to_keep = ["count", "geometry"]
    geojson_df = edges_active[columns_to_keep]
    geojson_df.to_file(output_file, driver="GeoJSON")

    logger.info("Saved GeoJSON to %s", output_file)


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


def plot_event_heatmaps(
    events: list[Event], output_file: str = "data/event_heatmaps.png"
):
    data = [
        {
            "type": e.type,
            "time": e.time,
            "bike_id": e.bike_id,
            "lat": e.lat,
            "lon": e.lon,
            "station_id": e.station_id,
        }
        for e in events
    ]

    df = pd.DataFrame(data)

    geometry = [Point(xy) for xy in zip(df["lon"], df["lat"])]
    gdf = gpd.GeoDataFrame(df, geometry=geometry, crs="EPSG:4326")

    filename = Path(output_file).parent / "events.geojson"
    gdf.to_file(filename, driver="GeoJSON")
    logger.info("Saved GeoJSON to %s", filename)

    gdf_dep = gdf[gdf["type"] == "departure"]
    gdf_arr = gdf[gdf["type"] == "arrival"]

    if gdf_dep.empty or gdf_arr.empty:
        logger.warning("Need both departures and arrivals to map transition density.")
        return

    x_min, x_max = gdf.geometry.x.min(), gdf.geometry.x.max()
    y_min, y_max = gdf.geometry.y.min(), gdf.geometry.y.max()
    X, Y = np.meshgrid(np.linspace(x_min, x_max, 200), np.linspace(y_min, y_max, 200))

    Z_dep = kde_surface(gdf_dep, X, Y)
    Z_arr = kde_surface(gdf_arr, X, Y)
    Z_transition = Z_dep - Z_arr

    fig, axes = plt.subplots(1, 3, figsize=(18, 5))

    densities = [Z_dep, Z_arr, Z_transition]
    cmaps = ["Oranges", "Purples", "RdBu_r"]
    titles = [
        "Departures (Sources)",
        "Arrivals (Sinks)",
        "Transition Density ",
    ]
    labels = [
        "Departures (Sources)",
        "Arrivals (Sinks)",
        "<-- Net Arrivals (Sinks) | Net Departures (Sources) --> ",
    ]
    gdf = [gdf_dep, gdf_arr, gdf]

    for i, Z in enumerate(densities):
        # For the transition surface, center vmin/vmax symmetrically at 0
        if i == 2:
            vmax = np.max(np.abs(Z))
            vmin = -vmax
        else:
            vmin = 0
            vmax = np.max(Z)

        contour = axes[i].contourf(
            X,
            Y,
            Z,
            levels=15,
            cmap=cmaps[i],
            vmin=vmin,
            vmax=vmax,
            alpha=0.6,
        )

        cbar = fig.colorbar(contour, ax=axes[i], shrink=0.7)
        cbar.set_label(labels[i])

        # plot events as points
        gdf[i].plot(ax=axes[i], color="black", markersize=1, alpha=0.1, label="Events")
        axes[i].set_title(titles[i], fontsize=12, fontweight="bold")
        axes[i].set_axis_off()

    fig.savefig(
        output_file,
        dpi=300,
        bbox_inches="tight",
        facecolor=fig.get_facecolor(),
    )

    plt.close(fig)
    logger.info("Saved event heatmaps to %s", output_file)


def kde_surface(gdf: gpd.GeoDataFrame, X, Y):
    positions = np.vstack([X.ravel(), Y.ravel()])

    kde = gaussian_kde(np.vstack([gdf.geometry.x, gdf.geometry.y]))
    Z = np.reshape(kde(positions).T, X.shape)

    return Z
