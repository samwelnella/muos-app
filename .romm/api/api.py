import base64
import json
import math
import os
from collections import namedtuple
from os import makedirs
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

from dotenv import load_dotenv

# Load .env file from one folder above
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))


Rom = namedtuple(
    "Rom",
    ["id", "name", "file_name", "platform_slug", "file_extension", "file_size", "file_size_bytes"],
)
Collection = namedtuple("Collection", ["id", "name", "rom_count"])
Platform = namedtuple("Platform", ["id", "display_name", "rom_count"])


class API:

    def __init__(self):
        self.host = os.getenv("HOST", "")
        self.__platforms_endpoint = "/api/platforms"
        self.__collections_endpoint = "/api/collections"
        self.__roms_endpoint = "/api/roms"
        self.username = os.getenv("USERNAME", "")
        self.__password = os.getenv("PASSWORD", "")
        self.__credentials = f"{self.username}:{self.__password}"
        self.__auth_token = base64.b64encode(self.__credentials.encode("utf-8")).decode(
            "utf-8"
        )
        self.__headers = {"Authorization": f"Basic {self.__auth_token}"}
        self.__exclude_platforms = set(os.getenv("EXCLUDE_PLATFORMS") or [])
        self.__include_collections = set(os.getenv("INCLUDE_COLLECTIONS") or [])
        self.__exclude_collections = set(os.getenv("EXCLUDE_COLLECTIONS") or [])
        self.__collections = []
        self.__platforms = []
        self.__roms = []

    @staticmethod
    def __human_readable_size(size_bytes):
        if size_bytes == 0:
            return "0B"
        size_name = ("B", "KB", "MB", "GB")
        i = int(math.floor(math.log(size_bytes, 1024)))
        p = math.pow(1024, i)
        s = round(size_bytes / p, 2)
        return (s, size_name[i])

    def get_platforms(self):
        try:
            request = Request(
                f"{self.host}{self.__platforms_endpoint}", headers=self.__headers
            )
        except ValueError:
            return ([], False, False)
        try:
            if request.type not in ("http", "https"):
                return ([], False, False)
            response = urlopen(request, timeout=60) # trunk-ignore(bandit/B310)
        except HTTPError as e:
            if e.code == 403:
                return ([], True, False)
            else:
                raise
        except URLError:
            return ([], False, False)
        platforms = json.loads(response.read().decode("utf-8"))
        self.__platforms = []
        for platform in platforms:
            if platform["rom_count"] > 0:
                if (
                    platform["slug"] not in MUOS_SUPPORTED_PLATFORMS
                    or platform["slug"] in self.__exclude_platforms
                ):
                    continue
                self.__platforms.append(
                    Platform(
                        id=platform["id"],
                        display_name=platform["display_name"],
                        rom_count=platform["rom_count"],
                    )
                )
        return (self.__platforms, True, True)

    def get_collections(self):
        try:
            request = Request(
                f"{self.host}{self.__collections_endpoint}", headers=self.__headers
            )
        except ValueError:
            return ([], False, False)
        try:
            if request.type not in ("http", "https"):
                return ([], False, False)
            response = urlopen(request, timeout=60) # trunk-ignore(bandit/B310)
        except HTTPError as e:
            if e.code == 403:
                return ([], True, False)
            else:
                raise
        except URLError:
            return ([], False, False)
        collections = json.loads(response.read().decode("utf-8"))
        self.__collections = []
        for collection in collections:
            if collection["rom_count"] > 0:
                if self.__include_collections:
                    if collection["name"] not in self.__include_collections:
                        continue
                elif self.__exclude_collections:
                    if collection["name"] in self.__exclude_collections:
                        continue
                self.__collections.append(
                    Collection(
                        id=collection["id"],
                        name=collection["name"],
                        rom_count=collection["rom_count"],
                    )
                )
        return (self.__collections, True, True)

    def get_roms(self, view, id):
        try:
            request = Request(
                f"{self.host}{self.__roms_endpoint}?{view}_id={id}&order_by=name&order_dir=asc",
                headers=self.__headers,
            )
        except ValueError:
            return ([], False, False)
        try:
            if request.type not in ("http", "https"):
                return ([], False, False)
            response = urlopen(request, timeout=1800) # trunk-ignore(bandit/B310)
        except HTTPError as e:
            if e.code == 403:
                return ([], True, False)
            else:
                raise
        except URLError:
            return ([], False, False)
        roms = json.loads(response.read().decode("utf-8"))
        self.__roms = [
            Rom(
                id=rom["id"],
                name=rom["name"],
                file_name=rom["file_name"],
                platform_slug=rom["platform_slug"],
                file_extension=rom["file_extension"],
                file_size=self.__human_readable_size(rom["file_size_bytes"]),
                file_size_bytes=rom["file_size_bytes"],
            )
            for rom in roms if rom["platform_slug"] in MUOS_SUPPORTED_PLATFORMS
        ]
        return self.__roms, True, True

    def reset_roms_list(self):
        self.__roms = []

    def download_rom(self, rom, dest_path):
        url = f"{self.host}{self.__roms_endpoint}/{rom.id}/content/{quote(rom.file_name)}"
        makedirs(os.path.dirname(dest_path), exist_ok=True)

        # Create a request with headers
        try:
            request = Request(url, headers=self.__headers)
        except ValueError:
            return (False, False)

        # Download the file to a temporary path
        try:
            if request.type not in ("http", "https"):
                return ([], False, False)
            with urlopen(request) as response, open(dest_path, "wb") as out_file: # trunk-ignore(bandit/B310)
                total_bytes = 0
                chunk_size = 1024
                while True:
                    chunk = response.read(chunk_size)
                    if not chunk:
                        break
                    out_file.write(chunk)
                    total_bytes += len(chunk)
                    yield (total_bytes, True, True)
        except HTTPError as e:
            if e.code == 403:
                return (0, True, False)
            else:
                raise
        except URLError:
            return (0, False, False)

        return (0, True, True)


