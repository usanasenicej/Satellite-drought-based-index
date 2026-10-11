"""Digital Earth Africa Sandbox helper (run inside https://sandbox.digitalearthafrica.org).

This is a template, not executed by the local pipeline. Copy into a Sandbox
notebook after logging in. DE Africa already hosts CHIRPS and several
vegetation products for Africa; MODIS collections can also be opened via
the Sandbox STAC / datacube.
"""

TEMPLATE = r'''
# Run this cell inside the Digital Earth Africa Sandbox

import datacube
import pandas as pd
import geopandas as gpd

dc = datacube.Datacube(app="adewi-rwanda")

# Example: CHIRPS rainfall over a bounding box covering Eastern + Southern Rwanda
query = dict(
    x=(29.35, 30.90),
    y=(-2.85, -1.05),
    time=("2018-01-01", "2024-12-31"),
    output_crs="EPSG:4326",
    resolution=(-0.05, 0.05),
)

# Product names change; list with: dc.list_products()
# rainfall = dc.load(product="rainfall_chirps_monthly", **query)

print("Use dc.list_products() to confirm current CHIRPS / NDVI product names,")
print("then spatial-mean by province polygons and export CSV with columns:")
print("time, province, ndvi, evi, rainfall, soil_moisture, lst")
'''

if __name__ == "__main__":
    print(TEMPLATE)
