from telnetlib import Telnet

robot_ip = "192.168.1.1"
panels = ["A", "B", "C", "D", "E", "F"]
init = "RABInit"
store = "RABStore A "
retrieve = "RABRetrieve "


def store_maker(panel, cubby):
    cmd = store + panel + " " + str(cubby)
    print(cmd)
    return cmd.encode("ascii") + b"\r\n"


def retrieve_maker(panel, cubby):
    cmd = retrieve + panel + " " + str(cubby) + " B"
    print(cmd)
    return cmd.encode("ascii") + b"\r\n"


with Telnet(robot_ip, 10100) as tn:
    try:
        tn.write(init.encode("ascii") + b"\r\n")
        res = tn.read_some().decode("ascii").strip("\r\n")
        if res == "0":
            for panel in panels:
                for cubby in range(1, 101):
                    tn.write(store_maker(panel, cubby))
                    res = tn.read_some().decode("ascii").strip("\r\n")
                    print(res)
                    tn.write(retrieve_maker(panel, cubby))
                    res = tn.read_some().decode("ascii").strip("\r\n")
                    print(res)

    except Exception as e:
        print(e)
    finally:
        tn.close()
