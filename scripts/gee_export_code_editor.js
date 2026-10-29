/**
 * ADEWI Rwanda — Google Earth Engine Code Editor Script
 * =====================================================
 *
 * HOW TO USE
 * ----------
 * 1. Open https://code.earthengine.google.com
 * 2. Paste this entire file into a new script.
 * 3. Click "Run" — you should see the provinces on the map and
 *    a preview table in the Console.
 * 4. Go to the "Tasks" panel (top right) and click "Run" next to
 *    the export task "ADEWI_Rwanda_provincial_timeseries".
 * 5. Wait for the export to complete (5–20 minutes depending on GEE load).
 * 6. Download provincial_timeseries.csv from your Google Drive
 *    (folder: ADEWI_Rwanda).
 * 7. Save the file to:  data/raw/provincial_timeseries.csv
 *    inside this repository.
 * 8. Re-run the Python pipeline:  python -m adewi
 *
 * OUTPUT COLUMNS
 * --------------
 * time, province, ndvi, evi, rainfall, soil_moisture, lst
 *
 * DATASET OPTIONS
 * ---------------
 * NDVI/EVI:  MOD13Q1 (250 m, 16-day) — DEFAULT
 *            MOD13A2 (1 km, 16-day)  — use if bandwidth is limited or
 *                                       export quota is hit (see below)
 * Rainfall:  CHIRPS/PENTAD           — DEFAULT (best for Africa)
 * Soil moist: FLDAS NOAH01           — DEFAULT (monthly, 10 km)
 *             ESA CCI Soil Moisture  — Alternative (daily, 0.25°)
 *                                      see commented section below
 * LST:        MOD11A2 (1 km, 8-day)  — DEFAULT
 */

// ─────────────────────────────────────────────────────────────────
// 1. Study area and time period
// ─────────────────────────────────────────────────────────────────

var start = '2018-01-01';
var end   = '2024-12-31';

// Province boundaries from FAO GAUL level-1.
// Alternative: geoBoundaries or HDX dataset for Rwanda — load as an
// ee.FeatureCollection from your Assets if preferred.
var provinces = ee.FeatureCollection('FAO/GAUL/2015/level1')
  .filter(ee.Filter.eq('ADM0_NAME', 'Rwanda'))
  .filter(ee.Filter.inList('ADM1_NAME', ['Eastern', 'Southern']));

Map.centerObject(provinces, 8);
Map.addLayer(provinces, {color: '2c3e50'}, 'Eastern + Southern Rwanda');

// ─────────────────────────────────────────────────────────────────
// 2. Vegetation indices — MODIS MOD13Q1 (250 m, 16-day)
//    Alternative: uncomment the MOD13A2 block below if you hit
//    export-size limits with MOD13Q1.
// ─────────────────────────────────────────────────────────────────

function scaleVI(img) {
  return img.select(['NDVI', 'EVI'])
    .multiply(0.0001)
    .rename(['ndvi', 'evi'])
    .copyProperties(img, ['system:time_start']);
}

// DEFAULT — 250 m resolution
var ndviCol = ee.ImageCollection('MODIS/061/MOD13Q1')
  .filterDate(start, end)
  .map(scaleVI);

/* ALTERNATIVE — 1 km resolution (lower data volume, faster export)
var ndviCol = ee.ImageCollection('MODIS/061/MOD13A2')
  .filterDate(start, end)
  .map(scaleVI);
*/

// ─────────────────────────────────────────────────────────────────
// 3. Rainfall — CHIRPS v2.0 pentad (5 km, 5-day sums)
//    Aggregated to 16-day sums to match MODIS composites.
// ─────────────────────────────────────────────────────────────────

var chirps = ee.ImageCollection('UCSB-CHG/CHIRPS/PENTAD')
  .filterDate(start, end)
  .select('precipitation');

// ─────────────────────────────────────────────────────────────────
// 4a. Soil moisture — FLDAS NOAH01 (10 km, monthly) [DEFAULT]
//     Units: m³/m³ (volumetric water content, top 10 cm)
// ─────────────────────────────────────────────────────────────────

var fldas = ee.ImageCollection('NASA/FLDAS/NOAH01/C/GL/M/V001')
  .filterDate(start, end)
  .select('SoilMoi00_10cm_tavg');

// Use FLDAS as the soil-moisture source by default:
var smCol = fldas;

