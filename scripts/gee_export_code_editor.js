/**
 * ADEWI Rwanda — Google Earth Engine Code Editor script
 *
 * 1. Open https://code.earthengine.google.com
 * 2. Paste this file
 * 3. Run, then start the export task
 * 4. Download provincial_timeseries.csv from Google Drive
 * 5. Save as data/raw/provincial_timeseries.csv in this repository
 *
 * Columns produced: time, province, ndvi, evi, rainfall, soil_moisture, lst
 */

var start = '2018-01-01';
var end = '2024-12-31';

var provinces = ee.FeatureCollection('FAO/GAUL/2015/level1')
  .filter(ee.Filter.eq('ADM0_NAME', 'Rwanda'))
  .filter(ee.Filter.inList('ADM1_NAME', ['Eastern', 'Southern']));

Map.centerObject(provinces, 8);
Map.addLayer(provinces, {color: 'black'}, 'Study provinces');

function scaleVI(img) {
  return img.select(['NDVI', 'EVI']).multiply(0.0001)
    .copyProperties(img, ['system:time_start']);
}

var ndvi = ee.ImageCollection('MODIS/061/MOD13Q1')
  .filterDate(start, end)
  .map(scaleVI);

var chirps = ee.ImageCollection('UCSB-CHG/CHIRPS/PENTAD')
  .filterDate(start, end)
  .select('precipitation');

var sm = ee.ImageCollection('NASA/FLDAS/NOAH01/C/GL/M/V001')
  .filterDate(start, end)
  .select('SoilMoi00_10cm_tavg');

function scaleLST(img) {
  return img.select('LST_Day_1km').multiply(0.02).rename('LST')
    .copyProperties(img, ['system:time_start']);
}

var lst = ee.ImageCollection('MODIS/061/MOD11A2')
  .filterDate(start, end)
  .map(scaleLST);

var viDates = ndvi.aggregate_array('system:time_start');

var stack = ee.ImageCollection(viDates.map(function (t) {
  t = ee.Number(t);
  var tEnd = t.add(16 * 24 * 3600 * 1000);
  var vi = ndvi.filterDate(t, tEnd).mean().rename(['ndvi', 'evi']);
  var rain = chirps.filterDate(t, tEnd).select('precipitation')
    .sum().rename('rainfall');
  var smi = sm.filterDate(t, tEnd).select('SoilMoi00_10cm_tavg')
    .mean().rename('soil_moisture');
  var lsti = lst.filterDate(t, tEnd).select('LST')
    .mean().rename('lst');
  return vi.addBands(rain).addBands(smi).addBands(lsti)
    .set('system:time_start', t);
}));

var table = stack.map(function (img) {
  return provinces.map(function (feat) {
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
}).flatten().select(['time', 'province', 'ndvi', 'evi', 'rainfall', 'soil_moisture', 'lst']);

Export.table.toDrive({
  collection: table,
  description: 'ADEWI_Rwanda_provincial_timeseries',
  folder: 'ADEWI_Rwanda',
  fileNamePrefix: 'provincial_timeseries',
  fileFormat: 'CSV'
});

print('Export task created. Start it from the Tasks panel.');
print(table.limit(5));
