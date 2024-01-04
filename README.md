# AIMS

Python interface for working with Map Service data from ArcGIS REST APIs.

## Purpose

AIMS, or the ArcGIS Interface for Map Services, seeks to provide a simple tool to extract data from ArcGIS REST API Map Services. One common difficulty in working with Map Services is the max record count which requires you to iteratively query subsets of data and then aggregate the resulting outputs into a single dataset. With AIMS, this is taken care of and in turn, a simplified interface allows users to quickly get data. Users also have the option to make concurrent requests to retrieve the data, speeding up the process even futher.

## Python

To install `aims`, use the following command:

```bash
pip install git+https://github.com/lukezaruba/aims.git
```

Currently, it is only available by installing via pip from GitHub.

With the Python package, users are able to access the data and metadata in a number of ways, such as:

- Data as a GeoDataFrame
- Data as a Python Dictionary (JSON)
- Schema as a Python Dictionary (JSON)
- Total Number of Records as an Integer
- Max Record Count as an Integer

Users can also save the data locally as a GeoJSON or as a Shapefile. The schema can be saved as a JSON.

The only argument needed is a URL for the Map Service layer, which whould be structured something like:

`https://maps.co.ramsey.mn.us/arcgis/rest/services/OpenData/OpenData/MapServer/11`

NOTE: It is important that the URL ends in the layer number, otherwise the URL might not successfully validate.

An additional argument that is optional is whether or not to make requests concurrently. By default, requests are made concurrently, but this behavior can be disabled.

Several other optional keyword arguments exist for querying the data when making a request. They follow the query parameters used by the ArcGIS REST API. The options available include:

- `where`
- `text`
- `objectIds`
- `geometry`
- `geometryType`
- `inSR`
- `spatialRel`
- `outFields`
- `outSR`

By default, users do not need to pass any values in for these keyword arguments, and all records and fields will be returned.

To learn more about these parameters, see Esri's [documentation](https://developers.arcgis.com/rest/services-reference/enterprise/query-map-service-layer-.htm).

To view documentation, use the following command:

```python
from aims import AIMS

help(AIMS)
```

A basic implementation can be seen below:

```python
# Import AIMS
from aims import AIMS

url = "https://maps.co.ramsey.mn.us/arcgis/rest/services/OpenData/OpenData/MapServer/11"

# Instantiate AIMS object and make request(s)
parcels = AIMS(url)

# See total record count
print(parcels.n_records)

# See max record count for single query/request
print(parcels.max_record_count)

# See schema of dataset
print(parcels.schema)

# See if pagination is supported
print(parcels.pagination_supported)

# See Esri geometry type of data
print(parcels.geometry_type)

# Get data as dict
parcels.data

# Get data as GeoDataFrame
parcels.gdf

# Export data as Shapefile
parcels.to_shapefile("file/path/to/my_shapefile.shp")

# Export data as GeoJSON
parcels.to_geojson("file/path/to/my_geojson.geojson")

# Export schema as JSON
import json

with open("file/path/to/schema.json", "w") as file:
    file.write(json.dumps(parcels.schema))
```

Here is an example that disables concurrent requests:

```python
# Import AIMS
from aims import AIMS

url = "https://maps.co.ramsey.mn.us/arcgis/rest/services/OpenData/OpenData/MapServer/11"

# Instantiate AIMS object and make request(s)
parcels = AIMS(url, concurrent=False)
```

Lastly, here is an example that uses ArcGIS REST API query parameters:

```python
# Import AIMS
from aims import AIMS

url = "https://maps.co.ramsey.mn.us/arcgis/rest/services/OpenData/OpenData/MapServer/11"

# Instantiate AIMS object and make request(s)
parcels = AIMS(url,
    where="StreetName = 'KELLOGG' AND ParcelAcresPolygon > 5", # Filtering to road and lot size
    outFields="ParcelID, Shape" # Only returning ParcelID and Shape fields
)
```

## Command Line Tool

When using `pip install` to download the Python package, a command line tool called `aims` is also installed.

In the same envrionment where `aims` is installed, users will be able to carry out requests directly from the command line rather than through Python.

Just run:

```bash
aims --help
```

This will show all of the various options to carry out requests.

One important thing to note is that be default, requests are not made concurrently with the command line tool.

It should also be noted that the query parameters are more limited with the command line tool. Currently only the following parameters are supported:

- `where`
- `outFields`
- `outSR`

An example implementation can be found below, which saves the data as a GeoJSON and Shapefile and the schema as a JSON file:

```bash
aims "https://maps.co.ramsey.mn.us/arcgis/rest/services/OpenData/OpenData/MapServer/11" -c -gjs my_output.geojson -shp my_output.shp -sc my_schema.json
```
