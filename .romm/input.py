from struct import unpack
from threading import Lock

class Input:
    _instance: "Input" | None = None
    key_code: int
    key_name: str
    key_value: int
    key_mapping: dict[int, str]
    input_lock: Lock

    def __new__(cls):
        if not cls._instance:
            cls._instance = super(Input, cls).__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        self.key_code = 0
        self.key_name= ""
        self.key_value = 0
        self.key_mapping = {
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
        self.input_lock = Lock()

    def check(self) -> None:
        with open("/dev/input/event1", "rb") as f:
            while True:
                event = f.read(24)
                if event:
                    (_, _, _, kcode, kvalue) = unpack("llHHI", event)
                    if kvalue != 0:
                        if kvalue != 1:
                            kvalue = -1
                        with self.input_lock:
                            self.key_code = kcode
                            self.key_name = self.key_mapping.get(
                                self.key_code, str(self.key_code)
                            )
                            self.key_value = kvalue

    def key(self, key_name: str, key_value: int = 99) -> bool:
        if self.key_name == key_name:
            if key_value != 99:
                return self.key_value == key_value
            print(f"BUTTON: {self.key_name} - {self.key_value}")
            return True
        return False

    def handle_navigation(self, selected_position: int, items_per_page :int, total_items: int) -> int:
        if self.key("DY"):
            if self.key_value == 1:
                if selected_position == total_items - 1:
                    selected_position = 0
                elif selected_position < total_items - 1:
                    selected_position += 1
            elif self.key_value == -1:
                if selected_position == 0:
                    selected_position = total_items - 1
                elif selected_position > 0:
                    selected_position -= 1
            self.reset_input()
        elif self.key("DX"):
            if self.key_value == 1:
                if selected_position < total_items - 1:
                    if selected_position + items_per_page <= total_items - 1:
                        selected_position = selected_position + items_per_page
                    else:
                        selected_position = total_items - 1
            elif self.key_value == -1:
                if selected_position > 0:
                    if selected_position - items_per_page >= 0:
                        selected_position = selected_position - items_per_page
                    else:
                        selected_position = 0
            self.reset_input()
        elif self.key("L1"):
            if selected_position > 0:
                if selected_position - items_per_page >= 0:
                    selected_position = selected_position - items_per_page
                else:
                    selected_position = 0
            self.reset_input()
        elif self.key("R1"):
            if selected_position < total_items - 1:
                if selected_position + items_per_page <= total_items - 1:
                    selected_position = selected_position + items_per_page
                else:
                    selected_position = total_items - 1
            self.reset_input()
        elif self.key("L2"):
            if selected_position > 0:
                if selected_position - 100 >= 0:
                    selected_position = selected_position - 100
                else:
                    selected_position = 0
            self.reset_input()
        elif self.key("R2"):
            if selected_position < total_items - 1:
                if selected_position + 100 <= total_items - 1:
                    selected_position = selected_position + 100
                else:
                    selected_position = total_items - 1
            self.reset_input()
        return selected_position

    def reset_input(self) -> None:
        with self.input_lock:
            self.key_name = ""
            self.key_value = 0
            self.key_code = 0
