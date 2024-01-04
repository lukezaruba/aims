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

"""cli.py: Implements command line interface for using AIMS."""

import json

import click

from aims import AIMS


@click.command()
@click.argument("url", type=click.Path(exists=False))
@click.option("--concurrent", "-c", is_flag=True)
@click.option("--where", "-w", default="1=1", show_default=True)
@click.option("--out-fields", "-f", default="*", show_default=True)
@click.option("--out-sr", "-crs", default="")
@click.option("--geojson", "-gjs", type=click.Path(exists=False))
@click.option("--shapefile", "-shp", type=click.Path(exists=False))
@click.option("--schema", "-sc", type=click.Path(exists=False))
def cli(url, concurrent, where, out_fields, out_sr, geojson, shapefile, schema) -> None:
    # Instantiate AIMS object
    instance = AIMS(url, concurrent, where=where, outFields=out_fields, outSR=out_sr)

    if geojson:
        # Check file extension
        if geojson.lower().endswith(".geojson"):
            out_gjs = geojson

        else:
            out_gjs = geojson + ".geojson"

        # Export
        instance.to_geojson(out_gjs)

        # Echo
        click.echo(f"GeoJSON saved at {out_gjs}")

    if shapefile:
        # Check file extension
        if shapefile.lower().endswith(".shp"):
            out_shp = shapefile

        else:
            out_shp = shapefile + ".shp"

        # Export
        instance.to_shapefile(out_shp)

        # Echo
        click.echo(f"Shapefile saved at {out_shp}")

    if schema:
        # Check file extension
        if schema.lower().endswith(".json"):
            out_schema = schema

        else:
            out_schema = schema + ".json"

        # Export
        with open(out_schema, "w") as file:
            file.write(json.dumps(instance.schema))

        # Echo
        click.echo(f"Schema saved at {schema}")

    click.echo("Processing complete.")
    click.echo(f"Retreived {instance.n_records} records.")