MUOS_SUPPORTED_PLATFORMS = frozenset(
    (
        "acpc",
        "arcade",
        "arduboy",
        "atari2600",
        "atari5200",
        "atari7800",
        "jaguar",
        "lynx",
        "atari-st",
        "wonderswan",
        "wonderswan-color",
        "cave-story",
        "chailove",
        "chip-8",
        "colecovision",
        "amiga",
        "c128",
        "c64",
        "cpet",
        "vic-20",
        "dos",
        "doom",
        "fairchild-channel-f",
        "vectrex",
        "galaksija",
        "g-and-w",
        "j2me",
        "lowres",
        "lua",
        "odyssey--1",
        "intellivision",
        "mega-duck-slash-cougar-boy",
        "msx",
        "turbografx-16-slash-pc-engine-cd",
        "supergrafx",
        "turbografx16--1",
        "pc-8000",
        "pc-fx",
        "pc-9800-series",
        "nds",
        "fds",
        "gba",
        "gbc",
        "gb",
        "n64",
        "nes",
        "famicom",
        "snes",
        "sfam",
        "pokemon-mini",
        "virtualboy",
        "openbor",
        "pico-8",
        "philips-cd-i",
        "quake",
        "rpg-maker",
        "neogeoaes",
        "neogeomvs",
        "neo-geo-cd",
        "neo-geo-pocket",
        "neo-geo-pocket-color",
        "scummvm",
        "sega-32x",
        "dc",
        "gamegear",
        "sega-master-system",
        "genesis-slash-megadrive",
        "sega-pico",
        "segacd",
        "sg1000",
        "saturn",
        "x1",
        "sharp-x68000",
        "sinclair-zx81",
        "zxs",
        "ps",
        "psp",
        "tic-80",
        "ti-83",
        "3do",
        "uzebox",
        "vemulator",
        "wasm-4",
        "watara-slash-quickshot-supervision",
        "wolfenstein-3d",
    )
)
