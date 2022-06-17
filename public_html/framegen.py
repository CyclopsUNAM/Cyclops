#!/usr/bin/env python3

import subprocess
import os
import json
from configparser import ConfigParser

import gradio as gr
from PIL import Image


def config(filename, section):
    """Reads configuration files."""

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


def main(constellation, dmill, viewtype):
    """Main function executed by user."""

    # Read configuration file
    conf = config("../config.ini", "framegen")
    user, host, route = conf["user"], conf["host"], conf["route"]

    # Run processing module
    command = (
        f'ssh {user}@{host} "cd {route}; '
        f'./processing.py {constellation} {int(dmill)} {viewtype}"'
    )
    output = subprocess.check_output(command, shell=True).decode().strip()

    # Store image in variable
    full_imgname = output[output.find(":") + 2:]
    imgname = full_imgname.split("/")[-1]
    os.system(f"scp {user}@{host}:{full_imgname} .")
    img = Image.open(imgname)
    os.system(f"rm {imgname}")

    return img

const = []
with open("../spider/constellations.json", "r") as f:
    const = list(json.load(f).keys())

frame = gr.Interface(
    fn=main,
    inputs=[
        gr.Dropdown(const, label="Constellation"),
        gr.Slider(-8, 145, step=1, value=0, label="Millennium Difference"),
        gr.Radio(["Real", "Apparent"], label="View Type")
    ],
    outputs=["image"],
)
frame.launch(server_port=7923)
