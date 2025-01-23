import struct

code = 0
codeName = ""
value = 0

mapping = {
    304: "A",
    305: "B",
    306: "Y",
    307: "X",
    308: "L1",
    309: "R1",
    314: "L2",
    315: "R2",
    17: "DY",
    16: "DX",
    310: "SELECT",
    311: "START",
    312: "MENUF",
    114: "V+",
    115: "V-",
}


def check():
    global type, code, codeName, codeDown, value, valueDown
    with open("/dev/input/event1", "rb") as f:
        while True:
            event = f.read(24)

            if event:
                (tv_sec, tv_usec, type, kcode, kvalue) = struct.unpack("llHHI", event)
                if kvalue != 0:
                    if kvalue != 1:
                        kvalue = -1
                    code = kcode
                    codeName = mapping.get(code, str(code))
                    value = kvalue
                    return


def key(keyCodeName, keyValue=99):
    global code, codeName, value
    if codeName == keyCodeName:
        if keyValue != 99:
            return value == keyValue
        return True


def handle_navigation(selected_position, max_items, total_items):
    global value

    if key("DY"):
        if value == 1:
            if selected_position == total_items - 1:
                selected_position = 0
            elif selected_position < total_items - 1:
                selected_position += 1
        elif value == -1:
            if selected_position == 0:
                selected_position = total_items - 1
            elif selected_position > 0:
                selected_position -= 1
    elif key("DX"):
        if value == 1:
            if selected_position < total_items - 1:
                if selected_position + max_items <= total_items - 1:
                    selected_position = selected_position + max_items
                else:
                    selected_position = total_items - 1
        elif value == -1:
            if selected_position > 0:
                if selected_position - max_items >= 0:
                    selected_position = selected_position - max_items
                else:
                    selected_position = 0
    return selected_position


def handle_large_navigation(selected_position, max_items, total_items):
    if key("L1"):
        if selected_position > 0:
            if selected_position - max_items >= 0:
                selected_position = selected_position - max_items
            else:
                selected_position = 0
    elif key("R1"):
        if selected_position < total_items - 1:
            if selected_position + max_items <= total_items - 1:
                selected_position = selected_position + max_items
            else:
                selected_position = total_items - 1
    elif key("L2"):
        if selected_position > 0:
            if selected_position - 100 >= 0:
                selected_position = selected_position - 100
            else:
                selected_position = 0
    elif key("R2"):
        if selected_position < total_items - 1:
            if selected_position + 100 <= total_items - 1:
                selected_position = selected_position + 100
            else:
                selected_position = total_items - 1
    return selected_position


def reset_input():
    global codeName, value
    codeName = ""
    value = 0
