import numpy as np
import re
import pathlib
import shutil
from datetime import datetime
from time import sleep
import math
import platform


np.set_printoptions(threshold=np.inf, linewidth=100)


def compile_regex(panel):
    regexString = f"Buffer{panel}\([1-9].*?\).XYZ.*"
    return re.compile(regexString)


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


def get_coord(regex):
    coordinates = regex[regex.rfind("(") + 1 : -1]
    coordinates = coordinates.split(",")
    float_coords = [float(ele) for ele in coordinates]
    return float_coords


def print_coords(cubbies):
    points_list = []
    for loc in cubbies:
        loc1 = get_coord(loc)
        points_list.append(loc1)
    a6D = np.array(points_list)
    print(a6D)


def cubbies_to_numpy(cubbies):
    points_list = []
    for loc in cubbies:
        points_list.append(get_coord(loc))
    return np.array(points_list)


def offset_numpy_arr(np_arr, rows):
    # Get x,y, and z of top left and bottom left and bottom right and make offsets
    x_offset_values = np.linspace(0, (np_arr[0][0] - np_arr[-5][0]), rows)
    y_offset_values = np.linspace(0, (np_arr[0][1] - np_arr[-5][1]), rows)
    # ^ the above only uses cubby 96 to determine an offset. The below uses 96 and 100 to determine offsets
    x96_x100_offset_list = np.linspace(np_arr[-5][0], np_arr[-1][0], 5)
    y96_y100_offset_list = np.linspace(np_arr[-5][1], np_arr[-1][1], 5)
    z96_z100_offset_list = np.linspace(np_arr[-5][2], np_arr[-1][2], 5)
    for i in range(5):
        x_offset_list = np.linspace(np_arr[i][0], x96_x100_offset_list[i], rows)
        y_offset_list = np.linspace(np_arr[i][1], y96_y100_offset_list[i], rows)
        z_offset_list = np.linspace(np_arr[i][2], z96_z100_offset_list[i], rows)
        for j in range(rows):
            # updates columns at a time
            np_arr[(j * 5) + i] = np_arr[i]  # Copy whole point and update below
            # np_arr[(j * 5) + i][0] = x_offset_list[j]    # X
            # np_arr[(j * 5) + i][1] = y_offset_list[j]    # Y
            np_arr[(j * 5) + i][0] -= x_offset_values[j]  # X
            np_arr[(j * 5) + i][1] -= y_offset_values[j]  # Y
            np_arr[(j * 5) + i][2] = z_offset_list[j]  # Z
    return np_arr


def make_updated_strings(panel, new_array):
    updated_strings = []
    for i in range(len(new_array)):
        x = np.around(new_array[i][0], 3)
        y = np.around(new_array[i][1], 3)
        z = np.around(new_array[i][2], 3)
        yaw = np.around(new_array[i][3], 3)
        new_str = f"Buffer{panel}({i+1}).XYZ({x},{y},{z},{yaw},90,-180)"
        updated_strings.append(new_str)
        # print(new_str)
    return updated_strings


def make_updated_gpo_file(gpo_content, points, new_array, projDir):
    for i in range(len(points)):
        gpo_content = gpo_content.replace(points[i], new_array[i])
    new_file = open(projDir / "RandomAccessBufferGPO.gpo", "w")
    new_file.write(gpo_content)
    print("wrote")
    new_file.close()


def main():
    # Setup
    robot_name = "1"
    now = datetime.now().strftime("%m%d%y_%H%M%S")

    projDir = pathlib.Path(f"robot{robot}/robot{robot}_Robot_Program_PO")
    backupDir = pathlib.Path(f"robot{robot}/robot{robot}_Robot_Program_PO{now}")

    # Backup Directory with date and time appended. Just rename and load to use old backup.
    # shutil.copytree(projDir, backupDir)

    panels = ["A1", "A2", "B1", "B2", "C1", "C2", "D1", "D2", "E1", "E2", "F1", "F2"]
    print("Enter the panel to calibrate and press enter.")
    print(f"The following are the options: {panels}")
    panel = input("Panel: ").upper()
    if panel not in panels:
        print(f"Entered panel, {panel}, is not in {panels}. Goodbye.")
        exit()
    gpoBuffersFile = open(projDir / "RandomAccessBufferGPO.gpo", "r")
    gpoBufferContent = gpoBuffersFile.read()
    # print(gpoBufferContent)
    gpoBuffersFile.close()
    bufferRegex = compile_regex(panel)
    points = bufferRegex.findall(gpoBufferContent)
    raw_numpy_arr = cubbies_to_numpy(points)
    us = make_updated_strings(panel, offset_numpy_arr(raw_numpy_arr, 10))

    print(panel)
    print("#".rjust(140, "#"))

    for i in range(0, len(points)):
        points_changed = 0
        if linear_distance(get_info(points[i]), get_info(us[i])) > 1:
            print("old", points[i]), print("new", us[i])
            points_changed += 1
    if points_changed == 0:
        print("No points were updated")

    # make_updated_gpo_file(gpoBufferContent, points, us, projDir)
    print()


if __name__ == "__main__":
    main()
