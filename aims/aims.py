#!/usr/bin/env python
# -*- coding: utf-8 -*-

# MIT License
#
# Copyright (c) 2024 Luke Zaruba
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""aims.py: Implements interface for working with ArcGIS REST API Map Services."""

import os
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Tuple, Union
from urllib.parse import urlparse

from geopandas import GeoDataFrame
from requests import get


class AIMS:
    def __init__(self, url: str, concurrent: bool = True, **kwargs: Any) -> None:
        """
        Instantiates AIMS object.

        Args:
            url (str): Input ArcGIS REST API Map Service.
            concurrent (bool, optional): Determines whether or not to make requests concurrently. Defaults to True.
        """
        # Validate URL
        self.url = self._validate_url(url)
        self.query_url = self.url + "/Query"

        # Get kwargs
        self._query_where = kwargs.get("where", "1=1")
        self._query_text = kwargs.get("text", "")
        self._query_objectIds = kwargs.get("objectIds", "")
        self._query_geometry = kwargs.get("geometry", "")
        self._query_geometryType = kwargs.get("geometryType", "")
        self._query_inSR = kwargs.get("inSR", "")
        self._query_spatialRel = kwargs.get("spatialRel", "")
        self._query_outFields = kwargs.get("outFields", "*")
        self._query_outSR = kwargs.get("outSR", "")

        # Get metadata
        (
            self.n_records,
            self.max_record_count,
            self.schema,
            self.pagination_supported,
            self.geometry_type,
        ) = self._get_metadata()

        # Compile list of URL params
        self._request_urls = [
            (i, self.max_record_count)
            for i in range(0, self.n_records, self.max_record_count)
        ]

        # Make requests concurrently or not
        if concurrent:
            with ThreadPoolExecutor() as executor:
                self._raw_responses = list(
                    executor.map(self._make_single_request, self._request_urls)
                )

        else:
            # Using normal map
            self._raw_responses = list(
                map(self._make_single_request, self._request_urls)
            )

        # With all data, combine
        initial_json = self._raw_responses[0].json()
        features = initial_json["features"]

        for resp in range(1, len(self._raw_responses)):
            features += self._raw_responses[resp].json()["features"]

        self.data = initial_json

        # Convert to GDF
        if self._query_outSR != "":
            self.gdf = GeoDataFrame.from_features(
                self.data["features"], crs=self._query_outSR
            )

        else:
            self.gdf = GeoDataFrame.from_features(self.data["features"], crs=4236)

    @staticmethod
    def _validate_url(url: str) -> str:
        """
        Determines validity of URL and make corrections.

        Args:
            url (str): Input URL

        Raises:
            ValueError: Unsuccessful validation of URL

        Returns:
            str: Validated URL
        """
        # Parse URL
        parsed = urlparse(url)

        split_path = parsed.path.split("/")

        # Find layer number
        for i in range(-1, -1 * len(split_path), -1):
            try:
                if isinstance(int(split_path[i]), int):
                    if i + 1 == 0:
                        return f"{parsed.scheme}://{parsed.netloc + '/'.join(split_path[:])}"
                    else:
                        return f"{parsed.scheme}://{parsed.netloc + '/'.join(split_path[: i + 1])}"
            except:
                pass

        raise ValueError(
            "Unable to validate URL. Should be URL of format: https://<ARCGIS_SERVER>/arcgis/rest/services/<FOLDER(S)>/MapServer/<LAYER_NUMBER>"
        )

    def to_shapefile(self, output_file: Union[str, os.PathLike]) -> None:
        """
        Exports data as shapefile.

        Args:
            output_file (Union[str, os.PathLike]): File path of output, ending in extension "shp"
        """
        self.gdf.to_file(output_file)

    def to_geojson(self, output_file: Union[str, os.PathLike]) -> None:
        """
        Exports data as GeoJSON.

        Args:
            output_file (Union[str, os.PathLike]): File path of output, ending in extension "geojson"
        """
        self.gdf.to_file(output_file, driver="GeoJSON")

    def _get_metadata(self) -> Tuple[int, int, dict, bool, str]:
        """
        Retrieves metadata needed to carry out request.

        Returns:
            Tuple[int, int, dict, bool, str]: Total number of records (int), max record count (int), schema (dict), pagination support (bool), & geometry type (str)
        """
        # Request metadata
        metadata_response = get(self.url, params={"f": "json"})

        metadata = metadata_response.json()

        max_record_count = int(metadata["maxRecordCount"])
        supports_pagination = metadata["advancedQueryCapabilities"][
            "supportsPagination"
        ]
        schema = metadata["fields"]

        geometry_type = metadata["geometryType"]

        # Find total record count via query
        total_record_response = get(
            self.query_url,
            params={"returnCountOnly": "true", "where": "1=1", "f": "json"},
        )
        total_record_count = int(total_record_response.json()["count"])

        return (
            total_record_count,
            max_record_count,
            schema,
            supports_pagination,
            geometry_type,
        )

    def _make_single_request(self, pagination_params: tuple) -> None:
        """
        Makes a single request given a set of params for paginating through data.

        Args:
            pagination_params (tuple): Offset and record count for pagination.
        """
        # Set up params
        params = {
            "where": self._query_where,
            "text": self._query_text,
            "geometry": self._query_geometry,
            "geometryType": self._query_geometryType,
            "inSR": self._query_inSR,
            "spatialRel": self._query_spatialRel,
            "outFields": self._query_outFields,
            "outSR": self._query_outSR,
            "resultOffset": pagination_params[0],
            "resultRecordCount": pagination_params[1],
            "f": "geojson",
        }

        # Make request
        resp = get(self.query_url, params=params)

        # Append data
        return resp
