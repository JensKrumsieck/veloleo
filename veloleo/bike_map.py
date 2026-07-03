import logging
from matplotlib import pyplot as plt
from matplotlib.colors import LogNorm

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

