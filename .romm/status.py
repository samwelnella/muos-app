import threading
from glyps import glyphs

class View:
    PLATFORMS = "platform"
    COLLECTIONS = "collection"
    ROMS = "roms"


class StartMenuOptions:
    SD_SWITCH = (f"{glyphs.microsd} Switch SD", 0)
    EXIT = (f"{glyphs.exit} Exit", 1)


class Status():
    _instance = None

    def __new__(cls):
        if not cls._instance:
            cls._instance = super(Status, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        self.valid_host = True
        self.valid_credentials = True

        self.me = None
        self.profile_pic_path = ""

        self.current_view = View.PLATFORMS
        self.selected_platform = None
        self.selected_collection = None

        self.show_start_menu = False
        self.show_contextual_menu = False

        self.platforms = []
        self.collections = []
        self.roms = []

        self.platforms_ready = threading.Event()
        self.collections_ready = threading.Event()
        self.roms_ready = threading.Event()
        self.download_rom_ready = threading.Event()
        self.me_ready = threading.Event()

        self.multi_selected_roms = []
        self.download_queue = []
        self.downloading_rom = None
        self.downloading_rom_position = 0
        self.total_downloaded_bytes = 0
        self.downloaded_percent = 0


    def reset_roms_list(self):
        self.roms = []