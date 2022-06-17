#!/usr/bin/env python3
# Copyright (C) 2022  Karime Ochoa Jacinto
#                     Luis Aaron Nieto Cruz
#                     Anton Pashkov
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""Cyclops Spider

This module fetches star data from SIMBAD on any given constellation and sends
collected data to a PostgreSQL database.
"""

import json
import psycopg2
import re
from astropy.table import Column
from astroquery.simbad import Simbad
from datetime import datetime, timezone
from configparser import ConfigParser
from sys import argv


def query_constellation(name):
    """Queries Simbad for the stars of a given constellation and returns a
    table from the results."""

    # Set fields to include in the result
    custom = Simbad()
    custom.add_votable_fields("typed_id", "ra", "dec", "pmra", "pmdec", "plx")
    custom.remove_votable_fields("main_id", "coordinates")

    # Parse JSON file for the given constellation and interpret data
    with open("constellations.json", "r") as f:
        items = json.load(f)[name]
        stars = list(items.keys())
        neighbors = list(items.values())
        for i in range(len(neighbors)):
            neighbors[i] = ";".join(neighbors[i])

    # Generate an astropy table
    table = custom.query_objects(stars)

    # Remove script_number_id column
    table.remove_column("SCRIPT_NUMBER_ID")

    # Add time, constellation and neighbors columns
    constellation = Column(name="CONSTELLATION", data=name)
    time = Column(name="TIME", data=datetime.now(timezone.utc))
    neighbors = Column(name="NEIGHBORS", data=neighbors)
    table.add_columns([constellation, time, neighbors])

    return table


def config(filename, section):
    """Reads configuration file."""

    # Create a parser
    parser = ConfigParser()

    # Read config file
    parser.read(filename)

    # Get section
    db = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            db[param[0]] = param[1]
    else:
        raise Exception(
            "Section {0} not found in the {1} file".format(section, filename)
        )

    return db


def verify(table):
    """Verifies the integrity of the astropy table created with the query_
    constellation function; returns True if verification is successful, and
    returns False otherwise."""

    # Verify column names
    if table.colnames != [
        "TYPED_ID",
        "RA",
        "DEC",
        "PMRA",
        "PMDEC",
        "PLX_VALUE",
        "CONSTELLATION",
        "TIME",
        "NEIGHBORS",
    ]:
        return False

    # Verify columns with numerical values
    for column in ["PMRA", "PMDEC", "PLX_VALUE"]:
        if table[column].dtype != "float64":
            return False

    # Regex for right ascension and declination verification
    ra_regex = r"[0-9]{2} [0-9]{2} [0-9]{2}.[0-9]{4}"
    dec_regex = r"(\+|-)[0-9]{2} [0-9]{2} [0-9]{2}.[0-9]{3}"

    # Open JSON file to verify star, constellation and neighbor names
    with open("constellations.json", "r") as f:
        json_dict = json.load(f)

    # Verify the rest of the data row by row
    for row in table:

        # Verify right ascension and declination
        if (
            bool(re.match(ra_regex, row["RA"])) is False
            or bool(re.match(dec_regex, row["DEC"])) is False
        ):
            return False

        # Verify datetime
        if type(row["TIME"]) != datetime:
            return False

        # Verify constellation name
        const = row["CONSTELLATION"]
        if const not in json_dict.keys():
            return False

        # Verify star name
        star = row["TYPED_ID"]
        if star not in json_dict[const].keys():
            return False

        # Verify neighbor names
        neighbors = row["NEIGHBORS"].split(";")
        if neighbors != json_dict[const][star]:
            return False

    return True


def send_to_database(table, filename):
    """Connects to the PostgreSQL database server, and sends collected star
    info to database."""

    conn = None
    try:
        # Read connection parameters
        params = config(filename=filename, section="postgresql")

        # Connect to the PostgreSQL server
        conn = psycopg2.connect(**params)

        # Create a cursor
        cur = conn.cursor()

        # Send star info to database
        sql = (
            "INSERT INTO stars(name, ra, dec, pm_ra, pm_dec, parallax, "
            "constellation, time, neighbors) VALUES (%s, %s, %s, %s, %s, %s, "
            "%s, %s, %s);"
        )
        cur.executemany(sql, list(table.iterrows()))
        conn.commit()

        # Close the communication with the PostgreSQL
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()


def main(constellation, conf_dir):
    """Driver code."""

    # Fetch constellation info
    const_data = query_constellation(constellation)

    # Verify integrity
    while verify(const_data) is False:
        const_data = query_constellation(constellation)

    # Send to database if verification is successful
    send_to_database(table=const_data, filename=conf_dir)


if __name__ == "__main__":
    # Script syntax:
    # ./spider.py [constellation]
    main(argv[1], "../config.ini")
