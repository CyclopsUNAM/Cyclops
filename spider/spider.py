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
    constellation = Column(name="constellation", data=name)
    time = Column(name="time", data=datetime.now(timezone.utc))
    neighbors = Column(name="neighbors", data=neighbors)
    table.add_columns([constellation, time, neighbors])

    return table


def db_config(filename="database.ini", section="postgresql"):
    """Reads database configuration file."""

    # Create a parser
    parser = ConfigParser()

    # Read config file
    parser.read(filename)

    # Get section, default to postgresql
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


def send_to_database(table, f="database.ini"):
    """Connect to the PostgreSQL database server, and sends collected star info
    to database."""

    conn = None
    try:
        # Read connection parameters
        params = db_config(filename=f)

        # Connect to the PostgreSQL server
        print("Connecting to the PostgreSQL database...")
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
            print("Database connection closed.")


def main(constellation, database_dir):
    """Driver code."""

    # Fetch constellation info
    const_data = query_constellation(constellation)

    # Verify integrity

    # Send to database
    send_to_database(const_data, f=database_dir)


if __name__ == "__main__":
    # Script syntax:
    # python3 spider.py [constellation]
    main(argv[1], "../database/database.ini")