/* 4b. ALTERNATIVE: ESA CCI Combined Soil Moisture (0.25°, daily)
 *   Pros: higher temporal resolution, longer record (1978–present).
 *   Cons: coarser spatial resolution; requires merging three products.
 *
 * var esaCci = ee.ImageCollection('ECMWF/ERA5_LAND/DAILY_AGGR')
 *   .filterDate(start, end)
 *   .select('volumetric_soil_water_layer_1')
 *   .map(function(img) {
 *     return img.rename('soil_moisture')
 *       .copyProperties(img, ['system:time_start']);
 *   });
 * var smCol = esaCci;
 *
 * NOTE: ESA CCI passive/active/combined products are available via the
 * Copernicus Climate Data Store (CDS) API and can be uploaded to GEE
 * as Assets. Follow the DE Africa guidance at:
 * https://docs.digitalearthafrica.org/en/latest/datasets/cci_soilmoisture.html
 */

// ─────────────────────────────────────────────────────────────────
// 5. Land Surface Temperature — MODIS MOD11A2 (1 km, 8-day)
//    Scale factor 0.02 converts raw DNs to Kelvin.
// ─────────────────────────────────────────────────────────────────

function scaleLST(img) {
  return img.select('LST_Day_1km')
    .multiply(0.02)
    .rename('lst')
    .copyProperties(img, ['system:time_start']);
}

var lstCol = ee.ImageCollection('MODIS/061/MOD11A2')
  .filterDate(start, end)
  .map(scaleLST);

// ─────────────────────────────────────────────────────────────────
// 6. Align all datasets to 16-day MODIS composite dates
//    and stack into a multi-band time series.
// ─────────────────────────────────────────────────────────────────

var viDates = ndviCol.aggregate_array('system:time_start');

var stack = ee.ImageCollection(viDates.map(function(t) {
  t = ee.Number(t);
  var tEnd = t.add(16 * 24 * 3600 * 1000);  // 16 days in ms

  // NDVI + EVI: mean of the 16-day composite window
  var vi = ndviCol.filterDate(t, tEnd).mean().rename(['ndvi', 'evi']);

  // Rainfall: SUM over 16 days (total mm)
  var rain = chirps.filterDate(t, tEnd)
    .select('precipitation')
    .sum()
    .rename('rainfall');

  // Soil moisture: MEAN (FLDAS is monthly so this picks the enclosing month)
  var smi = smCol.filterDate(t, tEnd)
    .mean()
    .rename('soil_moisture');

  // LST: MEAN over any overlapping 8-day composites
  var lsti = lstCol.filterDate(t, tEnd)
    .mean()
    .rename('lst');

  return vi.addBands(rain).addBands(smi).addBands(lsti)
    .set('system:time_start', t);
}));

// ─────────────────────────────────────────────────────────────────
// 7. Reduce each band to provincial mean and build the export table
//    Reduction scale: 5,000 m (reasonable for both 250 m and 10 km inputs)
// ─────────────────────────────────────────────────────────────────

var table = stack.map(function(img) {
  return provinces.map(function(feat) {
    var stats = img.reduceRegion({
      reducer: ee.Reducer.mean(),
      geometry: feat.geometry(),
      scale: 5000,
      maxPixels: 1e9,
      bestEffort: true
    });
    return feat.set(stats)
      .set('time', img.date().format('YYYY-MM-dd'))
      .set('province', feat.get('ADM1_NAME'));
  });
}).flatten()
  .select(['time', 'province', 'ndvi', 'evi', 'rainfall', 'soil_moisture', 'lst']);

// ─────────────────────────────────────────────────────────────────
// 8. Preview and export
// ─────────────────────────────────────────────────────────────────

print('Export task created. Start it from the Tasks panel (top right).');
print('First 5 rows:', table.limit(5));

Export.table.toDrive({
  collection: table,
  description: 'ADEWI_Rwanda_provincial_timeseries',
  folder: 'ADEWI_Rwanda',
  fileNamePrefix: 'provincial_timeseries',
  fileFormat: 'CSV'
});

// ─────────────────────────────────────────────────────────────────
// 9. After downloading:
//    - Open provincial_timeseries.csv in Excel or a text editor
//    - Verify columns: time, province, ndvi, evi, rainfall, soil_moisture, lst
//    - Check for missing values (null) in any column
//    - Save as: data/raw/provincial_timeseries.csv  (repository root)
//    - Run:  python -m adewi
// ─────────────────────────────────────────────────────────────────
