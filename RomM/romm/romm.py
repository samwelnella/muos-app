import os
import json
from urllib.request import urlopen, Request
from urllib.parse import quote
from filesystem.filesystem import Filesystem
from os import makedirs
import base64
from dotenv import load_dotenv
import math

# Load .env file from one folder above
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))
fs = Filesystem()

class RomM:

    def __init__(self):
        self.host = os.getenv("HOST", None)
        self.__platforms_endpoint = "/api/platforms"
        self.__roms_endpoint = "/api/roms"
        self.username = os.getenv("USERNAME", None)
        self.__password = os.getenv("PASSWORD", None)
        self.__credentials = f"{self.username}:{self.__password}"
        self.__auth_token = base64.b64encode(self.__credentials.encode('utf-8')).decode('utf-8')
        self.__headers = { 'Authorization': f'Basic {self.__auth_token}' }
        self.__console_list = []
        self.__roms_list = []

    def __human_readable_size(size_bytes):
        if size_bytes == 0:
            return "0B"
        size_name = ("B", "KB", "MB", "GB")
        i = int(math.floor(math.log(size_bytes, 1024)))
        p = math.pow(1024, i)
        s = round(size_bytes / p, 2)
        return f"{s} {size_name[i]}"
    
    def get_platforms(self):
        request = Request(f"{self.host}{self.__platforms_endpoint}", headers=self.__headers)
        response = urlopen(request)
        platforms = json.loads(
            response.read().decode('utf-8')
        )
        self.__console_list = []
        for platform in platforms:
            if platform['rom_count'] > 0:
                self.__console_list.append((platform['display_name'], platform['id'], platform['rom_count']))
        return self.__console_list

    def get_roms(self, platform_id, refresh=False):
        if len(self.__roms_list) > 0 and not refresh:
            return self.__roms_list
        try:
            request = Request(f"{self.host}{self.__roms_endpoint}?platform_id={platform_id}&order_by=name&order_dir=asc", headers=self.__headers)
            response = urlopen(request)
            roms = json.loads(
                response.read().decode('utf-8')
            )
            self.__roms_list = [(rom['name'], rom['file_name'], rom['platform_slug'], rom['file_extension'], rom['id'], rom['file_size_bytes']) for rom in roms]
            return self.__roms_list
        except:
            return []
    
    def reset_roms_list(self):
        self.__roms_list = []
    
    def download_rom(self, rom):
        url = f"{self.host}{self.__roms_endpoint}/{rom[4]}/content/{quote(rom[1])}"
        dest_path = os.path.join(fs.get_sd_storage_platform_path(rom[2]), rom[1])
        makedirs(os.path.dirname(dest_path), exist_ok=True)

        # Create a request with headers
        request = Request(url, headers=self.__headers)
        
        # Download the file to a temporary path
        with urlopen(request) as response, open(dest_path, 'wb') as out_file:
            out_file.write(response.read())
        
        return dest_path
