# Cyclops Spider
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

This module provides functions to fetch star data from the SIMBAD database.
"""

import json
import psycopg2
from urllib.request import urlopen
from configparser import ConfigParser
from sys import argv

def star_info(name):
    """Retrieves SIMBAD information on a given star."""

    # Replace ' ' with '+'
    name = name.replace(' ', '+')

    # URL format
    url = ('http://simbad.cds.unistra.fr/simbad/sim-script?submit'
          '=submit+script&script=query+id+' + name)

    # Read contents and store data in dictionary
    with urlopen(url) as f:
        lines = f.readlines()
        star_data = {'typed ident': False, 'coord': False,
                     'proper motion': False, 'parallax': False}

        for line in lines:
            line = line.decode()
            for key in star_data.keys():
                if line.startswith(key) and star_data[key] == False:
                    star_data[key] = line[line.find(': ')+2:].strip()
                    break

    return star_data

def costellation_info(name_constellation):
    """Fetches SIMBAD information on every star of a given constellation and
    returns a dictionary from the data."""

    # Read json file and transform to dictionary
    with open('constellations.json', 'r') as f:
        consts = json.load(f)
        stars_in_c = {}
        stars_in_c["constellation"] = name_constellation

        for i in range(0,len(consts)):
            name = consts[i].values()
            if name_constellation in name:
                star_name = consts[i]["stars"]
                for j in star_name:
                    key = j["name"]
                    value = star_info(key)
                    stars_in_c[key] = value

    return stars_in_c

def config(filename='database.ini', section='postgresql'):
    """Reads configuration file."""

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
        raise Exception('Section {0} not found in the {1} file'.format(section,
                        filename))

    return db

def send_to_database(data, f='database.ini'):
    """Connect to the PostgreSQL database server, and send collected star info
    to database."""

    conn = None
    try:
        # Read connection parameters
        params = config(filename=f)

        # Connect to the PostgreSQL server
        print('Connecting to the PostgreSQL database...')
        conn = psycopg2.connect(**params)

        # Create a cursor
        cur = conn.cursor()

        # Send star info to database
        # INSERT INTO stars values (name, constellation, ra, dec, pm_ra, 
        #                           pm_dec, parallax, time)

        # Display the PostgreSQL database server version
        db_version = cur.fetchone()
        print(db_version)

        # Close the communication with the PostgreSQL
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
            print(error)
    finally:
        if conn is not None:
            conn.close()
            print('Database connection closed.')

def main(constellation, database_dir):
    """Driver code."""

    # Fetch constellation info
    const_data = constellation_info(constellation)

    # Send to database
    send_to_database(const_data, f=database_dir)

if __name__ == '__main__':
    main(argv[1], '../database/database.ini')
