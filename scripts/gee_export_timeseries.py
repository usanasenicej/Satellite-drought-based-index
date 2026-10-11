"""Export provincial 16-day means of NDVI, EVI, CHIRPS, FLDAS soil moisture and MODIS LST.

Prerequisites:
  1. pip install earthengine-api
  2. earthengine authenticate
  3. A Google Cloud / Earth Engine project with export rights

The script writes a CSV to Google Drive (folder ADEWI_Rwanda). Download it to
data/raw/provincial_timeseries.csv (columns: time, province, ndvi, evi, rainfall,
soil_moisture, lst) and re-run the local pipeline.
"""

from __future__ import annotations

# earthengine-api is optional; this file is meant to be run after the student
# has a GEE account. The rest of the repository does not import this module.

GEE_JS_EQUIVALENT = "scripts/gee_export_code_editor.js"


def main() -> None:
    try:
        import ee
    except ImportError as exc:
        raise SystemExit(
            "Install earthengine-api and authenticate first:\n"
            "  pip install earthengine-api\n"
            "  earthengine authenticate\n"
        ) from exc

    ee.Initialize()

    start, end = "2018-01-01", "2024-12-31"
    provinces = ee.FeatureCollection("FAO/GAUL/2015/level1").filter(
        ee.Filter.And(
            ee.Filter.eq("ADM0_NAME", "Rwanda"),
            ee.Filter.inList("ADM1_NAME", ["Eastern", "Southern"]),
        )
    )

    def scale_modis_vi(img):
        return (
            img.select(["NDVI", "EVI"])
            .multiply(0.0001)
            .copyProperties(img, ["system:time_start"])
        )

    ndvi = (
        ee.ImageCollection("MODIS/061/MOD13Q1")
        .filterDate(start, end)
        .map(scale_modis_vi)
        .select(["NDVI", "EVI"])
    )

    chirps = (
        ee.ImageCollection("UCSB-CHG/CHIRPS/PENTAD")
        .filterDate(start, end)
        .select("precipitation")
    )

    sm = (
        ee.ImageCollection("NASA/FLDAS/NOAH01/C/GL/M/V001")
        .filterDate(start, end)
        .select("SoilMoi00_10cm_tavg")
    )

    def scale_lst(img):
        qc = img.select("QC_Day")
        lst = img.select("LST_Day_1km").multiply(0.02)
        # Keep pixels with bits 0-1 == 0 (good quality) when possible
        return lst.rename("LST").copyProperties(img, ["system:time_start"])

    lst = ee.ImageCollection("MODIS/061/MOD11A2").filterDate(start, end).map(scale_lst)

    vi_dates = ndvi.aggregate_array("system:time_start")

    def mosaic_sum(collection, start_ms, end_ms, band, out_name, reducer):
        return (
            collection.filterDate(start_ms, end_ms)
            .select(band)
            .reduce(reducer)
            .rename(out_name)
        )

    def compose_one(t):
        t = ee.Number(t)
        t_end = t.add(16 * 24 * 3600 * 1000)
        vi = ndvi.filterDate(t, t_end).mean().rename(["ndvi", "evi"])
        rain = mosaic_sum(chirps, t, t_end, "precipitation", "rainfall", ee.Reducer.sum())
        smi = mosaic_sum(sm, t, t_end, "SoilMoi00_10cm_tavg", "soil_moisture", ee.Reducer.mean())
        lsti = mosaic_sum(lst, t, t_end, "LST", "lst", ee.Reducer.mean())
        img = vi.addBands(rain).addBands(smi).addBands(lsti).set("system:time_start", t)
        return img

    stack = ee.ImageCollection(vi_dates.map(compose_one))

    def reduce_province(img):
        def per_feat(feat):
            stats = img.reduceRegion(
                reducer=ee.Reducer.mean(),
                geometry=feat.geometry(),
                scale=5000,
                maxPixels=1e9,
                bestEffort=True,
            )
            return feat.set(stats).set("time", img.date().format("YYYY-MM-dd"))

        return provinces.map(per_feat)

    table = stack.map(reduce_province).flatten()
    table = table.select(["time", "ADM1_NAME", "ndvi", "evi", "rainfall", "soil_moisture", "lst"])
    table = table.map(lambda f: f.set("province", f.get("ADM1_NAME")))

    task = ee.batch.Export.table.toDrive(
        collection=table,
        description="ADEWI_Rwanda_provincial_timeseries",
        folder="ADEWI_Rwanda",
        fileNamePrefix="provincial_timeseries",
        fileFormat="CSV",
    )
    task.start()
    print("Export started. Check the Earth Engine Tasks tab / Google Drive folder ADEWI_Rwanda.")
    print("When complete, copy the CSV to data/raw/provincial_timeseries.csv")
    print("and ensure the province column is named 'province' (Eastern / Southern).")


if __name__ == "__main__":
    main()
