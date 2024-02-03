import numpy as np
import re
from pathlib import Path
import csv
import math
from time import sleep


np.set_printoptions(threshold=np.inf, linewidth=100)
rab_name = "60"


def compile_regex(panel):
    regexString = f"Buffer{panel}\([1-9].*?\).XYZ.*"
    return re.compile(regexString)


def get_panel(regex):
    return regex[6]


def get_cubby(regex):
    return regex[regex.find("(") + 1 : regex.find(")")]


def get_panel_and_cubby(mo):
    panelAndCubby = []
    for i in range(0, len(mo)):
        panelAndCubby.append(get_panel(mo[i]) + get_cubby(mo[i]))
    return panelAndCubby


def get_info(raw_location):
    """
    Pass in a string like the below and return a dict of coordinates
    with x, y, z, yaw, pitch, roll

    BufferF(100).XYZ(-619.669,-314.6492,145.5031,42.01459,90,180)
    ConveyorA.XYZ(429.7065,355.0604,59.06869,84.88406,90,180)
    """
    name = raw_location[: raw_location.find(".")]
    coordinate_names = ["x", "y", "z", "yaw", "pitch", "roll"]
    coordinates = raw_location[raw_location.rfind("(") + 1 : -1]
    coordinates = coordinates.split(",")
    float_coords = [float(ele) for ele in coordinates]
    coordinate_dict = dict(zip(coordinate_names, float_coords))
    coordinate_dict["location"] = name
    return coordinate_dict


def linear_distance(loc1: dict, loc2: dict) -> float:
    return math.sqrt(
        (loc2["x"] - loc1["x"]) ** 2
        + (loc2["y"] - loc1["y"]) ** 2
        + (loc2["z"] - loc1["z"]) ** 2
    )


def main():
    gpoBuffersFile = open(
        Path(__file__).resolve().parents[1]
        / "rab60"
        / "RAB60_Robot_Program"
        / "RandomAccessBufferGPO.gpo",
        "r",
    )
    # backupFile = open(Path.cwd() / "RandomAccessBufferGPO_60backup.gpo", "w")
    # backupFile.write(gpoBufferContent)
    gpoBufferContent = gpoBuffersFile.read()
    gpoBuffersFile.close()
    panels = ["A", "B", "C", "D", "E", "F"]
    regexString = "Buffer[A-F]\([1-9].*?\).XYZ.*"
    conveyorString = "Conveyor[A-F].XYZ.*"
    reg = re.compile(regexString)

    # BufferA(1).XYZ(-619.2606,301.9012,1407.145,-41.56812,90,180)
    # Regex returns all strings matching something similar to the above.
    points = reg.findall(gpoBufferContent)
    conveyor = re.compile(conveyorString).findall(gpoBufferContent)
    points.extend(conveyor)
    OutPackoff = get_info(points[601])
    OutException = get_info(points[602])
    OutReturn = get_info(points[603])

    with open("pointscsv.csv", "w", newline="\n") as csvfile:
        fieldnames = [
            "location",
            "x",
            "y",
            "z",
            "yaw",
            "pitch",
            "roll",
            "Distance To Packoff",
            "Distance To SPH",
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for line in points:
            # Create a function
            # f.write(str(line))
            # f.write("\n")
            str_to_dict = get_info(line)
            str_to_dict["Distance To Packoff"] = linear_distance(
                str_to_dict, OutPackoff
            )
            str_to_dict["Distance To SPH"] = linear_distance(str_to_dict, OutException)
            writer.writerow(str_to_dict)


if __name__ == "__main__":
    main()
