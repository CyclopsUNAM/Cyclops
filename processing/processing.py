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
"""Cyclops Processing

This module provides the function to be wrapped by Gradio. For more details,
see the function's doctstring.
"""

import os
from configparser import ConfigParser

import psycopg2
import matplotlib.pyplot as plt
import numpy as np
from astropy import units as u
from astropy.coordinates import SkyCoord, Distance
from astropy.constants import c
from astropy.table import Table


def config(filename, section):
    """Reads configuration files."""

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


def get_most_recent(constellation, f="database.ini"):
    """Connects to the PostgreSQL database server, and fetches the most recent
    data on the given constellation."""

    conn = None
    try:
        # Read connection parameters
        params = config(filename=f, section="postgresql")

        # Connect to the PostgreSQL server
        print("Connecting to the PostgreSQL database...")
        conn = psycopg2.connect(**params)

        # Create a cursor
        cur = conn.cursor()

        # Fetch most recent data on the given constellation
        sql = (
            "SELECT * FROM stars WHERE time = (SELECT MAX(time) FROM stars "
            "WHERE constellation = %s);"
        )
        cur.execute(sql, (constellation,))
        result = cur.fetchall()
        columns = [
            "TYPED_ID",
            "RA",
            "DEC",
            "PMRA",
            "PMDEC",
            "PLX_VALUE",
            "CONSTELLATION",
            "TIME",
            "NEIGHBORS",
        ]

        # Close the communication with the PostgreSQL
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
            print("Database connection closed.")
            return Table(rows=result, names=columns)


def processing(constellation, dmill, viewtype):
    """Runs spider on a remote host on a given constellation, calculates the
    new coordinates (in accordance to dmill and viewtype), and returns a
    matplotlib figure of the constellation. Make sure to create a
    processing.ini file in the current directory with this format:

    [processing]
    user=[name]
    host=[ip address]
    route=[complete path to the directory where spider.py is located]

    Arguments:
    - constellation (str). Name of the constellation to visualize.
    - dmill (int). Sets how many millennia to the future or the past to show
    the given constellation.
    - viewtype (str; "Apparent" or "Real"). If set to "Apparent", the function
    will return the constellation as seen from Earth; if set to "Real", it
    will plot the constellation as it actually looks like (by taking into
    account the delay from the light reaching Earth).
    """

    # Read processing configuration file
    conf = config("processing.ini", "processing")
    user, host, route = conf["user"], conf["host"], conf["route"]

    # Run spider on the constellation
    command = f'ssh {user}@{host} "cd {route}; ./spider.py {constellation}"'
    os.system(command)

    # Get most recent data on the given constellation and save it to table
    table = get_most_recent(constellation, f="../database/database.ini")

    # Split names of neighbors column
    table["NEIGHBORS"] = [e.split(";") for e in table["NEIGHBORS"]]

    # Create the coordinates object
    coords = SkyCoord(
        ra=table["RA"],
        dec=table["DEC"],
        unit=(u.hourangle, u.deg),
        frame="icrs",
        obstime="j2000",
        pm_ra_cosdec=table["PMRA"] * u.mas / u.yr,
        pm_dec=table["PMDEC"] * u.mas / u.yr,
        distance=Distance(parallax=table["PLX_VALUE"] * u.mas),
    )

    # Apply movement
    cyear = table["TIME"][0].year
    coords = coords.apply_space_motion(dt=(cyear + dmill * 1000) * u.yr)

    # If viewtype is set to "Real", compute the real coordinates
    if viewtype == "Real":
        coords = coords.apply_space_motion(dt=coords.distance.to(u.m) / c)

    # Update values in table
    table["RA"] = coords.ra
    table["DEC"] = coords.dec

    # Plot constellation
    output_figure = plot_constellation(table)

    return output_figure


def plot_constellation(table):
    """Given an astropy table with constellation data, returns a matplotlib
    figure of the constellation."""

    # Initiate figure
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.invert_xaxis()
    ax.grid(True)

    # Plot individual stars
    ax.scatter(table["RA"], table["DEC"], color="#191919", s=20)

    # Draw lines between stars
    seen_before = []
    for row in table:
        seen_before.append(row["TYPED_ID"])
        x1 = row["RA"]
        y1 = row["DEC"]
        for neighbor in row["NEIGHBORS"]:
            if neighbor not in seen_before:
                x2 = table[table["TYPED_ID"] == neighbor]["RA"]
                y2 = table[table["TYPED_ID"] == neighbor]["DEC"]
                ax.plot([x1, x2], [y1, y2], color="#191919", linewidth=1)

    return fig

processing("Aquarius", 0, "Real")
plt.show()
